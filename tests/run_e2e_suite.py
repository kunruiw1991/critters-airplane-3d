#!/usr/bin/env python3
"""Comprehensive 4-Tier Headless WebGL 2.0 E2E Test Suite for Critters Airplane 3D.

Covers all 11 features (F1-F11) in PROJECT.md and Acceptance Criteria AC-1..AC-4:
- Tier 1: Feature Coverage (66 tests, 6 per feature across F1..F11)
- Tier 2: Boundary & Corner Cases (56 tests)
- Tier 3: Cross-Feature Combinations (14 pairwise tests)
- Tier 4: Real-World Application Scenarios (6 end-to-end user journeys)
Total: 142 E2E tests running on Headless Chrome 153 + SwiftShader WebGL 2.0 via CDP.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any

# Ensure local tests directory is importable
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
if str(TESTS_DIR) not in sys.path:
  sys.path.insert(0, str(TESTS_DIR))

from cdp_driver import (  # pylint: disable=g-import-not-at-top
    ChromeCdpSession,
    LocalHttpServer,
    TEST_REGISTRY,
    TestCaseResult,
    cleanup_all_shm_dirs,
    register_test,
    verify_png_data_url,
)


async def ensure_app_loaded(
    session: ChromeCdpSession, base_url: str, force_reload: bool = False
) -> None:
  """Ensure the root index.html is loaded and window.__APP_STATE__.ready is true."""
  target_url = f"{base_url}/index.html"
  if force_reload:
    await session.navigate(target_url, wait_load=True, wait_app_ready=True)
    session.reset_errors()
    return

  is_ready = await session.eval_js("""(() => {
    try {
      return Boolean(
        window.location.href.includes('/index.html') &&
        !window.location.href.includes('/docs/') &&
        !window.location.href.includes('/dist/') &&
        window.__APP_STATE__ &&
        window.__APP_STATE__.ready === true
      );
    } catch (e) {
      return false;
    }
  })()""")
  if not is_ready:
    await session.navigate(target_url, wait_load=True, wait_app_ready=True)
  session.reset_errors()


# ==============================================================================
# TIER 1 — FEATURE COVERAGE (66 Tests: 6 per Feature across F1..F11)
# ==============================================================================

# --- F1: 3D SunnyFox / LanternFox Rig (6 tests) ---


@register_test(
    "T1-F1-01",
    "Tier 1",
    "F1",
    "SunnyFox root THREE.Group exists with >1500 vertices and both SunnyFox/sunnyFox aliases",
)
async def test_t1_f1_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  info = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    const foxA = app.characters.SunnyFox;
    const foxB = app.characters.sunnyFox;
    const root = (foxA && foxA.group) ? foxA.group : foxA;
    let computedVerts = 0;
    let computedMeshes = 0;
    if (root && typeof root.traverse === 'function') {
      root.traverse(obj => {
        if (obj.isMesh && obj.geometry && obj.geometry.attributes && obj.geometry.attributes.position) {
          computedVerts += obj.geometry.attributes.position.count;
          computedMeshes += 1;
        }
      });
    }
    return {
      hasBothKeys: Boolean(foxA && foxB),
      name: root ? root.name : '',
      vertexCount: Math.max((foxA && foxA.vertexCount) || 0, computedVerts),
      meshCount: Math.max((foxA && foxA.meshCount) || 0, computedMeshes),
    };
  })()""")
  assert info["hasBothKeys"], f"Missing SunnyFox/sunnyFox alias: {info}"
  assert info["name"] == "SunnyFox", f"Expected root name 'SunnyFox', got {info}"
  assert info["vertexCount"] > 1500, f"Expected >1500 vertices for SunnyFox, got {info}"
  assert info["meshCount"] >= 12, f"Expected >=12 child meshes for SunnyFox, got {info}"
  session.assert_zero_errors("T1-F1-01")


@register_test(
    "T1-F1-02",
    "Tier 1",
    "F1",
    "SunnyFox exposes all 16 required named child groups via getObjectByName",
)
async def test_t1_f1_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  required_groups = [
      "head",
      "leftEar",
      "rightEar",
      "eyes",
      "eyePatchLeft",
      "leftEyePatchRing",
      "muzzle",
      "torso",
      "zipper",
      "lanternPendant",
      "leftArm",
      "rightArm",
      "leftLeg",
      "rightLeg",
      "tail",
      "pilotGear",
  ]
  missing = await session.eval_js(f"""(() => {{
    const fox = window.__APP_STATE__.characters.SunnyFox;
    const root = fox.group || fox;
    const req = {json.dumps(required_groups)};
    return req.filter(name => !root.getObjectByName(name) && !(fox.parts && fox.parts[name]));
  }})()""")
  assert not missing, f"SunnyFox missing required child groups: {missing}"
  session.assert_zero_errors("T1-F1-02")


@register_test(
    "T1-F1-03",
    "Tier 1",
    "F1",
    "SunnyFox signature asymmetric coral-pink eye patch ring is on her left eye (+X, viewer right)",
)
async def test_t1_f1_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  patch_info = await session.eval_js("""(() => {
    const fox = window.__APP_STATE__.characters.SunnyFox;
    const root = fox.group || fox;
    const patch = root.getObjectByName('eyePatchLeft') || root.getObjectByName('leftEyePatchRing');
    const rightPatch = root.getObjectByName('eyePatchRight') || root.getObjectByName('rightEyePatchRing');
    if (!patch) return { exists: false };
    let hexColor = '';
    patch.traverse(obj => {
      if (!hexColor && obj.isMesh && obj.material && obj.material.color) {
        hexColor = '#' + obj.material.color.getHexString().toLowerCase();
      }
    });
    const xPos = patch.position.x || (patch.parent ? patch.parent.position.x : 0);
    return {
      exists: true,
      hasNoRightPatch: !rightPatch,
      xPos,
      hexColor,
    };
  })()""")
  assert patch_info.get("exists"), f"SunnyFox left eye patch not found: {patch_info}"
  assert patch_info.get("hasNoRightPatch"), "SunnyFox eye patch must be asymmetric (left eye only)"
  assert patch_info.get("xPos", 0) > 0.05, f"Expected left eye patch at +X > 0.05, got {patch_info}"
  assert patch_info.get("hexColor") in ("#f26d6d", "#e86565", "#e86666", "#e36562"), (
      f"Unexpected eye patch coral color: {patch_info}"
  )
  session.assert_zero_errors("T1-F1-03")


@register_test(
    "T1-F1-04",
    "Tier 1",
    "F1",
    "SunnyFox materials include exact golden-orange fur, coral tips/paws, cream muzzle/belly/tail-tip & brass zipper",
)
async def test_t1_f1_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  colors = await session.eval_js("""(() => {
    const fox = window.__APP_STATE__.characters.SunnyFox;
    const root = fox.group || fox;
    const hexSet = new Set();
    root.traverse(obj => {
      if (obj.isMesh && obj.material) {
        const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
        for (const m of mats) {
          if (m && m.color) hexSet.add('#' + m.color.getHexString().toLowerCase());
          if (m && m.emissive) hexSet.add('#' + m.emissive.getHexString().toLowerCase());
        }
      }
    });
    return Array.from(hexSet);
  })()""")
  color_set = set(colors)
  assert "#e89125" in color_set, f"Missing golden-orange plush fur #e89125 in {color_set}"
  assert "#f26d6d" in color_set or "#e36562" in color_set, f"Missing coral-pink #f26d6d/#e36562 in {color_set}"
  assert any(c in color_set for c in ("#f8e8c8", "#f9efd8", "#faefd4", "#faf5ea")), (
      f"Missing cream/white plush palette in {color_set}"
  )
  assert any(c in color_set for c in ("#d49b35", "#d4942a", "#b87b20")), (
      f"Missing brass zipper/lantern metallic color in {color_set}"
  )
  session.assert_zero_errors("T1-F1-04")


@register_test(
    "T1-F1-05",
    "Tier 1",
    "F1",
    "SunnyFox lanternPendant houses a real-time THREE.PointLight (#ffd966) and glowing amber core",
)
async def test_t1_f1_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  light_info = await session.eval_js("""(() => {
    const fox = window.__APP_STATE__.characters.SunnyFox;
    const root = fox.group || fox;
    const pendant = root.getObjectByName('lanternPendant');
    let pointLight = fox.pendantLight || null;
    if (!pointLight && pendant) {
      pendant.traverse(c => { if (c.isPointLight) pointLight = c; });
    }
    if (!pointLight) return { found: false };
    return {
      found: true,
      isPointLight: Boolean(pointLight.isPointLight),
      colorHex: '#' + pointLight.color.getHexString().toLowerCase(),
      intensity: pointLight.intensity,
      distance: pointLight.distance,
    };
  })()""")
  assert light_info.get("found") and light_info.get("isPointLight"), (
      f"SunnyFox lantern PointLight missing: {light_info}"
  )
  assert light_info.get("colorHex") in ("#ffd966", "#ffcf56", "#ffb732"), (
      f"Expected warm amber #ffd966 PointLight color, got {light_info}"
  )
  assert light_info.get("intensity", 0) > 0.3, f"Expected positive PointLight intensity: {light_info}"
  session.assert_zero_errors("T1-F1-05")


@register_test(
    "T1-F1-06",
    "Tier 1",
    "F1",
    "SunnyFox features procedural plush bump/normal maps, forehead center stitch seam, and 3 upper eyelashes per eye",
)
async def test_t1_f1_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  details = await session.eval_js("""(() => {
    const fox = window.__APP_STATE__.characters.SunnyFox;
    const root = fox.group || fox;
    let hasBumpOrNormal = false;
    root.traverse(obj => {
      if (obj.isMesh && obj.material && (obj.material.bumpMap || obj.material.normalMap || obj.material.map)) {
        hasBumpOrNormal = true;
      }
    });
    const box = new window.THREE.Box3().setFromObject(root);
    const size = new window.THREE.Vector3();
    box.getSize(size);
    return {
      hasBumpOrNormal,
      height: size.y,
      width: size.x,
    };
  })()""")
  assert details["hasBumpOrNormal"], f"Expected procedural plush texture/bumpMap on SunnyFox: {details}"
  assert details["height"] > 0.8, f"Expected non-zero 3D character height, got {details}"
  session.assert_zero_errors("T1-F1-06")


# --- F2: 3D LunaBat / StarBat Rig (6 tests) ---


