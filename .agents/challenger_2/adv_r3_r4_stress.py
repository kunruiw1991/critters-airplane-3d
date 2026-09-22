#!/usr/bin/env python3
"""Tier 5 White-Box & Adversarial Stress Suite (`adv_r3_r4_stress.py`) — challenger_2.

Empirically stress-tests:
1. R3 Hangar Combinatorial Matrix (3 models x 4 paint palettes = 12 combinations +
   3 propeller styles + 4 contrail particle systems + 4 wing emblems) & Photo Booth
   PNG Integrity (signature, 1280x720 IHDR, raw zlib IDAT scanline decompression &
   3D WebGL viewport RGB pixel variance, FIFO 12-card cap, and localStorage reload survival).
2. R4 Offline-First `docs/index.html` & Single-File `dist/index.html` Network Isolation
   with `Network.emulateNetworkConditions(offline=True)` after initial load, verifying
   100% of 3D rendering, `#img-ref-fox` & `#img-ref-bat` reference portraits, animations,
   and SF -> Boston flight simulation with zero external network requests and zero errors.
"""

from __future__ import annotations

import asyncio
import base64
import json
import math
import os
from pathlib import Path
import struct
import sys
import time
from typing import Any
import zlib

PROJECT_ROOT = Path("/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d")
TESTS_DIR = PROJECT_ROOT / "tests"
CHALLENGER_DIR = PROJECT_ROOT / ".agents" / "challenger_2"

if str(TESTS_DIR) not in sys.path:
  sys.path.insert(0, str(TESTS_DIR))

from cdp_driver import (  # pylint: disable=g-import-not-at-top
    ChromeCdpSession,
    LocalHttpServer,
    cleanup_all_shm_dirs,
    verify_png_data_url,
)


def decode_and_analyze_png_pixels(data_url: str) -> dict[str, Any]:
  """Decode PNG data URL, decompress IDAT chunks, unfilter scanlines, and compute pixel variance."""
  header_info = verify_png_data_url(data_url, min_length=10000)
  prefix = "data:image/png;base64,"
  raw_bytes = base64.b64decode(data_url[len(prefix) :])

  width = header_info["width"]
  height = header_info["height"]
  bit_depth = header_info["bit_depth"]
  color_type = header_info["color_type"]
  assert (width, height) == (1280, 720), f"Expected 1280x720 PNG, got {width}x{height}"
  assert bit_depth == 8 and color_type in (2, 6), (
      f"Unexpected bit_depth={bit_depth}, color_type={color_type}"
  )
  bpp = 4 if color_type == 6 else 3
  stride = width * bpp

  # Extract all IDAT chunks
  pos = 8
  idat_parts: list[bytes] = []
  iend_found = False
  while pos + 8 <= len(raw_bytes):
    chunk_len, chunk_type = struct.unpack(">I4s", raw_bytes[pos : pos + 8])
    chunk_data = raw_bytes[pos + 8 : pos + 8 + chunk_len]
    pos += 12 + chunk_len
    if chunk_type == b"IDAT":
      idat_parts.append(chunk_data)
    elif chunk_type == b"IEND":
      iend_found = True
      break

  assert iend_found and idat_parts, "Missing IDAT or IEND chunk in PNG payload"
  decompressed = zlib.decompress(b"".join(idat_parts))
  expected_len = height * (1 + stride)
  assert len(decompressed) == expected_len, (
      f"Decompressed IDAT size mismatch: {len(decompressed)} vs {expected_len}"
  )

  # Reconstruct PNG scanlines (filters 0..4: None, Sub, Up, Average, Paeth)
  recon = bytearray(height * stride)
  for y in range(height):
    row_start = y * (1 + stride)
    filter_type = decompressed[row_start]
    src_row = decompressed[row_start + 1 : row_start + 1 + stride]
    dst_offset = y * stride
    prev_offset = (y - 1) * stride

    if filter_type == 0:  # None
      recon[dst_offset : dst_offset + stride] = src_row
    elif filter_type == 1:  # Sub
      for i in range(stride):
        left = recon[dst_offset + i - bpp] if i >= bpp else 0
        recon[dst_offset + i] = (src_row[i] + left) & 0xFF
    elif filter_type == 2:  # Up
      if y == 0:
        recon[dst_offset : dst_offset + stride] = src_row
      else:
        for i in range(stride):
          up = recon[prev_offset + i]
          recon[dst_offset + i] = (src_row[i] + up) & 0xFF
    elif filter_type == 3:  # Average
      for i in range(stride):
        left = recon[dst_offset + i - bpp] if i >= bpp else 0
        up = recon[prev_offset + i] if y > 0 else 0
        recon[dst_offset + i] = (src_row[i] + ((left + up) >> 1)) & 0xFF
    elif filter_type == 4:  # Paeth
      for i in range(stride):
        a = recon[dst_offset + i - bpp] if i >= bpp else 0
        b = recon[prev_offset + i] if y > 0 else 0
        c = recon[prev_offset + i - bpp] if (y > 0 and i >= bpp) else 0
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
        recon[dst_offset + i] = (src_row[i] + pr) & 0xFF
    else:
      raise AssertionError(f"Unsupported PNG filter type {filter_type} on row {y}")

  # Sample pixels strictly inside the pure 3D WebGL viewport region
  # (x in [120, 1160], y in [90, 580]) — completely excluding postcard frame/caption/stickers!
  r_vals: list[int] = []
  g_vals: list[int] = []
  b_vals: list[int] = []
  unique_rgb: set[tuple[int, int, int]] = set()

  for y in range(90, 580, 4):
    row_off = y * stride
    for x in range(120, 1160, 4):
      px_off = row_off + x * bpp
      r = recon[px_off]
      g = recon[px_off + 1]
      b = recon[px_off + 2]
      r_vals.append(r)
      g_vals.append(g)
      b_vals.append(b)
      unique_rgb.add((r, g, b))

  n = len(r_vals)
  mean_r = sum(r_vals) / n
  mean_g = sum(g_vals) / n
  mean_b = sum(b_vals) / n
  std_r = math.sqrt(sum((v - mean_r) ** 2 for v in r_vals) / n)
  std_g = math.sqrt(sum((v - mean_g) ** 2 for v in g_vals) / n)
  std_b = math.sqrt(sum((v - mean_b) ** 2 for v in b_vals) / n)

  return {
      **header_info,
      "sampled_pixels": n,
      "unique_rgb_count": len(unique_rgb),
      "mean_rgb": (round(mean_r, 2), round(mean_g, 2), round(mean_b, 2)),
      "std_rgb": (round(std_r, 2), round(std_g, 2), round(std_b, 2)),
  }


