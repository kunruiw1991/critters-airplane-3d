#!/usr/bin/env python3
"""Chrome DevTools Protocol (CDP) WebGL 2.0 Driver for Critters Airplane 3D.

Provides zero-install headless Chromium control over Python 3.13 + websockets:
- Ephemeral local HTTP server (`LocalHttpServer`) serving `index.html`, `docs/index.html`, and `dist/index.html`
- Headless Google Chrome 153 with SwiftShader WebGL 2.0 flags:
  `--headless=new --no-sandbox --use-gl=angle --use-angle=swiftshader --enable-webgl --ignore-gpu-blocklist --enable-unsafe-swiftshader --autoplay-policy=no-user-gesture-required --user-data-dir=/dev/shm/e2e_chrome_<pid>`
- Automatic cleanup of `/dev/shm/e2e_chrome_*` directories on session close and `atexit`
- Real-time capture of `Runtime.consoleAPICalled`, `Runtime.exceptionThrown`, and `Log.entryAdded`
- Binary PNG / IHDR header verification (`verify_png_data_url`)
- Declarative test registration (`@register_test`) and structured reporting
"""

from __future__ import annotations

import asyncio
import atexit
import base64
from dataclasses import dataclass
import functools
import glob
import http.server
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import threading
import time
from typing import Any, Callable, Coroutine, Sequence
import urllib.request
import uuid
import websockets


_ACTIVE_SHM_DIRS: set[str] = set()


def cleanup_all_shm_dirs() -> None:
  """Remove any temporary Chrome user-data directories created in /dev/shm."""
  pid_pattern = f"/dev/shm/e2e_chrome_{os.getpid()}*"
  for path in list(_ACTIVE_SHM_DIRS) + glob.glob(pid_pattern):
    try:
      if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
    except Exception:  # pylint: disable=broad-except
      pass
    _ACTIVE_SHM_DIRS.discard(path)


atexit.register(cleanup_all_shm_dirs)


def find_free_port() -> int:
  """Return an available localhost TCP port."""
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    return int(sock.getsockname()[1])


class _SilentDirectoryHandler(http.server.SimpleHTTPRequestHandler):
  """HTTP request handler serving a specified root directory silently."""

  def __init__(self, *args: Any, directory: str | None = None, **kwargs: Any):
    super().__init__(*args, directory=directory, **kwargs)

  def end_headers(self) -> None:
    self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
    super().end_headers()

  def log_message(self, format: str, *args: Any) -> None:  # pylint: disable=redefined-builtin
    pass


class LocalHttpServer:
  """Background HTTP server serving static application files on 127.0.0.1."""

  def __init__(self, root_dir: str | Path, port: int | None = None):
    self.root_dir = str(Path(root_dir).resolve())
    self.port = port or find_free_port()
    self._server: http.server.ThreadingHTTPServer | None = None
    self._thread: threading.Thread | None = None

  @property
  def base_url(self) -> str:
    return f"http://127.0.0.1:{self.port}"

  def start(self) -> str:
    handler = functools.partial(_SilentDirectoryHandler, directory=self.root_dir)
    self._server = http.server.ThreadingHTTPServer(("127.0.0.1", self.port), handler)
    self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
    self._thread.start()
    return self.base_url

  def stop(self) -> None:
    if self._server is not None:
      self._server.shutdown()
      self._server.server_close()
      self._server = None
    if self._thread is not None:
      self._thread.join(timeout=2.0)
      self._thread = None

  def __enter__(self) -> "LocalHttpServer":
    self.start()
    return self

  def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
    self.stop()