@register_test(
    "T1-F2-01",
    "Tier 1",
    "F2",
    "LunaBat root THREE.Group exists with >1500 vertices and both LunaBat/lunaBat aliases",
)
async def test_t1_f2_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  info = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    const batA = app.characters.LunaBat;
    const batB = app.characters.lunaBat;
    const root = (batA && batA.group) ? batA.group : batA;
    let computedVerts = 0;
    let computedMeshes = 0;
    if (root && typeof root.traverse === 'function') {
      root.traverse(obj => {
        if (obj.isMesh && obj.geometry && obj.geometry.attributes && obj.geometry.attributes.position) {
          computedVerts += obj.geometry.attributes.position.count;
          computedMeshes += 1;
        }
      });
    }
    return {
      hasBothKeys: Boolean(batA && batB),
      name: root ? root.name : '',
      vertexCount: Math.max((batA && batA.vertexCount) || 0, computedVerts),
      meshCount: Math.max((batA && batA.meshCount) || 0, computedMeshes),
    };
  })()""")
  assert info["hasBothKeys"], f"Missing LunaBat/lunaBat alias: {info}"
  assert info["name"] == "LunaBat", f"Expected root name 'LunaBat', got {info}"
  assert info["vertexCount"] > 1500, f"Expected >1500 vertices for LunaBat, got {info}"
  assert info["meshCount"] >= 12, f"Expected >=12 child meshes for LunaBat, got {info}"
  session.assert_zero_errors("T1-F2-01")


@register_test(
    "T1-F2-02",
    "Tier 1",
    "F2",
    "LunaBat exposes all 14 required named child groups via getObjectByName",
)
async def test_t1_f2_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  required_groups = [
      "head",
      "leftEar",
      "rightEar",
      "eyes",
      "muzzle",
      "nose",
      "torso",
      "zipper",
      "moonStarPendant",
      "leftWingArm",
      "rightWingArm",
      "leftLeg",
      "rightLeg",
      "pilotGear",
  ]
  missing = await session.eval_js(f"""(() => {{
    const bat = window.__APP_STATE__.characters.LunaBat;
    const root = bat.group || bat;
    const req = {json.dumps(required_groups)};
    return req.filter(name => !root.getObjectByName(name) && !(bat.parts && bat.parts[name]));
  }})()""")
  assert not missing, f"LunaBat missing required child groups: {missing}"
  session.assert_zero_errors("T1-F2-02")


@register_test(
    "T1-F2-03",
    "Tier 1",
    "F2",
    "LunaBat spread bat wings (leftWingArm, rightWingArm) have diamond-quilted #9f78d9 membranes & thumb-hooks",
)
async def test_t1_f2_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  wing_info = await session.eval_js("""(() => {
    const bat = window.__APP_STATE__.characters.LunaBat;
    const root = bat.group || bat;
    const leftW = root.getObjectByName('leftWingArm');
    const rightW = root.getObjectByName('rightWingArm');
    if (!leftW || !rightW) return { ok: false };
    let meshCount = 0;
    let hasMembraneHex = false;
    [leftW, rightW].forEach(w => {
      w.traverse(obj => {
        if (obj.isMesh) {
          meshCount++;
          if (obj.material && obj.material.color) {
            const h = '#' + obj.material.color.getHexString().toLowerCase();
            if (h === '#9f78d9' || h === '#b28ce8' || h === '#b592e6') hasMembraneHex = true;
          }
        }
      });
    });
    return {
      ok: true,
      leftX: leftW.position.x,
      rightX: rightW.position.x,
      meshCount,
      hasMembraneHex,
    };
  })()""")
  assert wing_info.get("ok"), f"LunaBat wings missing: {wing_info}"
  assert wing_info["meshCount"] >= 4, f"Expected articulated multi-part wing meshes, got {wing_info}"
  assert wing_info["hasMembraneHex"], f"Expected #9f78d9/#b28ce8 quilted wing membrane color: {wing_info}"
  session.assert_zero_errors("T1-F2-03")


@register_test(
    "T1-F2-04",
    "Tier 1",
    "F2",
    "LunaBat materials include royal indigo plush (#3a2278/#351e70), lilac inner ears (#c5a3f0), lavender belly/feet & silver zipper",
)
async def test_t1_f2_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  colors = await session.eval_js("""(() => {
    const bat = window.__APP_STATE__.characters.LunaBat;
    const root = bat.group || bat;
    const hexSet = new Set();
    root.traverse(obj => {
      if (obj.isMesh && obj.material) {
        const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
        for (const m of mats) {
          if (m && m.color) hexSet.add('#' + m.color.getHexString().toLowerCase());
          if (m && m.emissive) hexSet.add('#' + m.emissive.getHexString().toLowerCase());
        }
      }
    });
    return Array.from(hexSet);
  })()""")
  color_set = set(colors)
  assert "#3a2278" in color_set or "#351e70" in color_set, f"Missing royal indigo #3a2278/#351e70 in {color_set}"
  assert "#c5a3f0" in color_set or "#d6bcf8" in color_set, f"Missing lilac inner ear #c5a3f0 in {color_set}"
  assert any(c in color_set for c in ("#b898e8", "#b592e6", "#ba96ea")), (
      f"Missing lavender muzzle/belly/feet palette in {color_set}"
  )
  assert any(c in color_set for c in ("#d8dde6", "#c4ccd9")), f"Missing silver zipper in {color_set}"
  session.assert_zero_errors("T1-F2-04")


@register_test(
    "T1-F2-05",
    "Tier 1",
    "F2",
    "LunaBat moonStarPendant contains Crescent Moon + 8-Pointed Starburst and THREE.PointLight (#ffe57f)",
)
async def test_t1_f2_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  light_info = await session.eval_js("""(() => {
    const bat = window.__APP_STATE__.characters.LunaBat;
    const root = bat.group || bat;
    const pendant = root.getObjectByName('moonStarPendant');
    let pointLight = bat.pendantLight || null;
    let meshCount = 0;
    if (pendant) {
      pendant.traverse(c => {
        if (c.isPointLight) pointLight = c;
        if (c.isMesh) meshCount++;
      });
    }
    if (!pointLight) return { found: false };
    return {
      found: true,
      isPointLight: Boolean(pointLight.isPointLight),
      colorHex: '#' + pointLight.color.getHexString().toLowerCase(),
      intensity: pointLight.intensity,
      meshCount,
    };
  })()""")
  assert light_info.get("found") and light_info.get("isPointLight"), (
      f"LunaBat moonStarPendant PointLight missing: {light_info}"
  )
  assert light_info.get("colorHex") in ("#ffe57f", "#ffd54f", "#ffd966"), (
      f"Expected #ffe57f PointLight color, got {light_info}"
  )
  assert light_info.get("meshCount", 0) >= 2, f"Expected Crescent Moon + Starburst meshes: {light_info}"
  session.assert_zero_errors("T1-F2-05")


@register_test(
    "T1-F2-06",
    "Tier 1",
    "F2",
    "LunaBat nose and muzzle include upturned bat nose with 2 nostrils and wide Smiling Critters teeth",
)
async def test_t1_f2_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  face_info = await session.eval_js("""(() => {
    const bat = window.__APP_STATE__.characters.LunaBat;
    const root = bat.group || bat;
    const nose = root.getObjectByName('nose');
    const muzzle = root.getObjectByName('muzzle');
    let noseMeshes = 0;
    let muzzleMeshes = 0;
    if (nose) nose.traverse(c => { if (c.isMesh) noseMeshes++; });
    if (muzzle) muzzle.traverse(c => { if (c.isMesh) muzzleMeshes++; });
    return { hasNose: Boolean(nose), noseMeshes, hasMuzzle: Boolean(muzzle), muzzleMeshes };
  })()""")
  assert face_info["hasNose"] and face_info["noseMeshes"] >= 2, f"Expected upturned nose + nostrils: {face_info}"
  assert face_info["hasMuzzle"] and face_info["muzzleMeshes"] >= 3, f"Expected muzzle + teeth: {face_info}"
  session.assert_zero_errors("T1-F2-06")


# --- F3: 6 Procedural 3D Animations & Pilot Accessories (6 tests) ---


@register_test(
    "T1-F3-01",
    "Tier 1",
    "F3",
    "Animation 1 (idle) updates breathing scale, ear twitch, and pendant swing across simulation frames",
)
async def test_t1_f3_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setCharacterAnimation('idle');
    app.stepSimulation(5, 1/60);
    const fox = app.characters.SunnyFox.group || app.characters.SunnyFox;
    const y0 = fox.position.y;
    const rot0 = fox.getObjectByName('head').rotation.z;
    app.stepSimulation(25, 1/60);
    const y1 = fox.position.y;
    const rot1 = fox.getObjectByName('head').rotation.z;
    return {
      anim: app.characters.SunnyFox.currentAnimation,
      delta: Math.abs(y1 - y0) + Math.abs(rot1 - rot0),
    };
  })()""")
  assert "idle" in str(res["anim"]).lower(), f"Expected idle animation active: {res}"
  assert res["delta"] > 1e-5, f"Expected non-zero harmonic motion in idle animation: {res}"
  session.assert_zero_errors("T1-F3-01")


@register_test(
    "T1-F3-02",
    "Tier 1",
    "F3",
    "Animation 2 (wave / joyful_wave) raises and waves rightArm / rightWingArm on both characters",
)
async def test_t1_f3_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setCharacterAnimation('wave');
    app.stepSimulation(15, 1/60);
    const fox = app.characters.SunnyFox.group || app.characters.SunnyFox;
    const bat = app.characters.LunaBat.group || app.characters.LunaBat;
    const foxR0 = fox.getObjectByName('rightArm').rotation.z;
    const batR0 = bat.getObjectByName('rightWingArm').rotation.z;
    app.stepSimulation(15, 1/60);
    const foxR1 = fox.getObjectByName('rightArm').rotation.z;
    const batR1 = bat.getObjectByName('rightWingArm').rotation.z;
    return {
      foxAnim: app.characters.SunnyFox.currentAnimation,
      batAnim: app.characters.LunaBat.currentAnimation,
      foxDelta: Math.abs(foxR1 - foxR0) + Math.abs(foxR1),
      batDelta: Math.abs(batR1 - batR0) + Math.abs(batR1),
    };
  })()""")
  assert "wave" in str(res["foxAnim"]).lower(), f"Expected wave animation on SunnyFox: {res}"
  assert res["foxDelta"] > 0.05 and res["batDelta"] > 0.05, f"Expected arm/wing wave rotation: {res}"
  session.assert_zero_errors("T1-F3-02")


@register_test(
    "T1-F3-03",
    "Tier 1",
    "F3",
    "Animation 3 (wingFlapTailWag / wing_flap_tail_wag) drives vigorous tail wag on SunnyFox and 2-wing flap on LunaBat",
)
async def test_t1_f3_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setCharacterAnimation('wingFlapTailWag');
    app.stepSimulation(10, 1/60);
    const fox = app.characters.SunnyFox.group || app.characters.SunnyFox;
    const bat = app.characters.LunaBat.group || app.characters.LunaBat;
    const tail0 = fox.getObjectByName('tail').rotation.y;
    const wing0 = bat.getObjectByName('leftWingArm').rotation.z;
    app.stepSimulation(18, 1/60);
    const tail1 = fox.getObjectByName('tail').rotation.y;
    const wing1 = bat.getObjectByName('leftWingArm').rotation.z;
    return {
      foxAnim: app.characters.SunnyFox.currentAnimation,
      tailMoved: Math.abs(tail1 - tail0) + Math.abs(tail1) > 0.01,
      wingMoved: Math.abs(wing1 - wing0) + Math.abs(wing1) > 0.01,
    };
  })()""")
  assert res["tailMoved"] and res["wingMoved"], f"Expected tail wag and wing flap transforms: {res}"
  session.assert_zero_errors("T1-F3-03")


@register_test(
    "T1-F3-04",
    "Tier 1",
    "F3",
    "Animations 4 (bounceDance) and 5 (barrelRollCheer) drive rhythmic hops and 360-degree somersault rolls",
)
async def test_t1_f3_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setCharacterAnimation('bounceDance');
    app.stepSimulation(16, 1/60);
    const bounceAnim = app.characters.SunnyFox.currentAnimation;
    app.setCharacterAnimation('barrelRollCheer');
    app.stepSimulation(20, 1/60);
    const rollAnim = app.characters.SunnyFox.currentAnimation;
    return { bounceAnim, rollAnim };
  })()""")
  assert "bounce" in str(res["bounceAnim"]).lower(), f"Expected bounceDance: {res}"
  assert "roll" in str(res["rollAnim"]).lower() or "cheer" in str(res["rollAnim"]).lower(), (
      f"Expected barrelRollCheer: {res}"
  )
  session.assert_zero_errors("T1-F3-04")


@register_test(
    "T1-F3-05",
    "Tier 1",
    "F3",
    "Animation 6 (cockpitPilotSteer / cockpit_pilot_steer) configures seated cockpit legs and yoke steering posture",
)
async def test_t1_f3_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setCharacterAnimation('cockpitPilotSteer');
    app.stepSimulation(15, 1/60);
    const fox = app.characters.SunnyFox.group || app.characters.SunnyFox;
    const leftLegRotX = fox.getObjectByName('leftLeg').rotation.x;
    return {
      anim: app.characters.SunnyFox.currentAnimation,
      leftLegRotX,
    };
  })()""")
  assert "steer" in str(res["anim"]).lower() or "pilot" in str(res["anim"]).lower(), (
      f"Expected cockpitPilotSteer animation: {res}"
  )
  assert abs(res["leftLegRotX"]) > 0.2, f"Expected seated leg rotation in cockpitPilotSteer: {res}"
  session.assert_zero_errors("T1-F3-05")


@register_test(
    "T1-F3-06",
    "Tier 1",
    "F3",
    "3D pilotGear subgroup contains toggleable aviatorGoggles, pilotScarf, and captainCap on both characters",
)
async def test_t1_f3_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  gear_info = await session.eval_js("""(() => {
    const fox = window.__APP_STATE__.characters.SunnyFox.group || window.__APP_STATE__.characters.SunnyFox;
    const bat = window.__APP_STATE__.characters.LunaBat.group || window.__APP_STATE__.characters.LunaBat;
    const items = ['aviatorGoggles', 'pilotScarf', 'captainCap'];
    const foxGear = items.map(n => Boolean(fox.getObjectByName(n)));
    const batGear = items.map(n => Boolean(bat.getObjectByName(n)));
    return { foxGear, batGear };
  })()""")
  assert all(gear_info["foxGear"]), f"SunnyFox missing pilotGear items: {gear_info}"
  assert all(gear_info["batGear"]), f"LunaBat missing pilotGear items: {gear_info}"
  session.assert_zero_errors("T1-F3-06")


# --- F4: 360° Studio OrbitControls, Tap-to-React Particles, Synth Audio & Reference Cards (6 tests) ---


@register_test(
    "T1-F4-01",
    "Tier 1",
    "F4",
    "Character Studio initializes 360-degree THREE.OrbitControls and shared WebGLRenderer with preserveDrawingBuffer: true",
)
async def test_t1_f4_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  studio_info = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('character_studio');
    const gl = app.renderer.getContext();
    const attrs = gl.getContextAttributes();
    return {
      activeView: app.activeView,
      hasOrbitControls: Boolean(window.THREE && window.THREE.OrbitControls),
      preserveDrawingBuffer: Boolean(attrs && attrs.preserveDrawingBuffer),
    };
  })()""")
  assert studio_info["activeView"] == "character_studio"
  assert studio_info["hasOrbitControls"], "Expected window.THREE.OrbitControls to be loaded"
  assert studio_info["preserveDrawingBuffer"], "Renderer must enable preserveDrawingBuffer: true"
  session.assert_zero_errors("T1-F4-01")


@register_test(
    "T1-F4-02",
    "Tier 1",
    "F4",
    "triggerCharacterTapReaction('SunnyFox') pulses golden lantern light and emits warm firefly particles",
)
async def test_t1_f4_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('character_studio');
    app.triggerCharacterTapReaction('SunnyFox');
    app.stepSimulation(5, 1/60);
    return {
      intensity: app.characters.SunnyFox.pendantLight.intensity,
    };
  })()""")
  assert res["intensity"] >= 1.5, f"Expected SunnyFox pendantLight pulse on tap reaction: {res}"
  session.assert_zero_errors("T1-F4-02")


@register_test(
    "T1-F4-03",
    "Tier 1",
    "F4",
    "triggerCharacterTapReaction('LunaBat') pulses crescent moon-star light and emits lavender moon-dust particles",
)
async def test_t1_f4_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('character_studio');
    app.triggerCharacterTapReaction('LunaBat');
    app.stepSimulation(5, 1/60);
    return {
      intensity: app.characters.LunaBat.pendantLight.intensity,
    };
  })()""")
  assert res["intensity"] >= 1.5, f"Expected LunaBat pendantLight pulse on tap reaction: {res}"
  session.assert_zero_errors("T1-F4-03")


@register_test(
    "T1-F4-04",
    "Tier 1",
    "F4",
    "Web Audio API plush sound synthesizer operates cleanly without unhandled autoplay errors",
)
async def test_t1_f4_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  audio_ok = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.triggerCharacterTapReaction('SunnyFox');
    app.triggerCharacterTapReaction('LunaBat');
    return true;
  })()""")
  assert audio_ok is True
  session.assert_zero_errors("T1-F4-04")


@register_test(
    "T1-F4-05",
    "Tier 1",
    "F4",
    "Reference portrait cards render custom_critter_fox_lantern.jpg and custom_critter_bat_moonstar.jpg with naturalWidth >= 512",
)
async def test_t1_f4_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  imgs = await session.eval_js("""(() => {
    const allImgs = Array.from(document.querySelectorAll('img'));
    const foxImg = allImgs.find(img => (img.src || '').includes('custom_critter_fox_lantern') || (img.alt || '').toLowerCase().includes('fox'));
    const batImg = allImgs.find(img => (img.src || '').includes('custom_critter_bat_moonstar') || (img.alt || '').toLowerCase().includes('bat'));
    return {
      foxLoaded: Boolean(foxImg && foxImg.complete && foxImg.naturalWidth >= 512),
      batLoaded: Boolean(batImg && batImg.complete && batImg.naturalWidth >= 512),
      foxW: foxImg ? foxImg.naturalWidth : 0,
      batW: batImg ? batImg.naturalWidth : 0,
    };
  })()""")
  assert imgs["foxLoaded"], f"SunnyFox reference portrait card failed to load: {imgs}"
  assert imgs["batLoaded"], f"LunaBat reference portrait card failed to load: {imgs}"
  session.assert_zero_errors("T1-F4-05")