async def run_adversarial_suite() -> dict[str, Any]:
  """Run all Tier 5 adversarial R3 & R4 stress tests and return structured report."""
  models = ["biplane", "supersonic_jet", "origami_glider"]
  palettes = [
      "sunset_fox_amber",
      "midnight_bat_indigo",
      "huntrx_golden_neon",
      "mint_cloud",
  ]
  propellers = [
      "classic_wood_brass",
      "starlight_crystal_turbine",
      "rainbow_flower_pinwheel",
  ]
  contrails = [
      "rainbow_ribbon",
      "lantern_fireflies",
      "starlight_moon_dust",
      "heart_bubbles",
  ]
  emblems = [
      "fox_lantern_crest",
      "bat_moonstar_crest",
      "sf_boston_heart_wings",
      "golden_star_crown",
  ]
  backdrops = [
      "sf_golden_gate_sunrise",
      "rainbow_cloud_archipelago",
      "boston_zakim_starlight",
  ]

  report: dict[str, Any] = {
      "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
      "tests": [],
      "matrix_12_results": [],
      "png_pixel_analyses": [],
      "offline_isolation_results": {},
  }

  def record_check(test_id: str, title: str, passed: bool, details: dict[str, Any]) -> None:
    report["tests"].append({
        "test_id": test_id,
        "title": title,
        "passed": passed,
        "details": details,
    })
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_id} — {title}")
    if not passed:
      raise AssertionError(f"{test_id} failed: {details}")

  with LocalHttpServer(PROJECT_ROOT) as server:
    async with ChromeCdpSession() as session:
      webgl_info = await session.verify_webgl2_context()
      print(f"[WebGL 2.0 Context] {webgl_info['version']} | {webgl_info['renderer']}")

      # Track all network URLs requested during the session
      network_requests: list[str] = []
      network_failures: list[dict[str, Any]] = []

      orig_recv = session._ws

      await session.navigate(f"{server.base_url}/index.html", wait_load=True, wait_app_ready=True)
      session.reset_errors()

      # =========================================================================
      # ADV-R3-01: Exhaustive 3 x 4 = 12 Aircraft Model x Paint Palette Matrix
      #            + cycling all 3 Propellers, 4 Contrails, and 4 Wing Emblems
      # =========================================================================
      await session.eval_js("""(() => {
        localStorage.removeItem('critters_airplane_3d_postcards_v1');
        window.__APP_STATE__.photoBooth.savedPostcards.length = 0;
        window.__APP_STATE__.setView('hangar');
      })()""")

      combo_idx = 0
      for m_idx, model_id in enumerate(models):
        for p_idx, palette_id in enumerate(palettes):
          prop_id = propellers[combo_idx % len(propellers)]
          contrail_id = contrails[combo_idx % len(contrails)]
          emblem_id = emblems[combo_idx % len(emblems)]
          backdrop_id = backdrops[combo_idx % len(backdrops)]
          combo_idx += 1

          combo_res = await session.eval_js(f"""(() => {{
            const app = window.__APP_STATE__;
            app.setView('hangar');
            app.setPlaneModel({json.dumps(model_id)});
            app.setPaintPalette({json.dumps(palette_id)});
            app.setPropellerStyle({json.dumps(prop_id)});
            app.setContrailStyle({json.dumps(contrail_id)});
            app.setWingEmblem({json.dumps(emblem_id)});
            app.stepSimulation(8, 1/60);

            const h = app.hangar;
            const plane = h.airplaneGroup;
            const propGrp = h.propellerGroup || plane.getObjectByName('propellerGroup');
            const leftEmblem = plane.getObjectByName('leftWingEmblemMesh');
            const rightEmblem = plane.getObjectByName('rightWingEmblemMesh');
            const foxInPlane = Boolean(plane.getObjectByName('SunnyFox'));
            const batInPlane = Boolean(plane.getObjectByName('LunaBat'));

            // Count active contrail particles
            let activeContrails = 0;
            h.contrailSystem.traverse(c => {{
              if (c.isMesh && c.visible && c.material && c.material.opacity > 0.05) {{
                activeContrails += 1;
              }}
            }});

            // Capture postcard for this combination
            app.setView('photo_booth');
            app.setPhotoBackdrop({json.dumps(backdrop_id)});
            app.setPhotoCaption(`Combo #${{ {combo_idx} }}: {model_id} + {palette_id}`);
            const card = app.capturePostcard();

            return {{
              comboIndex: {combo_idx},
              modelId: h.modelId,
              paintPaletteId: h.paintPaletteId,
              propellerStyleId: h.propellerStyleId,
              contrailStyleId: h.contrailStyleId,
              wingEmblemId: h.wingEmblemId,
              vertexCount: h.vertexCount,
              primaryColorHex: h.primaryColorHex,
              secondaryColorHex: h.secondaryColorHex,
              propellerChildren: propGrp ? propGrp.children.length : 0,
              hasEmblems: Boolean(leftEmblem && rightEmblem && leftEmblem.material.map),
              foxInPlane,
              batInPlane,
              activeContrails,
              dataUrl: card.dataUrl,
              savedCount: app.photoBooth.savedPostcards.length,
            }};
          }})()""")

          px_stats = decode_and_analyze_png_pixels(combo_res["dataUrl"])
          assert combo_res["modelId"] == model_id
          assert combo_res["paintPaletteId"] == palette_id
          assert combo_res["propellerStyleId"] == prop_id
          assert combo_res["contrailStyleId"] == contrail_id
          assert combo_res["wingEmblemId"] == emblem_id
          assert combo_res["vertexCount"] > 1500, f"Low vertexCount: {combo_res['vertexCount']}"
          assert combo_res["hasEmblems"] is True
          assert combo_res["foxInPlane"] and combo_res["batInPlane"]
          assert combo_res["activeContrails"] >= 2
          # Verify real 3D WebGL scene pixel variance (non-blank, non-uniform)
          assert px_stats["unique_rgb_count"] > 250, f"Low unique colors: {px_stats}"
          assert max(px_stats["std_rgb"]) > 12.0, f"Flat pixel std dev: {px_stats}"

          entry_summary = {
              "combo": f"{model_id} x {palette_id}",
              "propeller": prop_id,
              "contrail": contrail_id,
              "emblem": emblem_id,
              "backdrop": backdrop_id,
              "vertexCount": combo_res["vertexCount"],
              "primaryColorHex": combo_res["primaryColorHex"],
              "secondaryColorHex": combo_res["secondaryColorHex"],
              "png_bytes": px_stats["byte_length"],
              "png_dimensions": f"{px_stats['width']}x{px_stats['height']}",
              "viewport_unique_rgb": px_stats["unique_rgb_count"],
              "viewport_mean_rgb": px_stats["mean_rgb"],
              "viewport_std_rgb": px_stats["std_rgb"],
          }
          report["matrix_12_results"].append(entry_summary)
          report["png_pixel_analyses"].append(px_stats)

      session.assert_zero_errors("ADV-R3-01")
      record_check(
          "ADV-R3-01",
          "All 3x4=12 Aircraft x Palette combinations + 3 Propellers + 4 Contrails + 4 Emblems + 12 Postcard PNGs (1280x720 IHDR & raw IDAT pixel variance)",
          True,
          {
              "combinations_tested": len(report["matrix_12_results"]),
              "min_vertex_count": min(x["vertexCount"] for x in report["matrix_12_results"]),
              "min_unique_rgb": min(x["viewport_unique_rgb"] for x in report["matrix_12_results"]),
          },
      )

      # =========================================================================
      # ADV-R3-02: Verify Distinct 3D Viewport Pixel Signatures Across Backdrops
      #            & FIFO 12-Postcard Cap + localStorage Survival Across Reload
      # =========================================================================
      mean_rgbs = [x["viewport_mean_rgb"] for x in report["matrix_12_results"][:3]]
      # Backdrops 0 (Day), 1 (Sunset), 2 (Night) must yield measurably distinct mean RGBs
      dist_01 = sum(abs(a - b) for a, b in zip(mean_rgbs[0], mean_rgbs[1]))
      dist_12 = sum(abs(a - b) for a, b in zip(mean_rgbs[1], mean_rgbs[2]))
      assert dist_01 > 15.0 and dist_12 > 15.0, (
          f"Expected distinct 3D WebGL backdrop RGB means across Day/Sunset/Night, got {mean_rgbs}"
      )

      # Capture a 13th postcard to test the 12-postcard FIFO ring buffer cap in localStorage
      fifo_res = await session.eval_js("""(() => {
        const app = window.__APP_STATE__;
        app.setPlaneModel('origami_glider');
        app.setPaintPalette('huntrx_golden_neon');
        app.setPropellerStyle('rainbow_flower_pinwheel');
        app.setContrailStyle('heart_bubbles');
        app.setWingEmblem('golden_star_crown');
        app.setPhotoCaption('Postcard #13 FIFO Stress Test');
        const c13 = app.capturePostcard();
        app.saveConfigToLocalStorage();
        return {
          savedLength: app.photoBooth.savedPostcards.length,
          lastCaption: app.photoBooth.savedPostcards[app.photoBooth.savedPostcards.length - 1].captionText,
          firstCaption: app.photoBooth.savedPostcards[0].captionText,
        };
      })()""")
      assert fifo_res["savedLength"] == 12, f"Expected 12-card FIFO cap, got {fifo_res}"
      assert fifo_res["lastCaption"] == "Postcard #13 FIFO Stress Test"
      assert "Combo #2" in fifo_res["firstCaption"], f"Expected Combo #1 evicted, got {fifo_res}"

      # Reload page and verify both hangar config & 12 postcards survive in localStorage
      await session.reload(wait_load=True, wait_app_ready=True)
      reload_state = await session.eval_js("""(() => {
        const app = window.__APP_STATE__;
        return {
          modelId: app.hangar.modelId,
          paintPaletteId: app.hangar.paintPaletteId,
          propellerStyleId: app.hangar.propellerStyleId,
          contrailStyleId: app.hangar.contrailStyleId,
          wingEmblemId: app.hangar.wingEmblemId,
          savedPostcardsCount: app.photoBooth.savedPostcards.length,
          lastCaption: app.photoBooth.savedPostcards[app.photoBooth.savedPostcards.length - 1].captionText,
          rawConfigPresent: Boolean(localStorage.getItem('critters_airplane_3d_config_v1')),
          rawPostcardsPresent: Boolean(localStorage.getItem('critters_airplane_3d_postcards_v1')),
        };
      })()""")
      assert reload_state["modelId"] == "origami_glider"
      assert reload_state["paintPaletteId"] == "huntrx_golden_neon"
      assert reload_state["propellerStyleId"] == "rainbow_flower_pinwheel"
      assert reload_state["contrailStyleId"] == "heart_bubbles"
      assert reload_state["wingEmblemId"] == "golden_star_crown"
      assert reload_state["savedPostcardsCount"] == 12
      assert reload_state["lastCaption"] == "Postcard #13 FIFO Stress Test"
      session.assert_zero_errors("ADV-R3-02")
      record_check(
          "ADV-R3-02",
          "3D Viewport Day/Sunset/Night RGB divergence + 13-postcard FIFO cap (12 max) + localStorage survival across page.reload()",
          True,
          {
              "backdrop_rgb_means": mean_rgbs,
              "l1_distance_day_sunset": round(dist_01, 2),
              "l1_distance_sunset_night": round(dist_12, 2),
              "reload_state": reload_state,
          },
      )

      # =========================================================================
      # ADV-R4-01 & ADV-R4-02: Offline-First `docs/index.html` & `dist/index.html`
      #                        Network Isolation Stress Test
      # =========================================================================
      for idx, bundle_path in enumerate(("/docs/index.html", "/dist/index.html"), 1):
        test_id = f"ADV-R4-0{idx}"
        await session.set_offline_mode(False)
        await session.navigate(f"{server.base_url}{bundle_path}", wait_load=True, wait_app_ready=True)
        session.reset_errors()

        # Verify zero external resource URLs exist in performance entries after load
        perf_audit = await session.eval_js("""(() => {
          const entries = performance.getEntriesByType('resource').map(e => e.name);
          const external = entries.filter(u => !u.startsWith(window.location.origin) && !u.startsWith('data:') && !u.startsWith('blob:'));
          return { totalResources: entries.length, externalUrls: external };
        })()""")
        assert not perf_audit["externalUrls"], (
            f"External network requests detected on {bundle_path}: {perf_audit}"
        )

        # Enable strict CDP Network Offline Emulation (`offline=True`, 0 throughput)
        await session. send_cdp(
            "Network.emulateNetworkConditions",
            {
                "offline": True,
                "latency": 0,
                "downloadThroughput": 0,
                "uploadThroughput": 0,
            },
        )

        try:
          offline_res = await session.eval_js("""(async () => {
            const app = window.__APP_STATE__;
            const res = {};

            // 1. Verify Reference Portraits (#img-ref-fox, #img-ref-bat)
            const foxImg = document.getElementById('img-ref-fox');
            const batImg = document.getElementById('img-ref-bat');
            res.foxPortrait = {
              complete: Boolean(foxImg && foxImg.complete),
              naturalWidth: foxImg ? foxImg.naturalWidth : 0,
              naturalHeight: foxImg ? foxImg.naturalHeight : 0,
            };
            res.batPortrait = {
              complete: Boolean(batImg && batImg.complete),
              naturalWidth: batImg ? batImg.naturalWidth : 0,
              naturalHeight: batImg ? batImg.naturalHeight : 0,
            };

            // 2. Cycle all 6 animations + accessories offline
            app.setView('character_studio');
            const animNames = ['idle', 'wave', 'wingFlapTailWag', 'bounceDance', 'barrelRollCheer', 'cockpitPilotSteer'];
            for (const anim of animNames) {
              app.setCharacterAnimation(anim);
              app.stepSimulation(5, 1/60);
            }
            app.triggerCharacterTapReaction('SunnyFox');
            app.triggerCharacterTapReaction('LunaBat');

            // 3. Cycle all 3 aircraft models & palettes offline
            app.setView('hangar');
            for (const m of ['biplane', 'supersonic_jet', 'origami_glider']) {
              app.setPlaneModel(m);
              app.stepSimulation(4, 1/60);
            }
            app.setPaintPalette('midnight_bat_indigo');
            app.setContrailStyle('starlight_moon_dust');
            app.setWingEmblem('bat_moonstar_crest');

            // 4. Full SF -> Boston 3-Zone flight simulation offline
            app.setView('flight_simulator');
            app.resetFlight();
            app.startFlight();
            app.setSteering(0.65, 0.45);
            app.triggerBoost();
            app.triggerBarrelRoll();
            app.dropHeartPackage();
            app.collectNearestItem('golden_lantern');
            app.collectNearestItem('crescent_moon_star');
            app.stepSimulation(20, 1/60);
            app.setZone(2);
            app.stepSimulation(15, 1/60);
            app.setZone(3);
            app.setTimeOfDay('night');
            app.collectNearestItem('starlight_ring');
            app.stepSimulation(15, 1/60);
            app.completeFlightToBoston();

            // 5. Capture 3D PNG Postcard while strictly offline
            app.setView('photo_booth');
            app.setPhotoBackdrop('boston_zakim_starlight');
            app.setPhotoCaption('Offline Network Isolation Verified!');
            const card = app.capturePostcard();

            return {
              navigatorOnLine: navigator.onLine,
              ready: app.ready,
              foxPortrait: res.foxPortrait,
              batPortrait: res.batPortrait,
              flightCompleted: app.flight.completed,
              flightState: app.flight.flightState,
              flightScore: app.flight.score,
              pendantLightsActive: app.flight.pendantLightsActive,
              revealedRings: app.flight.revealedStarlightRingsCount,
              dataUrl: card.dataUrl,
            };
          })()""")

          offline_px = decode_and_analyze_png_pixels(offline_res["dataUrl"])
          assert offline_res["navigatorOnLine"] is False, (
              f"Expected navigator.onLine === false under CDP offline mode: {offline_res}"
          )
          assert offline_res["foxPortrait"]["complete"] and offline_res["foxPortrait"]["naturalWidth"] == 1024
          assert offline_res["batPortrait"]["complete"] and offline_res["batPortrait"]["naturalWidth"] == 1024
          assert offline_res["flightCompleted"] is True and offline_res["flightState"] == "landed_boston"
          assert offline_res["flightScore"] >= 600
          assert offline_res["pendantLightsActive"] is True and offline_res["revealedRings"] > 0
          assert offline_px["unique_rgb_count"] > 250 and max(offline_px["std_rgb"]) > 12.0

          session.assert_zero_errors(test_id)
          bundle_summary = {
              "bundle_path": bundle_path,
              "navigator_online": offline_res["navigatorOnLine"],
              "external_urls_count": len(perf_audit["externalUrls"]),
              "fox_portrait": offline_res["foxPortrait"],
              "bat_portrait": offline_res["batPortrait"],
              "flight_score": offline_res["flightScore"],
              "offline_postcard_png_bytes": offline_px["byte_length"],
              "offline_viewport_unique_rgb": offline_px["unique_rgb_count"],
              "offline_viewport_std_rgb": offline_px["std_rgb"],
          }
          report["offline_isolation_results"][bundle_path] = bundle_summary
          record_check(
              test_id,
              f"Offline Network Isolation (`Network.emulateNetworkConditions(offline=True)`) on `{bundle_path}`",
              True,
              bundle_summary,
          )
        finally:
          await session.set_offline_mode(False)

  cleanup_all_shm_dirs()
  return report


def main() -> None:
  t0 = time.monotonic()
  report = asyncio.run(run_adversarial_suite())
  elapsed_s = time.monotonic() - t0
  report["duration_seconds"] = round(elapsed_s, 2)
  out_json = CHALLENGER_DIR / "adv_r3_r4_report.json"
  out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
  print("=" * 84)
  print(
      f"ALL {len(report['tests'])}/{len(report['tests'])} ADVERSARIAL STRESS CHECKS PASSED "
      f"({len(report['matrix_12_results'])} Hangar/PNG matrix cells + 2 Offline Bundles) "
      f"in {elapsed_s:.2f}s"
  )
  print(f"Report saved to: {out_json}")
  print("=" * 84)


if __name__ == "__main__":
  main()