def verify_png_data_url(data_url: str, min_length: int = 5000) -> dict[str, Any]:
  """Decode a data:image/png;base64,... URL and validate its PNG signature & IHDR dimensions."""
  prefix = "data:image/png;base64,"
  if not isinstance(data_url, str) or not data_url.startswith(prefix):
    raise AssertionError(
        f"Expected data URL starting with '{prefix}', got: {str(data_url)[:64]!r}"
    )
  if len(data_url) <= min_length:
    raise AssertionError(
        f"Expected data URL length > {min_length}, got {len(data_url)}"
    )
  b64_payload = data_url[len(prefix) :]
  raw_bytes = base64.b64decode(b64_payload)
  png_magic = b"\x89PNG\r\n\x1a\n"
  if len(raw_bytes) < 33 or raw_bytes[:8] != png_magic:
    raise AssertionError(
        f"Invalid PNG signature: expected {png_magic!r}, got {raw_bytes[:8]!r}"
    )
  chunk_len, chunk_type = struct.unpack(">I4s", raw_bytes[8:16])
  if chunk_type != b"IHDR" or chunk_len != 13:
    raise AssertionError(f"Expected 13-byte IHDR chunk, got {chunk_type!r} ({chunk_len})")
  width, height, bit_depth, color_type = struct.unpack(">IIBB", raw_bytes[16:26])
  if width <= 0 or height <= 0:
    raise AssertionError(f"Invalid PNG dimensions: {width}x{height}")
  return {
      "data_url_length": len(data_url),
      "byte_length": len(raw_bytes),
      "width": width,
      "height": height,
      "bit_depth": bit_depth,
      "color_type": color_type,
  }