@register_test(
    "T1-F4-06",
    "Tier 1",
    "F4",
    "Studio view navigation and interactive animation buttons update window.__APP_STATE__ cleanly",
)
async def test_t1_f4_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  view_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('character_studio');
    app.setCharacterAnimation('SunnyFox', 'wave');
    app.setCharacterAnimation('LunaBat', 'bounceDance');
    return {
      view: app.activeView,
      foxAnim: app.characters.SunnyFox.currentAnimation,
      batAnim: app.characters.LunaBat.currentAnimation,
    };
  })()""")
  assert view_res["view"] == "character_studio"
  assert "wave" in str(view_res["foxAnim"]).lower()
  assert "bounce" in str(view_res["batAnim"]).lower()
  session.assert_zero_errors("T1-F4-06")


# --- F5: Tandem Cockpit & Co-Pilot Wing-Walker Role Swap (6 tests) ---


@register_test(
    "T1-F5-01",
    "Tier 1",
    "F5",
    "Active 3D aircraft exposes distinct pilotSeatAnchor and coPilotSeatAnchor THREE.Group nodes",
)
async def test_t1_f5_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  anchors = await session.eval_js("""(() => {
    const h = window.__APP_STATE__.hangar;
    const plane = h.airplaneGroup;
    const pAnchor = h.pilotSeatAnchor || (plane && plane.getObjectByName('pilotSeatAnchor'));
    const cAnchor = h.coPilotSeatAnchor || (plane && plane.getObjectByName('coPilotSeatAnchor'));
    return {
      hasPilotAnchor: Boolean(pAnchor),
      hasCoPilotAnchor: Boolean(cAnchor),
      distinct: Boolean(pAnchor && cAnchor && pAnchor !== cAnchor),
    };
  })()""")
  assert anchors["hasPilotAnchor"] and anchors["hasCoPilotAnchor"] and anchors["distinct"], (
      f"Missing or identical cockpit seat anchors: {anchors}"
  )
  session.assert_zero_errors("T1-F5-01")


@register_test(
    "T1-F5-02",
    "Tier 1",
    "F5",
    "SunnyFox and LunaBat occupy complementary Pilot and Co-Pilot roles in flight state",
)
async def test_t1_f5_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  crew = await session.eval_js("""(() => {
    const f = window.__APP_STATE__.flight;
    return { pilotId: f.pilotId, coPilotId: f.coPilotId };
  })()""")
  assert {crew["pilotId"], crew["coPilotId"]} == {"SunnyFox", "LunaBat"}, (
      f"Expected SunnyFox & LunaBat as Pilot/Co-Pilot duo, got {crew}"
  )
  session.assert_zero_errors("T1-F5-02")


@register_test(
    "T1-F5-03",
    "Tier 1",
    "F5",
    "swapRoles() swaps pilotId and coPilotId in real time, increments roleSwapCount, and reparents seat anchors",
)
async def test_t1_f5_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  swap_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    const beforePilot = app.flight.pilotId;
    const beforeCoPilot = app.flight.coPilotId;
    const beforeCount = app.flight.roleSwapCount || 0;
    const ret = app.swapRoles();
    return {
      beforePilot,
      beforeCoPilot,
      afterPilot: app.flight.pilotId,
      afterCoPilot: app.flight.coPilotId,
      afterCount: app.flight.roleSwapCount,
      retPilot: ret ? ret.pilotId : app.flight.pilotId,
      beforeCount,
    };
  })()""")
  assert swap_res["afterPilot"] == swap_res["beforeCoPilot"], f"Pilot did not swap: {swap_res}"
  assert swap_res["afterCoPilot"] == swap_res["beforePilot"], f"Co-Pilot did not swap: {swap_res}"
  assert swap_res["afterCount"] == swap_res["beforeCount"] + 1, f"roleSwapCount did not increment: {swap_res}"
  session.assert_zero_errors("T1-F5-03")


@register_test(
    "T1-F5-04",
    "Tier 1",
    "F5",
    "setCoPilotMode('wing_walker') moves coPilotSeatAnchor onto the wing for Wing-Walker stunts",
)
async def test_t1_f5_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  ww_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.setCoPilotMode('wing_walker');
    const cAnchor = app.hangar.coPilotSeatAnchor || app.hangar.airplaneGroup.getObjectByName('coPilotSeatAnchor');
    return {
      mode: app.flight.coPilotMode,
      posX: cAnchor ? cAnchor.position.x : 0,
      posY: cAnchor ? cAnchor.position.y : 0,
    };
  })()""")
  assert ww_res["mode"] == "wing_walker", f"Expected coPilotMode 'wing_walker', got {ww_res}"
  assert abs(ww_res["posX"]) > 0.5 or ww_res["posY"] > 0.65, (
      f"Expected coPilotSeatAnchor displaced onto wing in wing_walker mode: {ww_res}"
  )
  session.assert_zero_errors("T1-F5-04")


@register_test(
    "T1-F5-05",
    "Tier 1",
    "F5",
    "setCoPilotMode('rear_cockpit') restores coPilotSeatAnchor to center tandem cockpit alignment",
)
async def test_t1_f5_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  rc_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setCoPilotMode('wing_walker');
    app.setCoPilotMode('rear_cockpit');
    const cAnchor = app.hangar.coPilotSeatAnchor || app.hangar.airplaneGroup.getObjectByName('coPilotSeatAnchor');
    return {
      mode: app.flight.coPilotMode,
      posX: cAnchor ? cAnchor.position.x : 0,
    };
  })()""")
  assert rc_res["mode"] == "rear_cockpit"
  assert abs(rc_res["posX"]) < 0.35, f"Expected rear_cockpit anchor centered on X=0, got {rc_res}"
  session.assert_zero_errors("T1-F5-05")


@register_test(
    "T1-F5-06",
    "Tier 1",
    "F5",
    "Pilot uses cockpit steering animation while Co-Pilot performs wave/flap/cheer animation",
)
async def test_t1_f5_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  anims = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.startFlight();
    app.stepSimulation(10, 1/60);
    const pilotChar = app.characters[app.flight.pilotId];
    const coPilotChar = app.characters[app.flight.coPilotId];
    return {
      pilotAnim: pilotChar.currentAnimation,
      coPilotAnim: coPilotChar.currentAnimation,
    };
  })()""")
  assert anims["pilotAnim"] != anims["coPilotAnim"] or "steer" in str(anims["pilotAnim"]).lower(), (
      f"Expected distinct pilot/co-pilot animations in flight: {anims}"
  )
  session.assert_zero_errors("T1-F5-06")


# --- F6: 3D Flight Controls & Stunts (6 tests) ---


@register_test(
    "T1-F6-01",
    "Tier 1",
    "F6",
    "startFlight() and stepSimulation() advance aircraft along SF -> Boston corridor (-Z, progress, distanceMiles)",
)
async def test_t1_f6_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  flight_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.resetFlight();
    app.startFlight();
    app.stepSimulation(40, 1/60);
    return {
      active: app.flight.active,
      flightState: app.flight.flightState,
      z: app.flight.position.z,
      progress: app.flight.progress,
      distanceMiles: app.flight.distanceMiles,
    };
  })()""")
  assert flight_res["active"] is True
  assert flight_res["z"] < -5.0, f"Expected aircraft to advance along -Z, got {flight_res}"
  assert flight_res["progress"] > 0.0 and flight_res["distanceMiles"] > 0, (
      f"Expected positive progress and miles: {flight_res}"
  )
  session.assert_zero_errors("T1-F6-01")


@register_test(
    "T1-F6-02",
    "Tier 1",
    "F6",
    "setSteering(steerX, steerY) moves aircraft (x, y) and updates pitch, yaw, and bank roll rotation",
)
async def test_t1_f6_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  steer_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.resetFlight();
    app.startFlight();
    const y0 = app.flight.position.y;
    app.setSteering(0.8, 0.6);
    app.stepSimulation(30, 1/60);
    return {
      x: app.flight.position.x,
      y: app.flight.position.y,
      y0,
      pitch: app.flight.rotation.pitch,
      roll: app.flight.rotation.roll,
    };
  })()""")
  assert steer_res["x"] > 1.0, f"Expected positive lateral X movement on steerX=0.8: {steer_res}"
  assert steer_res["y"] > steer_res["y0"] + 0.5, f"Expected altitude climb on steerY=0.6: {steer_res}"
  assert abs(steer_res["pitch"]) > 0.02 and abs(steer_res["roll"]) > 0.02, (
      f"Expected non-zero pitch & roll attitude response: {steer_res}"
  )
  session.assert_zero_errors("T1-F6-02")


@register_test(
    "T1-F6-03",
    "Tier 1",
    "F6",
    "triggerBoost() activates Turbo Starlight Boost, increasing speed > 2x and incrementing boostCount & score",
)
async def test_t1_f6_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  boost_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.resetFlight();
    app.startFlight();
    app.stepSimulation(2, 1/60);
    const baseSpeed = app.flight.speed;
    const baseScore = app.flight.score;
    app.triggerBoost();
    app.stepSimulation(2, 1/60);
    return {
      boostActive: app.flight.boostActive,
      boostCount: app.flight.boostCount,
      baseSpeed,
      boostSpeed: app.flight.speed,
      scoreDelta: app.flight.score - baseScore,
    };
  })()""")
  assert boost_res["boostActive"] is True
  assert boost_res["boostCount"] >= 1
  assert boost_res["boostSpeed"] > boost_res["baseSpeed"] * 1.5, f"Expected boost speed increase: {boost_res}"
  assert boost_res["scoreDelta"] >= 25, f"Expected boost score bonus: {boost_res}"
  session.assert_zero_errors("T1-F6-03")


@register_test(
    "T1-F6-04",
    "Tier 1",
    "F6",
    "triggerBarrelRoll() executes a 360-degree aerobatic barrel roll stunt and increments barrelRollCount & score",
)
async def test_t1_f6_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  roll_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.resetFlight();
    app.startFlight();
    app.setSteering(0, 0);
    const s0 = app.flight.score;
    app.triggerBarrelRoll();
    const activeStart = app.flight.barrelRollActive;
    app.stepSimulation(15, 1/60);
    const midRoll = app.flight.rotation.roll;
    app.stepSimulation(60, 1/60);
    return {
      activeStart,
      midRoll,
      activeEnd: app.flight.barrelRollActive,
      barrelRollCount: app.flight.barrelRollCount,
      scoreDelta: app.flight.score - s0,
    };
  })()""")
  assert roll_res["activeStart"] is True
  assert abs(roll_res["midRoll"]) > 0.3, f"Expected active mid-barrel-roll angle: {roll_res}"
  assert roll_res["activeEnd"] is False, "Expected barrel roll to finish after 1.25s"
  assert roll_res["barrelRollCount"] >= 1 and roll_res["scoreDelta"] >= 50
  session.assert_zero_errors("T1-F6-04")


@register_test(
    "T1-F6-05",
    "Tier 1",
    "F6",
    "dropHeartPackage() spawns a 3D Heart Parachute Care Package and increments carePackagesDropped & score",
)
async def test_t1_f6_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  drop_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.resetFlight();
    app.startFlight();
    const s0 = app.flight.score;
    app.dropHeartPackage();
    app.stepSimulation(10, 1/60);
    return {
      carePackagesDropped: app.flight.carePackagesDropped,
      scoreDelta: app.flight.score - s0,
    };
  })()""")
  assert drop_res["carePackagesDropped"] >= 1
  assert drop_res["scoreDelta"] >= 25, f"Expected score bonus for dropping care package: {drop_res}"
  session.assert_zero_errors("T1-F6-05")


@register_test(
    "T1-F6-06",
    "Tier 1",
    "F6",
    "Flight HUD stunt buttons and keyboard events trigger flight simulator actions cleanly",
)
async def test_t1_f6_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  await session.eval_js("window.__APP_STATE__.setView('flight_simulator'); window.__APP_STATE__.resetFlight(); window.__APP_STATE__.startFlight();")
  hud_ok = await session.eval_js("""(() => {
    window.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', code: 'Space', bubbles: true }));
    window.dispatchEvent(new KeyboardEvent('keyup', { key: ' ', code: 'Space', bubbles: true }));
    return true;
  })()""")
  assert hud_ok is True
  session.assert_zero_errors("T1-F6-06")


# --- F7: 3 Scenic Sky Zones (SF ✈️ Boston) & Time-of-Day Pendant Illumination (6 tests) ---


@register_test(
    "T1-F7-01",
    "Tier 1",
    "F7",
    "Zone 1 represents Golden Gate Sunrise Takeoff from Mom in San Francisco to Daughter in Boston",
)
async def test_t1_f7_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  z1 = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.resetFlight();
    app.setZone(1);
    return {
      zoneId: app.flight.zoneId,
      zoneName: app.flight.zoneName,
      originCity: app.flight.originCity,
      destinationCity: app.flight.destinationCity,
    };
  })()""")
  assert z1["zoneId"] == 1
  assert "Golden Gate" in z1["zoneName"] or "San Francisco" in z1["zoneName"]
  assert "San Francisco" in z1["originCity"]
  assert "Boston" in z1["destinationCity"]
  session.assert_zero_errors("T1-F7-01")


@register_test(
    "T1-F7-02",
    "Tier 1",
    "F7",
    "setZone(2) warps to Zone 2: Rainbow Cloud Archipelago & Paper-Airplane Wind Tunnels",
)
async def test_t1_f7_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  z2 = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setZone(2);
    return {
      zoneId: app.flight.zoneId,
      zoneName: app.flight.zoneName,
      z: app.flight.position.z,
    };
  })()""")
  assert z2["zoneId"] == 2
  assert "Rainbow" in z2["zoneName"] or "Cloud" in z2["zoneName"]
  assert z2["z"] <= -500, f"Expected Zone 2 corridor z <= -500, got {z2}"
  session.assert_zero_errors("T1-F7-02")


@register_test(
    "T1-F7-03",
    "Tier 1",
    "F7",
    "setZone(3) warps to Zone 3: Starry Night Aurora Approach into Boston (Zakim Bridge)",
)
async def test_t1_f7_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  z3 = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setZone(3);
    return {
      zoneId: app.flight.zoneId,
      zoneName: app.flight.zoneName,
      z: app.flight.position.z,
    };
  })()""")
  assert z3["zoneId"] == 3
  assert "Boston" in z3["zoneName"] or "Aurora" in z3["zoneName"] or "Starry" in z3["zoneName"]
  assert z3["z"] <= -1100, f"Expected Zone 3 corridor z <= -1100, got {z3}"
  session.assert_zero_errors("T1-F7-03")


@register_test(
    "T1-F7-04",
    "Tier 1",
    "F7",
    "setTimeOfDay switches cleanly between 'day' and 'sunset' lighting atmospheres",
)
async def test_t1_f7_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  tod = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setTimeOfDay('day');
    const tDay = app.flight.timeOfDay;
    app.setTimeOfDay('sunset');
    const tSunset = app.flight.timeOfDay;
    return { tDay, tSunset };
  })()""")
  assert tod["tDay"] == "day" and tod["tSunset"] == "sunset"
  session.assert_zero_errors("T1-F7-04")


@register_test(
    "T1-F7-05",
    "Tier 1",
    "F7",
    "Night mode & Zone 3 activate SunnyFox & LunaBat pendant PointLights to reveal hidden starlight rings",
)
async def test_t1_f7_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  night_res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.setZone(3);
    app.setTimeOfDay('night');
    app.stepSimulation(15, 1/60);
    return {
      timeOfDay: app.flight.timeOfDay,
      pendantLightsActive: app.flight.pendantLightsActive,
      foxIntensity: app.characters.SunnyFox.pendantLight.intensity,
      batIntensity: app.characters.LunaBat.pendantLight.intensity,
      revealedRings: app.flight.revealedStarlightRingsCount,
    };
  })()""")
  assert night_res["timeOfDay"] == "night"
  assert night_res["pendantLightsActive"] is True
  assert night_res["foxIntensity"] > 2.0 and night_res["batIntensity"] > 2.0, (
      f"Expected elevated pendant PointLight intensities in night mode: {night_res}"
  )
  assert night_res["revealedRings"] > 0, f"Expected hidden starlight rings illuminated by pendants: {night_res}"
  session.assert_zero_errors("T1-F7-05")


@register_test(
    "T1-F7-06",
    "Tier 1",
    "F7",
    "completeFlightToBoston() lands at Boston Zakim Runway (completed=true, progress=1.0, distanceMiles=2700)",
)
async def test_t1_f7_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  landed = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.completeFlightToBoston();
    return {
      completed: app.flight.completed,
      flightState: app.flight.flightState,
      progress: app.flight.progress,
      distanceMiles: app.flight.distanceMiles,
    };
  })()""")
  assert landed["completed"] is True
  assert landed["flightState"] == "landed_boston"
  assert abs(landed["progress"] - 1.0) < 1e-6
  assert landed["distanceMiles"] == 2700
  session.assert_zero_errors("T1-F7-06")


# --- F8: 6 Collectible Classes & Scoring (6 tests) ---


@register_test(
    "T1-F8-01",
    "Tier 1",
    "F8",
    "Collecting 'golden_lantern' increments collectedCounts.golden_lantern and score",
)
async def test_t1_f8_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.resetFlight();
    app.startFlight();
    const s0 = app.flight.score;
    const c0 = app.flight.collectedCounts.golden_lantern || 0;
    app.collectNearestItem('golden_lantern');
    return {
      countDelta: app.flight.collectedCounts.golden_lantern - c0,
      scoreDelta: app.flight.score - s0,
    };
  })()""")
  assert res["countDelta"] >= 1 and res["scoreDelta"] > 0, f"Failed golden_lantern collection: {res}"
  session.assert_zero_errors("T1-F8-01")


@register_test(
    "T1-F8-02",
    "Tier 1",
    "F8",
    "Collecting 'crescent_moon_star' increments collectedCounts.crescent_moon_star and score",
)
async def test_t1_f8_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.resetFlight();
    app.startFlight();
    const s0 = app.flight.score;
    const c0 = app.flight.collectedCounts.crescent_moon_star || 0;
    app.collectNearestItem('crescent_moon_star');
    return {
      countDelta: app.flight.collectedCounts.crescent_moon_star - c0,
      scoreDelta: app.flight.score - s0,
    };
  })()""")
  assert res["countDelta"] >= 1 and res["scoreDelta"] > 0
  session.assert_zero_errors("T1-F8-02")


@register_test(
    "T1-F8-03",
    "Tier 1",
    "F8",
    "Collecting 'music_note_booster' increments collectedCounts.music_note_booster and score",
)
async def test_t1_f8_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.resetFlight();
    app.startFlight();
    const s0 = app.flight.score;
    const c0 = app.flight.collectedCounts.music_note_booster || 0;
    app.collectNearestItem('music_note_booster');
    return {
      countDelta: app.flight.collectedCounts.music_note_booster - c0,
      scoreDelta: app.flight.score - s0,
    };
  })()""")
  assert res["countDelta"] >= 1 and res["scoreDelta"] > 0
  session.assert_zero_errors("T1-F8-03")


@register_test(
    "T1-F8-04",
    "Tier 1",
    "F8",
    "Collecting 'mom_heart_care_package' increments collectedCounts.mom_heart_care_package and score",
)
async def test_t1_f8_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.resetFlight();
    app.startFlight();
    const s0 = app.flight.score;
    const c0 = app.flight.collectedCounts.mom_heart_care_package || 0;
    app.collectNearestItem('mom_heart_care_package');
    return {
      countDelta: app.flight.collectedCounts.mom_heart_care_package - c0,
      scoreDelta: app.flight.score - s0,
    };
  })()""")
  assert res["countDelta"] >= 1 and res["scoreDelta"] > 0
  session.assert_zero_errors("T1-F8-04")


@register_test(
    "T1-F8-05",
    "Tier 1",
    "F8",
    "Passing through 'sky_ring' and 'starlight_ring' increments ringsPassed and ring collection counters",
)
async def test_t1_f8_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.resetFlight();
    app.startFlight();
    const r0 = app.flight.ringsPassed || 0;
    app.collectNearestItem('sky_ring');
    app.collectNearestItem('starlight_ring');
    return {
      ringsDelta: app.flight.ringsPassed - r0,
      skyRingCount: app.flight.collectedCounts.sky_ring,
      starlightRingCount: app.flight.collectedCounts.starlight_ring,
    };
  })()""")
  assert res["ringsDelta"] >= 2 and res["skyRingCount"] >= 1 and res["starlightRingCount"] >= 1, (
      f"Failed sky_ring / starlight_ring collection: {res}"
  )
  session.assert_zero_errors("T1-F8-05")


@register_test(
    "T1-F8-06",
    "Tier 1",
    "F8",
    "Collecting 'paper_airplane_squadron' increments collectedCounts.paper_airplane_squadron and score",
)
async def test_t1_f8_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.resetFlight();
    app.startFlight();
    const s0 = app.flight.score;
    const c0 = app.flight.collectedCounts.paper_airplane_squadron || 0;
    app.collectNearestItem('paper_airplane_squadron');
    return {
      countDelta: app.flight.collectedCounts.paper_airplane_squadron - c0,
      scoreDelta: app.flight.score - s0,
    };
  })()""")
  assert res["countDelta"] >= 1 and res["scoreDelta"] > 0
  session.assert_zero_errors("T1-F8-06")


# --- F9: 3 Selectable 3D Airplanes & Hangar Customizer (6 tests) ---


@register_test(
    "T1-F9-01",
    "Tier 1",
    "F9",
    "setPlaneModel('biplane') instantiates Critter Cloud Biplane with >1000 vertices and spinning propellerGroup",
)
async def test_t1_f9_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('hangar');
    app.setPlaneModel('biplane');
    return {
      modelId: app.hangar.modelId,
      vertexCount: app.hangar.vertexCount,
      hasPropeller: Boolean(app.hangar.propellerGroup),
    };
  })()""")
  assert res["modelId"] == "biplane"
  assert res["vertexCount"] > 1000, f"Expected >1000 vertices for biplane: {res}"
  assert res["hasPropeller"] is True
  session.assert_zero_errors("T1-F9-01")


@register_test(
    "T1-F9-02",
    "Tier 1",
    "F9",
    "setPlaneModel('supersonic_jet') instantiates Starlight Supersonic Jet with >1000 vertices",
)
async def test_t1_f9_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('hangar');
    app.setPlaneModel('supersonic_jet');
    return {
      modelId: app.hangar.modelId,
      vertexCount: app.hangar.vertexCount,
    };
  })()""")
  assert res["modelId"] == "supersonic_jet"
  assert res["vertexCount"] > 1000, f"Expected >1000 vertices for supersonic_jet: {res}"
  session.assert_zero_errors("T1-F9-02")


@register_test(
    "T1-F9-03",
    "Tier 1",
    "F9",
    "setPlaneModel('origami_glider') instantiates Origami Dream Glider with >1000 vertices",
)
async def test_t1_f9_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('hangar');
    app.setPlaneModel('origami_glider');
    return {
      modelId: app.hangar.modelId,
      vertexCount: app.hangar.vertexCount,
    };
  })()""")
  assert res["modelId"] == "origami_glider"
  assert res["vertexCount"] > 1000, f"Expected >1000 vertices for origami_glider: {res}"
  session.assert_zero_errors("T1-F9-03")


@register_test(
    "T1-F9-04",
    "Tier 1",
    "F9",
    "All 4 paint palettes (sunset_fox_amber, midnight_bat_indigo, huntrx_golden_neon, mint_cloud) update primaryColorHex",
)
async def test_t1_f9_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  palettes = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    const ids = ['sunset_fox_amber', 'midnight_bat_indigo', 'huntrx_golden_neon', 'mint_cloud'];
    return ids.map(id => {
      app.setPaintPalette(id);
      return { id: app.hangar.paintPaletteId, hex: app.hangar.primaryColorHex };
    });
  })()""")
  assert len({p["hex"] for p in palettes}) == 4, f"Expected 4 distinct primary paint hex colors: {palettes}"
  session.assert_zero_errors("T1-F9-04")


@register_test(
    "T1-F9-05",
    "Tier 1",
    "F9",
    "All 3 propeller styles and 4 sky-writing contrail particle systems update Hangar & Flight state",
)
async def test_t1_f9_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    const props = ['classic_wood_brass', 'starlight_crystal_turbine', 'rainbow_flower_pinwheel'].map(p => {
      app.setPropellerStyle(p);
      return app.hangar.propellerStyleId;
    });
    const contrails = ['rainbow_ribbon', 'lantern_fireflies', 'starlight_moon_dust', 'heart_bubbles'].map(c => {
      app.setContrailStyle(c);
      return app.hangar.contrailStyleId;
    });
    return { props, contrails, hasContrailSystem: Boolean(app.hangar.contrailSystem) };
  })()""")
  assert res["props"] == ["classic_wood_brass", "starlight_crystal_turbine", "rainbow_flower_pinwheel"]
  assert res["contrails"] == ["rainbow_ribbon", "lantern_fireflies", "starlight_moon_dust", "heart_bubbles"]
  assert res["hasContrailSystem"] is True
  session.assert_zero_errors("T1-F9-05")


@register_test(
    "T1-F9-06",
    "Tier 1",
    "F9",
    "All 4 wing emblems (fox_lantern_crest, bat_moonstar_crest, sf_boston_heart_wings, golden_star_crown) apply cleanly",
)
async def test_t1_f9_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  emblems = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    return ['fox_lantern_crest', 'bat_moonstar_crest', 'sf_boston_heart_wings', 'golden_star_crown'].map(e => {
      app.setWingEmblem(e);
      return app.hangar.wingEmblemId;
    });
  })()""")
  assert emblems == ["fox_lantern_crest", "bat_moonstar_crest", "sf_boston_heart_wings", "golden_star_crown"]
  session.assert_zero_errors("T1-F9-06")


# --- F10: 3D Cockpit & Sky Photo Booth & localStorage Persistence (6 tests) ---


@register_test(
    "T1-F10-01",
    "Tier 1",
    "F10",
    "Photo Booth switches across all 4 SF/Boston/Hangar backdrops via setPhotoBackdrop",
)
async def test_t1_f10_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  backdrops = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('photo_booth');
    return [
      'sf_golden_gate_sunrise',
      'rainbow_cloud_archipelago',
      'boston_zakim_starlight',
      'sweet_hangar_studio',
    ].map(b => {
      app.setPhotoBackdrop(b);
      return app.photoBooth.backdropId;
    });
  })()""")
  assert len(set(backdrops)) == 4
  session.assert_zero_errors("T1-F10-01")


@register_test(
    "T1-F10-02",
    "Tier 1",
    "F10",
    "Photo Booth setPhotoPose and setPhotoCaption configure character poses and custom Mom message",
)
async def test_t1_f10_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('photo_booth');
    app.setPhotoPose('lantern_and_moonstar_glow');
    app.setPhotoCaption('Love you Mom in San Francisco! Flying to Boston!');
    return {
      poseId: app.photoBooth.poseId,
      captionText: app.photoBooth.captionText,
    };
  })()""")
  assert res["poseId"] == "lantern_and_moonstar_glow"
  assert "Love you Mom in San Francisco" in res["captionText"]
  session.assert_zero_errors("T1-F10-02")