class ChromeCdpSession:
  """Async CDP driver managing headless Google Chrome 153 with SwiftShader WebGL 2.0."""

  def __init__(
      self,
      chrome_binary: str = "/usr/bin/google-chrome",
      window_size: tuple[int, int] = (1440, 900),
      extra_flags: Sequence[str] = (),
  ):
    self.chrome_binary = chrome_binary
    self.window_size = window_size
    self.extra_flags = list(extra_flags)
    self.cdp_port = find_free_port()
    self.user_data_dir = f"/dev/shm/e2e_chrome_{os.getpid()}_{uuid.uuid4().hex[:8]}"
    _ACTIVE_SHM_DIRS.add(self.user_data_dir)
    self._proc: subprocess.Popen[bytes] | None = None
    self._ws: Any = None
    self._recv_task: asyncio.Task[None] | None = None
    self._msg_id = 0
    self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
    self.console_errors: list[dict[str, Any]] = []
    self.page_exceptions: list[dict[str, Any]] = []
    self.console_logs: list[dict[str, Any]] = []
    self._load_event = asyncio.Event()

  async def start(self) -> "ChromeCdpSession":
    os.makedirs(self.user_data_dir, exist_ok=True)
    cache_dir = os.path.join(self.user_data_dir, "cache")
    config_dir = os.path.join(self.user_data_dir, "config")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)

    # Launch Chrome 153 with SwiftShader WebGL 2.0 enabled (NO --disable-gpu)
    cmd = [
        self.chrome_binary,
        "--headless=new",
        "--no-sandbox",
        "--use-gl=angle",
        "--use-angle=swiftshader",
        "--enable-webgl",
        "--ignore-gpu-blocklist",
        "--enable-unsafe-swiftshader",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        "--autoplay-policy=no-user-gesture-required",
        f"--user-data-dir={self.user_data_dir}",
        f"--disk-cache-dir={cache_dir}",
        f"--remote-debugging-port={self.cdp_port}",
        f"--window-size={self.window_size[0]},{self.window_size[1]}",
        *self.extra_flags,
        "about:blank",
    ]
    chrome_env = {
        **os.environ,
        "HOME": self.user_data_dir,
        "XDG_CACHE_HOME": cache_dir,
        "XDG_CONFIG_HOME": config_dir,
        "TMPDIR": "/dev/shm",
    }
    self._proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=chrome_env,
    )
    ws_url = await self._wait_for_target_ws_url()
    self._ws = await websockets.connect(ws_url, max_size=64 * 1024 * 1024)
    self._recv_task = asyncio.create_task(self._recv_loop())
    await self.send_cdp("Runtime.enable")
    await self.send_cdp("Page.enable")
    await self.send_cdp("DOM.enable")
    await self.send_cdp("Network.enable")
    await self.send_cdp("Log.enable")
    return self

  async def _wait_for_target_ws_url(self, timeout_sec: float = 15.0) -> str:
    deadline = time.monotonic() + timeout_sec
    url = f"http://127.0.0.1:{self.cdp_port}/json/list"
    last_err: Exception | None = None
    while time.monotonic() < deadline:
      try:
        with urllib.request.urlopen(url, timeout=1.0) as resp:
          targets = json.loads(resp.read().decode("utf-8"))
          for target in targets:
            if target.get("type") == "page" and target.get("webSocketDebuggerUrl"):
              return str(target["webSocketDebuggerUrl"])
      except Exception as exc:  # pylint: disable=broad-except
        last_err = exc
      await asyncio.sleep(0.05)
    raise RuntimeError(
        f"Timed out waiting for Chrome CDP endpoint on port {self.cdp_port}: {last_err}"
    )

  async def _recv_loop(self) -> None:
    try:
      async for raw_msg in self._ws:
        data = json.loads(raw_msg)
        if "id" in data:
          fut = self._pending.pop(data["id"], None)
          if fut and not fut.done():
            fut.set_result(data)
        else:
          method = data.get("method", "")
          params = data.get("params", {})
          if method == "Runtime.consoleAPICalled":
            self.console_logs.append(params)
            if params.get("type") == "error":
              self.console_errors.append(params)
          elif method == "Runtime.exceptionThrown":
            self.page_exceptions.append(params)
          elif method == "Log.entryAdded":
            entry = params.get("entry", {})
            if entry.get("level") == "error":
              text = str(entry.get("text", ""))
              url_str = str(entry.get("url", ""))
              if "favicon.ico" not in url_str and "favicon.ico" not in text:
                self.console_errors.append(entry)
          elif method == "Page.loadEventFired":
            self._load_event.set()
    except Exception:  # pylint: disable=broad-except
      pass

  async def send_cdp(
      self, method: str, params: dict[str, Any] | None = None
  ) -> dict[str, Any]:
    self._msg_id += 1
    msg_id = self._msg_id
    payload = {"id": msg_id, "method": method, "params": params or {}}
    loop = asyncio.get_running_loop()
    fut: asyncio.Future[dict[str, Any]] = loop.create_future()
    self._pending[msg_id] = fut
    await self._ws.send(json.dumps(payload))
    resp = await asyncio.wait_for(fut, timeout=30.0)
    if "error" in resp:
      raise RuntimeError(f"CDP error in {method}: {resp['error']}")
    return resp.get("result", {})

  async def close(self) -> None:
    if self._recv_task is not None:
      self._recv_task.cancel()
      try:
        await self._recv_task
      except asyncio.CancelledError:
        pass
      self._recv_task = None
    if self._ws is not None:
      try:
        await self._ws.close()
      except Exception:  # pylint: disable=broad-except
        pass
      self._ws = None
    if self._proc is not None:
      try:
        self._proc.terminate()
        self._proc.wait(timeout=3.0)
      except Exception:  # pylint: disable=broad-except
        try:
          self._proc.kill()
        except Exception:  # pylint: disable=broad-except
          pass
      self._proc = None
    if os.path.exists(self.user_data_dir):
      shutil.rmtree(self.user_data_dir, ignore_errors=True)
    _ACTIVE_SHM_DIRS.discard(self.user_data_dir)

  async def __aenter__(self) -> "ChromeCdpSession":
    return await self.start()

  async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
    await self.close()

  def reset_errors(self) -> None:
    self.console_errors.clear()
    self.page_exceptions.clear()

  def assert_zero_errors(self, context_label: str = "") -> None:
    prefix = f"[{context_label}] " if context_label else ""
    if self.console_errors or self.page_exceptions:
      raise AssertionError(
          f"{prefix}Expected zero console/page errors, got "
          f"{len(self.console_errors)} console.error(s): {self.console_errors[:3]} "
          f"and {len(self.page_exceptions)} pageerror(s): {self.page_exceptions[:3]}"
      )

  async def navigate(
      self, url: str, wait_load: bool = True, wait_app_ready: bool = True
  ) -> None:
    self._load_event.clear()
    await self.send_cdp("Page.navigate", {"url": url})
    if wait_load:
      try:
        await asyncio.wait_for(self._load_event.wait(), timeout=0.1)
      except asyncio.TimeoutError:
        pass
      await self.wait_until_ready(wait_app_ready=wait_app_ready)

  async def reload(self, wait_load: bool = True, wait_app_ready: bool = True) -> None:
    self._load_event.clear()
    await self.send_cdp("Page.reload", {"ignoreCache": False})
    if wait_load:
      try:
        await asyncio.wait_for(self._load_event.wait(), timeout=0.1)
      except asyncio.TimeoutError:
        pass
      await self.wait_until_ready(wait_app_ready=wait_app_ready)

  async def wait_until_ready(
      self, timeout_sec: float = 10.0, wait_app_ready: bool = True
  ) -> None:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
      try:
        ready = await self.eval_js(
            "document.readyState === 'complete' && "
            f"(!{str(wait_app_ready).lower()} || Boolean(window.__APP_STATE__ && window.__APP_STATE__.ready === true))"
        )
        if ready:
          return
      except Exception:  # pylint: disable=broad-except
        pass
      await asyncio.sleep(0.04)

  async def eval_js(
      self,
      expression: str,
      await_promise: bool = True,
      return_by_value: bool = True,
  ) -> Any:
    res = await self.send_cdp(
        "Runtime.evaluate",
        {
            "expression": expression,
            "awaitPromise": await_promise,
            "returnByValue": return_by_value,
        },
    )
    if "exceptionDetails" in res:
      exc = res["exceptionDetails"]
      raise RuntimeError(f"JS evaluation exception: {exc}")
    remote_obj = res.get("result", {})
    if "value" in remote_obj:
      return remote_obj["value"]
    return None

  async def verify_webgl2_context(self) -> dict[str, Any]:
    """Verify that headless Chrome SwiftShader WebGL 2.0 is active."""
    info = await self.eval_js("""(() => {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
      if (!gl) return { ok: false, version: '', renderer: '' };
      const dbg = gl.getExtension('WEBGL_debug_renderer_info');
      return {
        ok: true,
        isWebGL2: typeof WebGL2RenderingContext !== 'undefined' && (gl instanceof WebGL2RenderingContext),
        version: gl.getParameter(gl.VERSION) || '',
        shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION) || '',
        renderer: dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : (gl.getParameter(gl.RENDERER) || ''),
      };
    })()""")
    if not info or not info.get("ok"):
      raise AssertionError(f"WebGL context failed to initialize: {info}")
    return info

  async def set_viewport(self, width: int, height: int, mobile: bool = False) -> None:
    await self.send_cdp(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": 2 if mobile else 1,
            "mobile": mobile,
        },
    )

  async def set_offline_mode(self, offline: bool = True) -> None:
    await self.send_cdp(
        "Network.emulateNetworkConditions",
        {
            "offline": offline,
            "latency": 0,
            "downloadThroughput": -1,
            "uploadThroughput": -1,
        },
    )


@dataclass
class TestCaseSpec:
  """Metadata and async callable for a registered E2E test case."""

  test_id: str
  tier: str
  feature: str
  title: str
  fn: Callable[[ChromeCdpSession, str], Coroutine[Any, Any, None]]


@dataclass
class TestCaseResult:
  """Execution outcome of a single test case."""

  test_id: str
  tier: str
  feature: str
  title: str
  passed: bool
  duration_ms: float
  error_message: str = ""
  console_error_count: int = 0
  page_exception_count: int = 0


TEST_REGISTRY: list[TestCaseSpec] = []


def register_test(test_id: str, tier: str, feature: str, title: str):
  """Decorator registering an async E2E test function in the global registry."""

  def decorator(
      fn: Callable[[ChromeCdpSession, str], Coroutine[Any, Any, None]]
  ) -> Callable[[ChromeCdpSession, str], Coroutine[Any, Any, None]]:
    TEST_REGISTRY.append(
        TestCaseSpec(
            test_id=test_id,
            tier=tier,
            feature=feature,
            title=title,
            fn=fn,
        )
    )
    return fn

  return decorator