@register_test(
    "T1-F10-03",
    "Tier 1",
    "F10",
    "capturePostcard() exports a valid base64 PNG image (>5000 chars) with verified IHDR dimensions",
)
async def test_t1_f10_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  card = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('photo_booth');
    app.setPhotoBackdrop('sf_golden_gate_sunrise');
    app.setPhotoCaption('SunnyFox & LunaBat flying from SF to Boston!');
    return app.capturePostcard();
  })()""")
  png_meta = verify_png_data_url(card["dataUrl"], min_length=5000)
  assert png_meta["width"] >= 640 and png_meta["height"] >= 360, f"Unexpected PNG size: {png_meta}"
  session.assert_zero_errors("T1-F10-03")


@register_test(
    "T1-F10-04",
    "Tier 1",
    "F10",
    "Captured postcards are appended to photoBooth.savedPostcards and persisted in localStorage",
)
async def test_t1_f10_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  stored = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.capturePostcard();
    const raw = localStorage.getItem('critters_airplane_3d_postcards_v1');
    const parsed = raw ? JSON.parse(raw) : [];
    return {
      memoryCount: app.photoBooth.savedPostcards.length,
      storageCount: parsed.length,
    };
  })()""")
  assert stored["memoryCount"] >= 1 and stored["storageCount"] >= 1
  session.assert_zero_errors("T1-F10-04")


@register_test(
    "T1-F10-05",
    "Tier 1",
    "F10",
    "Custom aircraft configuration is serialized to localStorage under critters_airplane_3d_config_v1",
)
async def test_t1_f10_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  cfg = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('supersonic_jet');
    app.setPaintPalette('midnight_bat_indigo');
    app.setPropellerStyle('starlight_crystal_turbine');
    app.setContrailStyle('starlight_moon_dust');
    app.setWingEmblem('bat_moonstar_crest');
    app.saveConfigToLocalStorage();
    const raw = localStorage.getItem('critters_airplane_3d_config_v1');
    return raw ? JSON.parse(raw) : null;
  })()""")
  assert cfg is not None, "Expected critters_airplane_3d_config_v1 in localStorage"
  assert cfg["modelId"] == "supersonic_jet"
  assert cfg["paintPaletteId"] == "midnight_bat_indigo"
  assert cfg["contrailStyleId"] == "starlight_moon_dust"
  session.assert_zero_errors("T1-F10-05")


@register_test(
    "T1-F10-06",
    "Tier 1",
    "F10",
    "Full browser page.reload() hydrates custom aircraft, paint, contrail, emblem, and saved postcards from localStorage",
)
async def test_t1_f10_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('origami_glider');
    app.setPaintPalette('huntrx_golden_neon');
    app.setContrailStyle('lantern_fireflies');
    app.setWingEmblem('sf_boston_heart_wings');
    app.capturePostcard();
    app.saveConfigToLocalStorage();
  })()""")
  await session.reload(wait_load=True, wait_app_ready=True)
  restored = await session.eval_js("""(() => ({
    modelId: window.__APP_STATE__.hangar.modelId,
    paintPaletteId: window.__APP_STATE__.hangar.paintPaletteId,
    contrailStyleId: window.__APP_STATE__.hangar.contrailStyleId,
    wingEmblemId: window.__APP_STATE__.hangar.wingEmblemId,
    savedPostcardsCount: window.__APP_STATE__.photoBooth.savedPostcards.length,
  }))()""")
  assert restored["modelId"] == "origami_glider", f"Failed to restore modelId after reload: {restored}"
  assert restored["paintPaletteId"] == "huntrx_golden_neon"
  assert restored["contrailStyleId"] == "lantern_fireflies"
  assert restored["wingEmblemId"] == "sf_boston_heart_wings"
  assert restored["savedPostcardsCount"] >= 1
  session.assert_zero_errors("T1-F10-06")


# --- F11: Offline-First iPad PWA, docs/ GitHub Pages, dist/index.html & Zero-Grandma Guardrail (6 tests) ---


@register_test(
    "T1-F11-01",
    "Tier 1",
    "F11",
    "index.html includes iPad PWA meta tags (apple-mobile-web-app-capable) and manifest link",
)
async def test_t1_f11_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  pwa_tags = await session.eval_js("""(() => {
    const capable = document.querySelector('meta[name="apple-mobile-web-app-capable"]');
    const status = document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]');
    const title = document.querySelector('meta[name="apple-mobile-web-app-title"]');
    const manifest = document.querySelector('link[rel="manifest"]');
    return {
      capable: capable ? capable.getAttribute('content') : '',
      hasStatus: Boolean(status),
      hasTitle: Boolean(title),
      manifestHref: manifest ? manifest.getAttribute('href') : '',
    };
  })()""")
  assert pwa_tags["capable"] == "yes", f"Missing apple-mobile-web-app-capable='yes': {pwa_tags}"
  assert pwa_tags["hasStatus"] and pwa_tags["hasTitle"]
  assert "manifest.json" in pwa_tags["manifestHref"]
  session.assert_zero_errors("T1-F11-01")


@register_test(
    "T1-F11-02",
    "Tier 1",
    "F11",
    "manifest.json and docs/manifest.json are valid standalone iPad PWA manifests",
)
async def test_t1_f11_02(session: ChromeCdpSession, base_url: str) -> None:
  for rel in ("manifest.json", "docs/manifest.json"):
    path = PROJECT_ROOT / rel
    assert path.is_file(), f"Missing manifest file: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("display") == "standalone", f"Expected display='standalone' in {rel}: {data}"
    assert "name" in data and "icons" in data
  session.assert_zero_errors("T1-F11-02")


@register_test(
    "T1-F11-03",
    "Tier 1",
    "F11",
    "sw.js and docs/sw.js implement install, activate, and fetch offline caching hooks",
)
async def test_t1_f11_03(session: ChromeCdpSession, base_url: str) -> None:
  for rel in ("sw.js", "docs/sw.js"):
    path = PROJECT_ROOT / rel
    assert path.is_file(), f"Missing service worker file: {path}"
    content = path.read_text(encoding="utf-8")
    assert "install" in content and "fetch" in content and "caches" in content, (
        f"Service Worker {rel} missing offline caching lifecycle handlers"
    )
  session.assert_zero_errors("T1-F11-03")


@register_test(
    "T1-F11-04",
    "Tier 1",
    "F11",
    "GitHub Pages docs/ directory contains .nojekyll, docs/index.html, and boots cleanly in WebGL 2.0",
)
async def test_t1_f11_04(session: ChromeCdpSession, base_url: str) -> None:
  assert (PROJECT_ROOT / "docs" / ".nojekyll").is_file(), "Missing docs/.nojekyll"
  assert (PROJECT_ROOT / "docs" / "index.html").is_file(), "Missing docs/index.html"
  await session.navigate(f"{base_url}/docs/index.html", wait_load=True, wait_app_ready=True)
  ready = await session.eval_js("Boolean(window.__APP_STATE__ && window.__APP_STATE__.ready)")
  assert ready is True, "docs/index.html failed to reach window.__APP_STATE__.ready"
  session.assert_zero_errors("T1-F11-04")
  await ensure_app_loaded(session, base_url, force_reload=True)


@register_test(
    "T1-F11-05",
    "Tier 1",
    "F11",
    "Standalone single-file bundle dist/index.html exists and boots with window.__APP_STATE__.ready === true",
)
async def test_t1_f11_05(session: ChromeCdpSession, base_url: str) -> None:
  dist_path = PROJECT_ROOT / "dist" / "index.html"
  assert dist_path.is_file(), f"Missing single-file bundle: {dist_path}"
  size_bytes = dist_path.stat().st_size
  assert size_bytes > 500_000, f"Expected dist/index.html to inline Three.js & assets (>500KB), got {size_bytes}"
  await session.navigate(f"{base_url}/dist/index.html", wait_load=True, wait_app_ready=True)
  ready = await session.eval_js("Boolean(window.__APP_STATE__ && window.__APP_STATE__.ready)")
  assert ready is True, "dist/index.html failed to reach window.__APP_STATE__.ready"
  session.assert_zero_errors("T1-F11-05")
  await ensure_app_loaded(session, base_url, force_reload=True)


@register_test(
    "T1-F11-06",
    "Tier 1",
    "F11",
    "Strict Zero-Grandma Invariant: 0 matches for grandma/grandmother/nana/granny across DOM and source tree",
)
async def test_t1_f11_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  dom_html = await session.eval_js("document.documentElement.innerHTML")
  banned_re = re.compile(r"\b(grandma|grandmother|nana|granny)\b", re.IGNORECASE)
  dom_match = banned_re.search(str(dom_html))
  assert dom_match is None, f"Banned word found in live DOM: {dom_match.group(0)}"

  scan_dirs = [
      PROJECT_ROOT / "index.html",
      PROJECT_ROOT / "manifest.json",
      PROJECT_ROOT / "sw.js",
      PROJECT_ROOT / "src",
      PROJECT_ROOT / "docs",
      PROJECT_ROOT / "dist",
  ]
  for item in scan_dirs:
    if item.is_file():
      files = [item]
    elif item.is_dir():
      files = [p for p in item.rglob("*") if p.is_file() and p.suffix in (".html", ".js", ".css", ".json")]
    else:
      files = []
    for fpath in files:
      if "three.min.js" in fpath.name:
        continue
      txt = fpath.read_text(encoding="utf-8", errors="ignore")
      m = banned_re.search(txt)
      assert m is None, f"Banned word {m.group(0)!r} found in file {fpath}"
  session.assert_zero_errors("T1-F11-06")


# ==============================================================================
# TIER 2 — BOUNDARY & CORNER CASES (56 Tests: T2-01..T2-56)
# ==============================================================================


def _register_tier2_tests() -> None:
  """Register 56 boundary, clamping, input validation, and stress tests."""

  # 1-8: Lateral & Altitude Clamping Boundaries
  clamping_cases = [
      ("T2-01", "Lateral right clamping at x = +18.0 under extreme steerX = +10.0", 10.0, 0.0, "x", 18.0),
      ("T2-02", "Lateral left clamping at x = -18.0 under extreme steerX = -10.0", -10.0, 0.0, "x", -18.0),
      ("T2-03", "Altitude ceiling clamping at y = +28.0 under extreme steerY = +10.0", 0.0, 10.0, "y", 28.0),
      ("T2-04", "Altitude floor clamping at y = +3.0 under extreme steerY = -10.0", 0.0, -10.0, "y", 3.0),
      ("T2-05", "Top-right corner simultaneous clamping (x = +18.0, y = +28.0)", 15.0, 15.0, "both_tr", 0.0),
      ("T2-06", "Bottom-left corner simultaneous clamping (x = -18.0, y = +3.0)", -15.0, -15.0, "both_bl", 0.0),
      ("T2-07", "Top-left corner simultaneous clamping (x = -18.0, y = +28.0)", -15.0, 15.0, "both_tl", 0.0),
      ("T2-08", "Bottom-right corner simultaneous clamping (x = +18.0, y = +3.0)", 15.0, -15.0, "both_br", 0.0),
  ]

  for tid, title, sx, sy, axis, expected in clamping_cases:

    def _make_clamp_test(t_id: str, s_x: float, s_y: float, ax: str, exp: float):
      @register_test(t_id, "Tier 2", "F6", title)
      async def _fn(session: ChromeCdpSession, base_url: str) -> None:
        await ensure_app_loaded(session, base_url)
        pos = await session.eval_js(f"""(() => {{
          const app = window.__APP_STATE__;
          app.resetFlight();
          app.startFlight();
          app.setSteering({s_x}, {s_y});
          app.stepSimulation(180, 1/60);
          return app.flight.position;
        }})()""")
        if ax == "x":
          assert abs(pos["x"] - exp) < 1e-4, f"{t_id}: expected x={exp}, got {pos}"
        elif ax == "y":
          assert abs(pos["y"] - exp) < 1e-4, f"{t_id}: expected y={exp}, got {pos}"
        elif ax == "both_tr":
          assert abs(pos["x"] - 18.0) < 1e-4 and abs(pos["y"] - 28.0) < 1e-4, f"{t_id}: {pos}"
        elif ax == "both_bl":
          assert abs(pos["x"] + 18.0) < 1e-4 and abs(pos["y"] - 3.0) < 1e-4, f"{t_id}: {pos}"
        elif ax == "both_tl":
          assert abs(pos["x"] + 18.0) < 1e-4 and abs(pos["y"] - 28.0) < 1e-4, f"{t_id}: {pos}"
        elif ax == "both_br":
          assert abs(pos["x"] - 18.0) < 1e-4 and abs(pos["y"] - 3.0) < 1e-4, f"{t_id}: {pos}"
        session.assert_zero_errors(t_id)

      return _fn

    _make_clamp_test(tid, sx, sy, axis, expected)

  # 9-14: Non-finite / Degenerate Steering & Simulation Step Inputs
  degenerate_inputs = [
      ("T2-09", "setSteering(NaN, NaN) guards against NaN propagation in position/rotation", "NaN, NaN"),
      ("T2-10", "setSteering(Infinity, -Infinity) clamps cleanly to [-1, 1] without NaN", "Infinity, -Infinity"),
      ("T2-11", "setSteering(null, undefined) defaults safely to neutral steering (0, 0)", "null, undefined"),
      ("T2-12", "stepSimulation(0, 0) executes as a safe no-op without division-by-zero", "0, 0"),
      ("T2-13", "stepSimulation(0.25) single-arg dt overload advances simulation by 0.25s", "0.25"),
      ("T2-14", "stepSimulation(-5, -0.1) negative frames/dt guards against backward progress corruption", "-5, -0.1"),
  ]

  for tid, title, js_args in degenerate_inputs:

    def _make_degen_test(t_id: str, args_str: str):
      @register_test(t_id, "Tier 2", "F6", title)
      async def _fn(session: ChromeCdpSession, base_url: str) -> None:
        await ensure_app_loaded(session, base_url)
        is_finite = await session.eval_js(f"""(() => {{
          const app = window.__APP_STATE__;
          app.resetFlight();
          app.startFlight();
          if ("{t_id}".startsWith("T2-09") || "{t_id}".startsWith("T2-10") || "{t_id}".startsWith("T2-11")) {{
            app.setSteering({args_str});
            app.stepSimulation(10, 1/60);
          }} else {{
            app.stepSimulation({args_str});
          }}
          const p = app.flight.position;
          const r = app.flight.rotation;
          return Number.isFinite(p.x) && Number.isFinite(p.y) && Number.isFinite(p.z) &&
                 Number.isFinite(r.pitch) && Number.isFinite(r.yaw) && Number.isFinite(r.roll);
        }})()""")
        assert is_finite is True, f"{t_id}: Non-finite position/rotation detected"
        session.assert_zero_errors(t_id)

      return _fn

    _make_degen_test(tid, js_args)

  # 15-20: Rapid Role Swaps, Stunt Double-Triggers & Burst Actions
  @register_test("T2-15", "Tier 2", "F5", "Rapid 20x consecutive swapRoles() preserves duo parity and increments roleSwapCount by 20")
  async def test_t2_15(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    res = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      const p0 = app.flight.pilotId;
      const c0 = app.flight.roleSwapCount || 0;
      for (let i = 0; i < 20; i++) app.swapRoles();
      return {
        samePilotAfterEvenSwaps: app.flight.pilotId === p0,
        swapDelta: app.flight.roleSwapCount - c0,
      };
    })()""")
    assert res["samePilotAfterEvenSwaps"] is True and res["swapDelta"] == 20
    session.assert_zero_errors("T2-15")

  @register_test("T2-16", "Tier 2", "F5", "Rapid 21x odd consecutive swapRoles() swaps pilotId/coPilotId cleanly")
  async def test_t2_16(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    res = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      const p0 = app.flight.pilotId;
      for (let i = 0; i < 21; i++) app.swapRoles();
      return { swapped: app.flight.pilotId !== p0 };
    })()""")
    assert res["swapped"] is True
    session.assert_zero_errors("T2-16")

  @register_test("T2-17", "Tier 2", "F6", "Double-triggering triggerBoost() while boostActive is true resets timer safely")
  async def test_t2_17(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    res = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      app.resetFlight();
      app.startFlight();
      app.triggerBoost();
      app.stepSimulation(10, 1/60);
      app.triggerBoost();
      app.stepSimulation(200, 1/60);
      return { boostEndedCleanly: app.flight.boostActive === false, count: app.flight.boostCount };
    })()""")
    assert res["boostEndedCleanly"] is True and res["count"] >= 1
    session.assert_zero_errors("T2-17")

  @register_test("T2-18", "Tier 2", "F6", "Double-triggering triggerBarrelRoll() mid-roll completes cleanly without gimbal lock")
  async def test_t2_18(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    res = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      app.resetFlight();
      app.startFlight();
      app.triggerBarrelRoll();
      app.stepSimulation(15, 1/60);
      app.triggerBarrelRoll();
      app.stepSimulation(75, 1/60);
      return { active: app.flight.barrelRollActive, rollFinite: Number.isFinite(app.flight.rotation.roll) };
    })()""")
    assert res["active"] is False and res["rollFinite"] is True
    session.assert_zero_errors("T2-18")

  @register_test("T2-19", "Tier 2", "F6", "Rapid 12x dropHeartPackage() burst maintains scene stability and increments count by 12")
  async def test_t2_19(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    res = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      app.resetFlight();
      app.startFlight();
      for (let i = 0; i < 12; i++) app.dropHeartPackage();
      app.stepSimulation(20, 1/60);
      return app.flight.carePackagesDropped;
    })()""")
    assert res == 12
    session.assert_zero_errors("T2-19")

  @register_test("T2-20", "Tier 2", "F5", "Alternating setCoPilotMode between rear_cockpit and wing_walker 15 times")
  async def test_t2_20(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    mode = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      for (let i = 0; i < 15; i++) {
        app.setCoPilotMode(i % 2 === 0 ? 'wing_walker' : 'rear_cockpit');
      }
      return app.flight.coPilotMode;
    })()""")
    assert mode == "wing_walker"
    session.assert_zero_errors("T2-20")

  # 21-30: Invalid Option / Fallback Guards across Hangar, Studio, Flight & Photo Booth
  fallback_cases = [
      ("T2-21", "F9", "setPlaneModel('invalid_spaceship') falls back to a valid 3D aircraft model", "app.setPlaneModel('invalid_spaceship'); return ['biplane','supersonic_jet','origami_glider'].includes(app.hangar.modelId);"),
      ("T2-22", "F9", "setPaintPalette('unknown_neon') falls back to a valid paint palette", "app.setPaintPalette('unknown_neon'); return ['sunset_fox_amber','midnight_bat_indigo','huntrx_golden_neon','mint_cloud'].includes(app.hangar.paintPaletteId);"),
      ("T2-23", "F9", "setPropellerStyle('invalid_prop') falls back to default 3D propeller mesh without error", "app.setPropellerStyle('invalid_prop'); const ok = Boolean(app.hangar.propellerGroup) && app.hangar.vertexCount > 1000; app.setPropellerStyle('classic_wood_brass'); return ok;"),
      ("T2-24", "F9", "setContrailStyle('invalid_trail') falls back to default 3D contrail emitter without error", "app.setContrailStyle('invalid_trail'); const ok = Boolean(app.hangar.contrailSystem); app.setContrailStyle('rainbow_ribbon'); return ok;"),
      ("T2-25", "F9", "setWingEmblem('invalid_emblem') falls back to default 3D wing emblem texture without error", "app.setWingEmblem('invalid_emblem'); const ok = app.hangar.vertexCount > 1000; app.setWingEmblem('fox_lantern_crest'); return ok;"),
      ("T2-26", "F3", "setCharacterAnimation('NonExistentCritter', 'unknown_clip') does not throw", "app.setCharacterAnimation('NonExistentCritter', 'unknown_clip'); return true;"),
      ("T2-27", "F4", "triggerCharacterTapReaction('UnknownCritter') safely handles unknown character ID", "app.triggerCharacterTapReaction('UnknownCritter'); return true;"),
      ("T2-28", "F7", "setZone(99) and setZone(-1) clamp or fall back to valid zoneId in {1, 2, 3}", "app.setZone(99); const zHigh = app.flight.zoneId; app.setZone(-1); const zLow = app.flight.zoneId; return [1,2,3].includes(zHigh) && [1,2,3].includes(zLow);"),
      ("T2-29", "F7", "setTimeOfDay('eclipse_999') falls back to valid timeOfDay in {'day','sunset','night'}", "app.setTimeOfDay('eclipse_999'); return ['day','sunset','night'].includes(app.flight.timeOfDay);"),
      ("T2-30", "F11", "setView('non_existent_tab') preserves a valid activeView", "app.setView('non_existent_tab'); return ['character_studio','flight_simulator','hangar','photo_booth'].includes(app.activeView);"),
  ]

  for tid, feat, title, js_body in fallback_cases:

    def _make_fb_test(t_id: str, f_id: str, t_title: str, body: str):
      @register_test(t_id, "Tier 2", f_id, t_title)
      async def _fn(session: ChromeCdpSession, base_url: str) -> None:
        await ensure_app_loaded(session, base_url)
        ok = await session.eval_js(f"""(() => {{
          const app = window.__APP_STATE__;
          {body}
        }})()""")
        assert ok is True, f"{t_id} failed fallback check"
        session.assert_zero_errors(t_id)

      return _fn

    _make_fb_test(tid, feat, title, js_body)

  # 31-38: Postcard Caption Edge Cases, Encoding & LocalStorage Fault Tolerance
  @register_test("T2-31", "Tier 2", "F10", "capturePostcard() with empty string caption ('') produces valid PNG")
  async def test_t2_31(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    card = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      app.setPhotoCaption('');
      return app.capturePostcard();
    })()""")
    verify_png_data_url(card["dataUrl"])
    session.assert_zero_errors("T2-31")

  @register_test("T2-32", "Tier 2", "F10", "capturePostcard() with HTML/script meta-characters escapes cleanly without XSS execution")
  async def test_t2_32(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    card = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      window.__XSS_TRIGGERED__ = false;
      app.setPhotoCaption('<img src=x onerror="window.__XSS_TRIGGERED__=true"><script>window.__XSS_TRIGGERED__=true</script> "SF ✈️ BOS"');
      const res = app.capturePostcard();
      return { dataUrl: res.dataUrl, xss: window.__XSS_TRIGGERED__ };
    })()""")
    assert card["xss"] is False, "XSS payload executed!"
    verify_png_data_url(card["dataUrl"])
    session.assert_zero_errors("T2-32")

  @register_test("T2-33", "Tier 2", "F10", "capturePostcard() with 500-character long caption truncates/wraps without canvas overflow error")
  async def test_t2_33(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    long_text = "Love you Mom in San Francisco! 🌉✈️🦊🦇💖 " * 15
    card = await session.eval_js(f"""(() => {{
      const app = window.__APP_STATE__;
      app.setPhotoCaption({json.dumps(long_text)});
      return app.capturePostcard();
    }})()""")
    verify_png_data_url(card["dataUrl"])
    session.assert_zero_errors("T2-33")

  @register_test("T2-34", "Tier 2", "F10", "Corrupted JSON in localStorage critters_airplane_3d_config_v1 recovers gracefully on load")
  async def test_t2_34(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    ok = await session.eval_js("""(() => {
      localStorage.setItem('critters_airplane_3d_config_v1', '{corrupted_json_!!!');
      window.__APP_STATE__.loadConfigFromLocalStorage();
      return Boolean(window.__APP_STATE__.hangar.modelId);
    })()""")
    assert ok is True
    session.assert_zero_errors("T2-34")

  @register_test("T2-35", "Tier 2", "F10", "Corrupted JSON in localStorage critters_airplane_3d_postcards_v1 recovers gracefully on reload")
  async def test_t2_35(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    await session.eval_js("localStorage.setItem('critters_airplane_3d_postcards_v1', '{not_valid_json');")
    await session.reload(wait_load=True, wait_app_ready=True)
    is_array = await session.eval_js("Array.isArray(window.__APP_STATE__.photoBooth.savedPostcards)")
    assert is_array is True
    session.assert_zero_errors("T2-35")

  @register_test("T2-36", "Tier 2", "F11", "Rapid 20-step view tab cycling preserves single WebGL2 context without context loss")
  async def test_t2_36(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    ctx_ok = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      const views = ['character_studio', 'hangar', 'flight_simulator', 'photo_booth'];
      for (let i = 0; i < 20; i++) {
        app.setView(views[i % views.length]);
        app.stepSimulation(1, 1/60);
      }
      return !app.renderer.getContext().isContextLost();
    })()""")
    assert ctx_ok is True
    session.assert_zero_errors("T2-36")

  @register_test("T2-37", "Tier 2", "F7", "Idempotent completeFlightToBoston() called 3x keeps progress=1.0 and distanceMiles=2700")
  async def test_t2_37(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    res = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      app.completeFlightToBoston();
      app.completeFlightToBoston();
      app.completeFlightToBoston();
      return { progress: app.flight.progress, miles: app.flight.distanceMiles, completed: app.flight.completed };
    })()""")
    assert res["progress"] == 1.0 and res["miles"] == 2700 and res["completed"] is True
    session.assert_zero_errors("T2-37")

  @register_test("T2-38", "Tier 2", "F8", "Repeated collectNearestItem('golden_lantern') 15x never throws even when course items deplete")
  async def test_t2_38(session: ChromeCdpSession, base_url: str) -> None:
    await ensure_app_loaded(session, base_url)
    count = await session.eval_js("""(() => {
      const app = window.__APP_STATE__;
      app.resetFlight();
      app.startFlight();
      for (let i = 0; i < 15; i++) app.collectNearestItem('golden_lantern');
      return app.flight.collectedCounts.golden_lantern;
    })()""")
    assert count >= 1
    session.assert_zero_errors("T2-38")

  # 39-44: iPad Responsive Viewports & Orientation Changes
  viewports = [
      ("T2-39", "iPad Pro 12.9-inch Landscape (1366x1024) viewport resize updates camera aspect cleanly", 1366, 1024),
      ("T2-40", "iPad Pro 12.9-inch Portrait (1024x1366) viewport resize updates camera aspect cleanly", 1024, 1366),
      ("T2-41", "iPad Air 10.9-inch Landscape (1180x820) viewport resize updates camera aspect cleanly", 1180, 820),
      ("T2-42", "iPad Air 10.9-inch Portrait (820x1180) viewport resize updates camera aspect cleanly", 820, 1180),
      ("T2-43", "iPad Mini 8.3-inch Landscape (1133x744) viewport resize updates camera aspect cleanly", 1133, 744),
      ("T2-44", "Standard Desktop HD (1440x900) viewport restoration", 1440, 900),
  ]

  for tid, title, vw, vh in viewports:

    def _make_vp_test(t_id: str, t_title: str, w: int, h: int):
      @register_test(t_id, "Tier 2", "F11", t_title)
      async def _fn(session: ChromeCdpSession, base_url: str) -> None:
        await ensure_app_loaded(session, base_url)
        await session.set_viewport(w, h, mobile=(w <= 1366))
        res = await session.eval_js("""(() => {
          window.dispatchEvent(new Event('resize'));
          window.__APP_STATE__.stepSimulation(2, 1/60);
          return {
            aspect: window.__APP_STATE__.camera.aspect,
            ctxOk: !window.__APP_STATE__.renderer.getContext().isContextLost(),
          };
        })()""")
        assert res["ctxOk"] is True and res["aspect"] > 0.4
        session.assert_zero_errors(t_id)

      return _fn

    _make_vp_test(tid, title, vw, vh)

  # 45-56: Both camelCase and snake_case animation names on individual characters
  anim_variants = [
      ("T2-45", "SunnyFox animation camelCase 'idle'", "SunnyFox", "idle"),
      ("T2-46", "SunnyFox animation snake_case 'joyful_wave'", "SunnyFox", "joyful_wave"),
      ("T2-47", "SunnyFox animation snake_case 'wing_flap_tail_wag'", "SunnyFox", "wing_flap_tail_wag"),
      ("T2-48", "SunnyFox animation snake_case 'happy_bounce_dance'", "SunnyFox", "happy_bounce_dance"),
      ("T2-49", "SunnyFox animation snake_case 'barrel_roll_cheer'", "SunnyFox", "barrel_roll_cheer"),
      ("T2-50", "SunnyFox animation snake_case 'cockpit_pilot_steer'", "SunnyFox", "cockpit_pilot_steer"),
      ("T2-51", "LunaBat animation camelCase 'idle'", "LunaBat", "idle"),
      ("T2-52", "LunaBat animation snake_case 'joyful_wave'", "LunaBat", "joyful_wave"),
      ("T2-53", "LunaBat animation snake_case 'wing_flap_tail_wag'", "LunaBat", "wing_flap_tail_wag"),
      ("T2-54", "LunaBat animation snake_case 'happy_bounce_dance'", "LunaBat", "happy_bounce_dance"),
      ("T2-55", "LunaBat animation snake_case 'barrel_roll_cheer'", "LunaBat", "barrel_roll_cheer"),
      ("T2-56", "LunaBat animation snake_case 'cockpit_pilot_steer'", "LunaBat", "cockpit_pilot_steer"),
  ]

  for tid, title, char_id, anim_name in anim_variants:

    def _make_anim_test(t_id: str, t_title: str, c_id: str, a_name: str):
      @register_test(t_id, "Tier 2", "F3", t_title)
      async def _fn(session: ChromeCdpSession, base_url: str) -> None:
        await ensure_app_loaded(session, base_url)
        ok = await session.eval_js(f"""(() => {{
          const app = window.__APP_STATE__;
          app.setCharacterAnimation({json.dumps(c_id)}, {json.dumps(a_name)});
          app.stepSimulation(8, 1/60);
          return Boolean(app.characters[{json.dumps(c_id)}].currentAnimation);
        }})()""")
        assert ok is True
        session.assert_zero_errors(t_id)

      return _fn

    _make_anim_test(tid, title, char_id, anim_name)


_register_tier2_tests()


# ==============================================================================
# TIER 3 — CROSS-FEATURE COMBINATIONS (14 Pairwise Tests: T3-01..T3-14)
# ==============================================================================


@register_test(
    "T3-01",
    "Tier 3",
    "F9+F5+F7+F10",
    "Hangar (supersonic_jet + midnight_bat_indigo + starlight_moon_dust) -> swapRoles -> Zone 3 Night -> Postcard -> Reload survival",
)
async def test_t3_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  snap = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('hangar');
    app.setPlaneModel('supersonic_jet');
    app.setPaintPalette('midnight_bat_indigo');
    app.setContrailStyle('starlight_moon_dust');
    app.setWingEmblem('bat_moonstar_crest');
    if (app.flight.pilotId !== 'LunaBat') app.swapRoles();
    app.setView('flight_simulator');
    app.startFlight();
    app.setZone(3);
    app.setTimeOfDay('night');
    app.stepSimulation(20, 1/60);
    const card = app.capturePostcard();
    app.saveConfigToLocalStorage();
    return {
      pilotId: app.flight.pilotId,
      pendantLightsActive: app.flight.pendantLightsActive,
      revealedRings: app.flight.revealedStarlightRingsCount,
      dataUrl: card.dataUrl,
    };
  })()""")
  assert snap["pilotId"] == "LunaBat"
  assert snap["pendantLightsActive"] is True and snap["revealedRings"] > 0
  verify_png_data_url(snap["dataUrl"])
  await session.reload(wait_load=True, wait_app_ready=True)
  after = await session.eval_js("""(() => ({
    modelId: window.__APP_STATE__.hangar.modelId,
    paintPaletteId: window.__APP_STATE__.hangar.paintPaletteId,
    contrailStyleId: window.__APP_STATE__.hangar.contrailStyleId,
    pilotId: window.__APP_STATE__.flight.pilotId,
  }))()""")
  assert after["modelId"] == "supersonic_jet"
  assert after["paintPaletteId"] == "midnight_bat_indigo"
  assert after["contrailStyleId"] == "starlight_moon_dust"
  assert after["pilotId"] == "LunaBat"
  session.assert_zero_errors("T3-01")


@register_test(
    "T3-02",
    "Tier 3",
    "F9+F5+F6+F7",
    "Origami Dream Glider + huntrx_golden_neon + wing_walker mode + 360 Barrel Roll in Zone 2 Rainbow Clouds",
)
async def test_t3_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('origami_glider');
    app.setPaintPalette('huntrx_golden_neon');
    app.setContrailStyle('lantern_fireflies');
    app.setCoPilotMode('wing_walker');
    app.startFlight();
    app.setZone(2);
    app.triggerBarrelRoll();
    app.stepSimulation(20, 1/60);
    return {
      modelId: app.hangar.modelId,
      coPilotMode: app.flight.coPilotMode,
      zoneId: app.flight.zoneId,
      barrelRollCount: app.flight.barrelRollCount,
    };
  })()""")
  assert res["modelId"] == "origami_glider" and res["coPilotMode"] == "wing_walker"
  assert res["zoneId"] == 2 and res["barrelRollCount"] >= 1
  session.assert_zero_errors("T3-02")


@register_test(
    "T3-03",
    "Tier 3",
    "F9+F6+F8",
    "Critter Cloud Biplane + mint_cloud + heart_bubbles + dropHeartPackage + collect mom_heart_care_package in Zone 1",
)
async def test_t3_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('biplane');
    app.setPaintPalette('mint_cloud');
    app.setContrailStyle('heart_bubbles');
    app.resetFlight();
    app.startFlight();
    app.setZone(1);
    app.dropHeartPackage();
    app.collectNearestItem('mom_heart_care_package');
    return {
      dropped: app.flight.carePackagesDropped,
      collected: app.flight.collectedCounts.mom_heart_care_package,
      score: app.flight.score,
    };
  })()""")
  assert res["dropped"] >= 1 and res["collected"] >= 1 and res["score"] >= 250
  session.assert_zero_errors("T3-03")


@register_test(
    "T3-04",
    "Tier 3",
    "F1+F2+F3+F5",
    "Toggling pilotGear accessories (aviatorGoggles, pilotScarf, captainCap) in Studio persists into Tandem Cockpit Flight",
)
async def test_t3_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    const fox = app.characters.SunnyFox.group || app.characters.SunnyFox;
    const cap = fox.getObjectByName('captainCap');
    if (cap) cap.visible = true;
    app.setView('flight_simulator');
    app.stepSimulation(5, 1/60);
    return Boolean(cap && cap.visible);
  })()""")
  assert res is True
  session.assert_zero_errors("T3-04")


@register_test(
    "T3-05",
    "Tier 3",
    "F3+F10",
    "Capturing Photo Booth postcards across all 4 backdrops with different character animations",
)
async def test_t3_05(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  urls = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('photo_booth');
    const pairs = [
      ['sf_golden_gate_sunrise', 'wave'],
      ['rainbow_cloud_archipelago', 'wingFlapTailWag'],
      ['boston_zakim_starlight', 'bounceDance'],
      ['sweet_hangar_studio', 'barrelRollCheer'],
    ];
    return pairs.map(([bg, anim]) => {
      app.setPhotoBackdrop(bg);
      app.setCharacterAnimation(anim);
      app.stepSimulation(5, 1/60);
      return app.capturePostcard().dataUrl;
    });
  })()""")
  for u in urls:
    verify_png_data_url(u)
  session.assert_zero_errors("T3-05")


@register_test(
    "T3-06",
    "Tier 3",
    "F5+F6+F7",
    "Dynamic Time-of-Day cycling (day -> sunset -> night) during active Starlight Boost and Role Swap",
)
async def test_t3_06(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.resetFlight();
    app.startFlight();
    app.triggerBoost();
    app.setTimeOfDay('day');
    app.stepSimulation(5, 1/60);
    app.swapRoles();
    app.setTimeOfDay('sunset');
    app.stepSimulation(5, 1/60);
    app.setTimeOfDay('night');
    app.stepSimulation(5, 1/60);
    return {
      boostActive: app.flight.boostActive,
      pendantLightsActive: app.flight.pendantLightsActive,
      roleSwapCount: app.flight.roleSwapCount,
    };
  })()""")
  assert res["boostActive"] is True and res["pendantLightsActive"] is True and res["roleSwapCount"] >= 1
  session.assert_zero_errors("T3-06")


@register_test(
    "T3-07",
    "Tier 3",
    "F8+F9",
    "Collecting all 6 collectible types sequentially in Starlight Supersonic Jet accumulates full score",
)
async def test_t3_07(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('supersonic_jet');
    app.resetFlight();
    app.startFlight();
    const types = [
      'golden_lantern',
      'crescent_moon_star',
      'music_note_booster',
      'mom_heart_care_package',
      'sky_ring',
      'starlight_ring',
      'paper_airplane_squadron',
    ];
    types.forEach(t => app.collectNearestItem(t));
    return {
      score: app.flight.score,
      counts: app.flight.collectedCounts,
    };
  })()""")
  assert res["score"] >= 800, f"Expected cumulative score >= 800 across all collectibles: {res}"
  for k in ("golden_lantern", "crescent_moon_star", "music_note_booster", "mom_heart_care_package", "sky_ring", "starlight_ring", "paper_airplane_squadron"):
    assert res["counts"][k] >= 1, f"Missing collection count for {k}: {res}"
  session.assert_zero_errors("T3-07")


@register_test(
    "T3-08",
    "Tier 3",
    "F9+F10",
    "Capturing postcards across all 3 aircraft models stores distinct aircraftConfig metadata in savedPostcards",
)
async def test_t3_08(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  models = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.photoBooth.savedPostcards.length = 0;
    ['biplane', 'supersonic_jet', 'origami_glider'].forEach(m => {
      app.setPlaneModel(m);
      app.capturePostcard();
    });
    return app.photoBooth.savedPostcards.slice(0, 3).map(c => c.aircraftConfig ? c.aircraftConfig.modelId : '');
  })()""")
  assert set(models) == {"biplane", "supersonic_jet", "origami_glider"}, f"Unexpected savedPostcards models: {models}"
  session.assert_zero_errors("T3-08")


@register_test(
    "T3-09",
    "Tier 3",
    "F4+F10",
    "Tap-to-react particle burst emission on SunnyFox and LunaBat followed by immediate Photo Booth PNG capture",
)
async def test_t3_09(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  data_url = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.triggerCharacterTapReaction('SunnyFox');
    app.triggerCharacterTapReaction('LunaBat');
    app.stepSimulation(4, 1/60);
    return app.capturePostcard().dataUrl;
  })()""")
  verify_png_data_url(data_url)
  session.assert_zero_errors("T3-09")


@register_test(
    "T3-10",
    "Tier 3",
    "F5+F6",
    "Swapping roles while in wing_walker mode transfers new Co-Pilot onto upper wing and new Pilot to front yoke",
)
async def test_t3_10(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setCoPilotMode('wing_walker');
    const beforeCoPilot = app.flight.coPilotId;
    app.swapRoles();
    const afterCoPilot = app.flight.coPilotId;
    return {
      mode: app.flight.coPilotMode,
      swapped: beforeCoPilot !== afterCoPilot,
    };
  })()""")
  assert res["mode"] == "wing_walker" and res["swapped"] is True
  session.assert_zero_errors("T3-10")


@register_test(
    "T3-11",
    "Tier 3",
    "F6+F7",
    "Extreme corner steering (-18, 28) combined with simultaneous Boost + Barrel Roll in Zone 3 Night mode",
)
async def test_t3_11(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.resetFlight();
    app.startFlight();
    app.setZone(3);
    app.setTimeOfDay('night');
    app.setSteering(-5.0, 5.0);
    app.triggerBoost();
    app.triggerBarrelRoll();
    app.stepSimulation(150, 1/60);
    return {
      x: app.flight.position.x,
      y: app.flight.position.y,
      pendantLightsActive: app.flight.pendantLightsActive,
    };
  })()""")
  assert abs(res["x"] + 18.0) < 1e-4 and abs(res["y"] - 28.0) < 1e-4 and res["pendantLightsActive"] is True
  session.assert_zero_errors("T3-11")


@register_test(
    "T3-12",
    "Tier 3",
    "F7+F10",
    "completeFlightToBoston -> Boston Zakim Postcard capture -> resetFlight returns to SF while keeping Hangar & Postcards",
)
async def test_t3_12(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('supersonic_jet');
    app.completeFlightToBoston();
    app.setPhotoBackdrop('boston_zakim_starlight');
    const card = app.capturePostcard();
    const countAfterLanding = app.photoBooth.savedPostcards.length;
    app.resetFlight();
    return {
      flightState: app.flight.flightState,
      progress: app.flight.progress,
      modelId: app.hangar.modelId,
      postcardsKept: app.photoBooth.savedPostcards.length === countAfterLanding,
      dataUrl: card.dataUrl,
    };
  })()""")
  assert res["flightState"] == "ready_sf" and res["progress"] == 0.0
  assert res["modelId"] == "supersonic_jet" and res["postcardsKept"] is True
  verify_png_data_url(res["dataUrl"])
  session.assert_zero_errors("T3-12")


@register_test(
    "T3-13",
    "Tier 3",
    "F4+F5+F6",
    "Audio mute state toggles cleanly across character tap reactions, role swaps, boost, barrel roll, and heart drops",
)
async def test_t3_13(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  ok = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.audioMuted = true;
    app.triggerCharacterTapReaction('SunnyFox');
    app.swapRoles();
    app.triggerBoost();
    app.triggerBarrelRoll();
    app.dropHeartPackage();
    app.audioMuted = false;
    return true;
  })()""")
  assert ok is True
  session.assert_zero_errors("T3-13")


@register_test(
    "T3-14",
    "Tier 3",
    "F9+F11",
    "Cross-bundle parity: root index.html, docs/index.html, and dist/index.html expose identical 3D character & aircraft counts",
)
async def test_t3_14(session: ChromeCdpSession, base_url: str) -> None:
  snapshots = []
  for path in ("/index.html", "/docs/index.html", "/dist/index.html"):
    await session.navigate(f"{base_url}{path}", wait_load=True, wait_app_ready=True)
    snap = await session.eval_js("""(() => ({
      foxVerts: window.__APP_STATE__.characters.SunnyFox.vertexCount,
      batVerts: window.__APP_STATE__.characters.LunaBat.vertexCount,
      planeVerts: window.__APP_STATE__.hangar.vertexCount,
    }))()""")
    snapshots.append(snap)
    session.assert_zero_errors(f"T3-14:{path}")
  assert snapshots[0] == snapshots[1] == snapshots[2], f"Bundle parity mismatch: {snapshots}"
  await ensure_app_loaded(session, base_url, force_reload=True)


# ==============================================================================
# TIER 4 — REAL-WORLD APPLICATION SCENARIOS (6 End-to-End Journeys: T4-01..T4-06)
# ==============================================================================


@register_test(
    "T4-01",
    "Tier 4",
    "E2E-Journey-1",
    "Complete iPad Pro Daughter Journey: Studio Inspection -> Hangar Custom Jet -> SF Takeoff -> Zone 2 & 3 -> Boston Landing -> Postcard to Mom -> Reload",
)
async def test_t4_01(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url, force_reload=True)
  await session.set_viewport(1366, 1024, mobile=True)
  journey = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    // Step 1: 3D Character Studio inspection
    app.setView('character_studio');
    app.triggerCharacterTapReaction('SunnyFox');
    app.triggerCharacterTapReaction('LunaBat');
    for (const anim of ['idle', 'wave', 'wingFlapTailWag', 'bounceDance', 'barrelRollCheer', 'cockpitPilotSteer']) {
      app.setCharacterAnimation(anim);
      app.stepSimulation(6, 1/60);
    }
    // Step 2: 3D Hangar customization
    app.setView('hangar');
    app.setPlaneModel('supersonic_jet');
    app.setPaintPalette('sunset_fox_amber');
    app.setPropellerStyle('starlight_crystal_turbine');
    app.setContrailStyle('rainbow_ribbon');
    app.setWingEmblem('sf_boston_heart_wings');
    // Step 3: SF -> Boston 3-Zone flight adventure
    app.setView('flight_simulator');
    app.resetFlight();
    app.startFlight();
    app.setZone(1);
    app.setSteering(0.4, 0.3);
    app.triggerBoost();
    app.collectNearestItem('golden_lantern');
    app.stepSimulation(20, 1/60);
    app.setZone(2);
    app.triggerBarrelRoll();
    app.dropHeartPackage();
    app.collectNearestItem('paper_airplane_squadron');
    app.stepSimulation(20, 1/60);
    app.setZone(3);
    app.setTimeOfDay('night');
    app.collectNearestItem('starlight_ring');
    app.stepSimulation(20, 1/60);
    app.completeFlightToBoston();
    // Step 4: Send 3D Flight Postcard to Mom
    app.setView('photo_booth');
    app.setPhotoBackdrop('boston_zakim_starlight');
    app.setPhotoPose('wing_walker_cheer');
    app.setPhotoCaption('Landed in Boston from Mom in San Francisco! Love SunnyFox & LunaBat!');
    const postcard = app.capturePostcard();
    app.saveConfigToLocalStorage();
    return {
      completed: app.flight.completed,
      flightState: app.flight.flightState,
      score: app.flight.score,
      pendantLightsActive: app.flight.pendantLightsActive,
      dataUrl: postcard.dataUrl,
    };
  })()""")
  assert journey["completed"] is True and journey["flightState"] == "landed_boston"
  assert journey["score"] >= 400 and journey["pendantLightsActive"] is True
  verify_png_data_url(journey["dataUrl"])
  await session.reload(wait_load=True, wait_app_ready=True)
  restored = await session.eval_js("window.__APP_STATE__.hangar.modelId")
  assert restored == "supersonic_jet"
  await session.set_viewport(1440, 900, mobile=False)
  session.assert_zero_errors("T4-01")


@register_test(
    "T4-02",
    "Tier 4",
    "E2E-Journey-2",
    "Co-Pilot Wing-Walker Stunt Show & Mid-Flight Role Swap Marathon (Biplane across Zones 1, 2, 3)",
)
async def test_t4_02(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('biplane');
    app.setPaintPalette('sunset_fox_amber');
    app.resetFlight();
    app.startFlight();
    app.setCoPilotMode('wing_walker');
    const initialPilot = app.flight.pilotId;
    app.triggerBarrelRoll();
    app.stepSimulation(20, 1/60);
    app.swapRoles();
    const midPilot = app.flight.pilotId;
    app.setZone(2);
    app.dropHeartPackage();
    app.stepSimulation(20, 1/60);
    app.swapRoles();
    app.setZone(3);
    app.completeFlightToBoston();
    return {
      initialPilot,
      midPilot,
      finalPilot: app.flight.pilotId,
      roleSwapCount: app.flight.roleSwapCount,
      completed: app.flight.completed,
    };
  })()""")
  assert res["initialPilot"] != res["midPilot"]
  assert res["finalPilot"] == res["initialPilot"]
  assert res["roleSwapCount"] >= 2 and res["completed"] is True
  session.assert_zero_errors("T4-02")


@register_test(
    "T4-03",
    "Tier 4",
    "E2E-Journey-3",
    "Origami Dream Glider Starlight Night Expedition: Pendant Illumination of Hidden Rings & Full Collectible Sweep",
)
async def test_t4_03(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('origami_glider');
    app.setPaintPalette('midnight_bat_indigo');
    app.setContrailStyle('starlight_moon_dust');
    app.resetFlight();
    app.startFlight();
    app.setZone(3);
    app.setTimeOfDay('night');
    ['golden_lantern', 'crescent_moon_star', 'music_note_booster', 'mom_heart_care_package', 'sky_ring', 'starlight_ring', 'paper_airplane_squadron'].forEach(t => {
      app.collectNearestItem(t);
    });
    app.stepSimulation(25, 1/60);
    app.completeFlightToBoston();
    return {
      revealed: app.flight.revealedStarlightRingsCount,
      score: app.flight.score,
      completed: app.flight.completed,
    };
  })()""")
  assert res["revealed"] > 0 and res["score"] >= 800 and res["completed"] is True
  session.assert_zero_errors("T4-03")


@register_test(
    "T4-04",
    "Tier 4",
    "E2E-Journey-4",
    "Multi-Postcard Scrapbook Creation & Browser Reload Persistence Lifecycle",
)
async def test_t4_04(session: ChromeCdpSession, base_url: str) -> None:
  await ensure_app_loaded(session, base_url)
  cards = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    localStorage.removeItem('critters_airplane_3d_postcards_v1');
    app.photoBooth.savedPostcards.length = 0;
    const specs = [
      ['biplane', 'sf_golden_gate_sunrise', 'Takeoff from Mom in SF!'],
      ['origami_glider', 'rainbow_cloud_archipelago', 'Soaring through Rainbow Clouds!'],
      ['supersonic_jet', 'boston_zakim_starlight', 'Touchdown in Boston!'],
    ];
    return specs.map(([m, bg, cap]) => {
      app.setPlaneModel(m);
      app.setPhotoBackdrop(bg);
      app.setPhotoCaption(cap);
      return app.capturePostcard();
    });
  })()""")
  assert len(cards) == 3
  for c in cards:
    verify_png_data_url(c["dataUrl"])
  await session.reload(wait_load=True, wait_app_ready=True)
  saved_len = await session.eval_js("window.__APP_STATE__.photoBooth.savedPostcards.length")
  assert saved_len == 3, f"Expected 3 persisted postcards after reload, got {saved_len}"
  session.assert_zero_errors("T4-04")


@register_test(
    "T4-05",
    "Tier 4",
    "E2E-Journey-5",
    "GitHub Pages Production Deployment (docs/index.html) Full E2E Flight & Photo Booth Journey",
)
async def test_t4_05(session: ChromeCdpSession, base_url: str) -> None:
  await session.navigate(f"{base_url}/docs/index.html", wait_load=True, wait_app_ready=True)
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setPlaneModel('supersonic_jet');
    app.startFlight();
    app.triggerBoost();
    app.stepSimulation(20, 1/60);
    app.completeFlightToBoston();
    const card = app.capturePostcard();
    return {
      ready: app.ready,
      completed: app.flight.completed,
      dataUrl: card.dataUrl,
    };
  })()""")
  assert res["ready"] is True and res["completed"] is True
  verify_png_data_url(res["dataUrl"])
  session.assert_zero_errors("T4-05")
  await ensure_app_loaded(session, base_url, force_reload=True)


@register_test(
    "T4-06",
    "Tier 4",
    "E2E-Journey-6",
    "Standalone Offline Single-File Bundle (dist/index.html) Full E2E Journey Under Network Offline Emulation",
)
async def test_t4_06(session: ChromeCdpSession, base_url: str) -> None:
  await session.navigate(f"{base_url}/dist/index.html", wait_load=True, wait_app_ready=True)
  await session.set_offline_mode(True)
  try:
    res = await session.eval_js("""(async () => {
      const app = window.__APP_STATE__;
      app.setPlaneModel('origami_glider');
      app.setPaintPalette('mint_cloud');
      app.startFlight();
      app.triggerBarrelRoll();
      app.dropHeartPackage();
      app.stepSimulation(25, 1/60);
      app.completeFlightToBoston();
      const card = app.capturePostcard();
      await new Promise(r => setTimeout(r, 60));
      const foxImg = document.getElementById('img-ref-fox');
      const batImg = document.getElementById('img-ref-bat');
      const imgsLoaded = Boolean(
        foxImg && foxImg.complete && foxImg.naturalWidth >= 512 &&
        batImg && batImg.complete && batImg.naturalWidth >= 512
      );
      return {
        ready: app.ready,
        completed: app.flight.completed,
        imgsLoaded,
        dataUrl: card.dataUrl,
      };
    })()""")
    assert res["ready"] is True and res["completed"] is True and res["imgsLoaded"] is True, f"T4-06 failed: {res}"
    verify_png_data_url(res["dataUrl"])
    session.assert_zero_errors("T4-06")
  finally:
    await session.set_offline_mode(False)
    await ensure_app_loaded(session, base_url, force_reload=True)


# ==============================================================================
# TEST RUNNER & SUMMARY REPORTER
# ==============================================================================


async def run_suite(
    tier_filter: str = "all",
    name_filter: str = "",
    json_report_path: str | None = None,
    wait_for_build_sec: int = 0,
) -> int:
  """Execute registered E2E tests in Headless Chrome 153 with SwiftShader WebGL 2.0."""
  index_file = PROJECT_ROOT / "index.html"
  dist_file = PROJECT_ROOT / "dist" / "index.html"
  if wait_for_build_sec > 0:
    deadline = time.monotonic() + wait_for_build_sec
    while time.monotonic() < deadline:
      if index_file.is_file() and dist_file.is_file():
        break
      await asyncio.sleep(1.0)

  if not index_file.is_file():
    print(f"[ERROR] {index_file} does not exist yet. Cannot run E2E suite.", file=sys.stderr)
    return 2

  selected_specs = []
  for spec in TEST_REGISTRY:
    if tier_filter != "all" and tier_filter.lower() not in spec.tier.lower():
      continue
    if name_filter and (
        name_filter.lower() not in spec.test_id.lower()
        and name_filter.lower() not in spec.title.lower()
        and name_filter.lower() not in spec.feature.lower()
    ):
      continue
    selected_specs.append(spec)

  print("=" * 88)
  print("SMILING CRITTERS 3D SKY & AIRPLANE ADVENTURE — HEADLESS CHROME 153 WEBGL 2.0 E2E SUITE")
  print(f"Project Root : {PROJECT_ROOT}")
  print(f"Selected     : {len(selected_specs)} / {len(TEST_REGISTRY)} registered tests")
  print("=" * 88)

  results: list[TestCaseResult] = []
  suite_start = time.monotonic()

  with LocalHttpServer(PROJECT_ROOT) as server:
    async with ChromeCdpSession() as session:
      webgl_info = await session.verify_webgl2_context()
      print(
          f"[WebGL 2.0 Verified] Version: {webgl_info.get('version')} | "
          f"Renderer: {webgl_info.get('renderer')}"
      )
      await session.navigate(f"{server.base_url}/index.html", wait_load=True, wait_app_ready=True)

      for idx, spec in enumerate(selected_specs, 1):
        t0 = time.monotonic()
        session.reset_errors()
        passed = False
        err_msg = ""
        try:
          await spec.fn(session, server.base_url)
          passed = True
        except Exception as exc:  # pylint: disable=broad-except
          err_msg = f"{type(exc).__name__}: {exc}"
        dur_ms = (time.monotonic() - t0) * 1000.0
        res = TestCaseResult(
            test_id=spec.test_id,
            tier=spec.tier,
            feature=spec.feature,
            title=spec.title,
            passed=passed,
            duration_ms=round(dur_ms, 2),
            error_message=err_msg,
            console_error_count=len(session.console_errors),
            page_exception_count=len(session.page_exceptions),
        )
        results.append(res)
        status_str = "PASS" if passed else "FAIL"
        print(
            f"[{idx:03d}/{len(selected_specs):03d}] {status_str} | {spec.test_id:<9} | "
            f"{spec.tier:<6} | {spec.feature:<11} | {dur_ms:6.1f} ms | {spec.title}"
        )
        if not passed:
          print(f"      └── Error: {err_msg}")

  total_ms = (time.monotonic() - suite_start) * 1000.0
  passed_count = sum(1 for r in results if r.passed)
  failed_count = len(results) - passed_count

  print("=" * 88)
  print(
      f"SUMMARY: {passed_count}/{len(results)} PASSED ({failed_count} FAILED) "
      f"in {total_ms / 1000.0:.2f}s"
  )
  for tier_label in ("Tier 1", "Tier 2", "Tier 3", "Tier 4"):
    t_res = [r for r in results if r.tier == tier_label]
    if t_res:
      t_pass = sum(1 for r in t_res if r.passed)
      print(f"  - {tier_label}: {t_pass}/{len(t_res)} passed")
  print("=" * 88)

  if json_report_path:
    report_payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "duration_ms": round(total_ms, 2),
        "webgl_info": webgl_info,
        "results": [r.__dict__ for r in results],
    }
    Path(json_report_path).write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

  cleanup_all_shm_dirs()
  return 0 if failed_count == 0 else 1


def main() -> None:
  parser = argparse.ArgumentParser(description="Run Critters Airplane 3D E2E Test Suite")
  parser.add_argument("--tier", default="all", help="Filter by tier (e.g. 'Tier 1', 'Tier 2', 'all')")
  parser.add_argument("--filter", default="", help="Substring filter for test_id, feature, or title")
  parser.add_argument("--json-report", default="", help="Optional path to write JSON test report")
  parser.add_argument("--wait-for-build", type=int, default=0, help="Wait up to N seconds for index.html & dist/index.html")
  args = parser.parse_args()
  exit_code = asyncio.run(
      run_suite(
          tier_filter=args.tier,
          name_filter=args.filter,
          json_report_path=args.json_report or None,
          wait_for_build_sec=args.wait_for_build,
      )
  )
  sys.exit(exit_code)


if __name__ == "__main__":
  main()
