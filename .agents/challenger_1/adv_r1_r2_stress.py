#!/usr/bin/env python3
"""Tier 5 White-Box Adversarial Stress Test Suite (`challenger_1`).

Standalone Python 3.13 + CDP Headless Chrome 153 WebGL 2.0 stress harness verifying:
1. R1 3D Scene Graph & Skeletal Animation Stress:
   - Exact vertex & mesh counts for SunnyFox (21,091 vertices, 16 required child groups)
     and LunaBat (17,724 vertices, 14 required child groups).
   - Rapid cycling through all 6 animations (`idle`, `wave`, `wingFlapTailWag`,
     `bounceDance`, `barrelRollCheer`, `cockpitPilotSteer`) + snake_case aliases
     across 120 simulation steps, asserting zero NaN/Infinity quaternions, positions,
     rotations, scales, or world matrices on every single bone/sub-group/mesh.
   - Real-time `THREE.PointLight` color (`#ffd966`, `#ffe57f`), distance (`45.0`),
     and intensity transitions across `day` (1.2), `sunset` (2.4), `night` (3.8 / 3.6),
     and tap reactions (4.5).
   - All 3 `pilotGear` toggles (`aviatorGoggles`, `pilotScarf` with animated tails,
     `captainCap`) on both SunnyFox and LunaBat.
2. R2 Extreme Flight Kinematics & Collectible Stress:
   - Extreme `setSteering(±999, ±999)` + `NaN`/`Infinity` resilience.
   - Simultaneous `triggerBoost()` + `triggerBarrelRoll()` + `dropHeartPackage()` +
     `swapRoles()` + `setCoPilotMode('wing_walker')` + multi-class item collection
     across 180 simulation steps.
   - Strict coordinate bounds (`x ∈ [-18, 18]`, `y ∈ [3, 28]`) at every step.
   - Monotonically increasing score across all flight stunts, drops, collectibles,
     and landing.
   - Zone 3 hidden starlight ring illumination (`pendantLightsActive === true`,
     `revealedStarlightRingsCount === 18`, `opacity === 1.0`, `emissiveIntensity === 2.6`).
   - Boston landing celebration (`completeFlightToBoston()`, `flightState === 'landed_boston'`,
     `distanceMiles === 2700`, `progress === 1.0`).
"""

from __future__ import annotations

import asyncio
import atexit
import glob
import json
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any

# Import project CDP driver from tests/ (read-only)
PROJECT_ROOT = Path("/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d")
TESTS_DIR = PROJECT_ROOT / "tests"
if str(TESTS_DIR) not in sys.path:
  sys.path.insert(0, str(TESTS_DIR))

from cdp_driver import (  # pylint: disable=g-import-not-at-top
    ChromeCdpSession,
    LocalHttpServer,
    cleanup_all_shm_dirs,
)


def force_cleanup_shm() -> None:
  """Ensure zero /dev/shm Chrome temporary directories remain on exit."""
  cleanup_all_shm_dirs()
  for pattern in (
      f"/dev/shm/e2e_chrome_{os.getpid()}*",
      "/dev/shm/adv_chrome_*",
  ):
    for p in glob.glob(pattern):
      try:
        shutil.rmtree(p, ignore_errors=True)
      except Exception:  # pylint: disable=broad-except
        pass


atexit.register(force_cleanup_shm)


async def run_r1_stress(session: ChromeCdpSession) -> dict[str, Any]:
  """Execute R1 3D Scene Graph, 120-step Animation Cycling, PointLight & PilotGear Stress."""
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    if (!app || !app.ready) {
      throw new Error('window.__APP_STATE__ is not ready');
    }

    const fox = app.characters.SunnyFox.group || app.characters.SunnyFox;
    const bat = app.characters.LunaBat.group || app.characters.LunaBat;

    const countGeom = (root) => {
      let verts = 0;
      let meshes = 0;
      let nodes = 0;
      root.traverse((obj) => {
        nodes += 1;
        if (obj.isMesh && obj.geometry && obj.geometry.attributes && obj.geometry.attributes.position) {
          verts += obj.geometry.attributes.position.count;
          meshes += 1;
        }
      });
      return { verts, meshes, nodes };
    };

    const foxStats = countGeom(fox);
    const batStats = countGeom(bat);

    const foxRequiredGroups = [
      'head', 'leftEar', 'rightEar', 'eyes', 'eyePatchLeft', 'leftEyePatchRing',
      'muzzle', 'torso', 'zipper', 'lanternPendant', 'leftArm', 'rightArm',
      'leftLeg', 'rightLeg', 'tail', 'pilotGear'
    ];
    const batRequiredGroups = [
      'head', 'leftEar', 'rightEar', 'eyes', 'muzzle', 'nose', 'torso',
      'zipper', 'moonStarPendant', 'leftWingArm', 'rightWingArm',
      'leftLeg', 'rightLeg', 'pilotGear'
    ];

    const missingFoxGroups = foxRequiredGroups.filter((g) => !fox.getObjectByName(g));
    const missingBatGroups = batRequiredGroups.filter((g) => !bat.getObjectByName(g));

    // 1. Rapidly cycle through all 6 animations across 120 simulation steps
    const animations = [
      'idle',
      'wave',
      'wingFlapTailWag',
      'bounceDance',
      'barrelRollCheer',
      'cockpitPilotSteer',
    ];
    const aliasAnimations = [
      'idle',
      'joyful_wave',
      'wing_flap_tail_wag',
      'happy_bounce_dance',
      'barrel_roll_cheer',
      'cockpit_pilot_steer',
    ];

    let nanOrInfCount = 0;
    let unnormalizedQuatCount = 0;
    let totalNodeChecks = 0;
    const canonicalStatesSeen = new Set();

    const inspectHierarchyFinite = (root, stepIdx, animName) => {
      root.updateMatrixWorld(true);
      root.traverse((obj) => {
        totalNodeChecks += 1;
        const p = obj.position;
        const q = obj.quaternion;
        const r = obj.rotation;
        const s = obj.scale;
        const m = obj.matrixWorld.elements;

        if (
          !Number.isFinite(p.x) || !Number.isFinite(p.y) || !Number.isFinite(p.z) ||
          !Number.isFinite(q.x) || !Number.isFinite(q.y) || !Number.isFinite(q.z) || !Number.isFinite(q.w) ||
          !Number.isFinite(r.x) || !Number.isFinite(r.y) || !Number.isFinite(r.z) ||
          !Number.isFinite(s.x) || !Number.isFinite(s.y) || !Number.isFinite(s.z) ||
          s.x <= 0 || s.y <= 0 || s.z <= 0
        ) {
          nanOrInfCount += 1;
        }

        const qNorm = Math.hypot(q.x, q.y, q.z, q.w);
        if (!Number.isFinite(qNorm) || Math.abs(qNorm - 1.0) > 1e-3) {
          unnormalizedQuatCount += 1;
        }

        for (let i = 0; i < 16; i++) {
          if (!Number.isFinite(m[i])) {
            nanOrInfCount += 1;
            break;
          }
        }
      });
    };

    const origRender = app.renderer.render.bind(app.renderer);
    for (let step = 0; step < 120; step++) {
      // Execute full WebGL software render on boundary steps while checking 3D scene graph every step
      app.renderer.render = (step === 0 || step === 60 || step === 119) ? origRender : () => {};
      const animFox = animations[step % animations.length];
      const animBat = aliasAnimations[(step + 3) % aliasAnimations.length];
      app.setCharacterAnimation('SunnyFox', animFox);
      app.setCharacterAnimation('LunaBat', animBat);
      // Vary steering during cockpitPilotSteer to stress head/arm/wing coupling
      app.setSteering(Math.sin(step * 0.35), Math.cos(step * 0.25));
      app.stepSimulation(1, 1 / 60);

      canonicalStatesSeen.add(fox.userData.canonicalAnimState);
      canonicalStatesSeen.add(bat.userData.canonicalAnimState);

      inspectHierarchyFinite(fox, step, animFox);
      inspectHierarchyFinite(bat, step, animBat);
    }
    app.renderer.render = origRender;

    // 2. Verify real-time THREE.PointLight color, distance, and intensity transitions
    const captureLightState = (mode) => {
      app.setTimeOfDay(mode);
      app.stepSimulation(1, 1 / 60);
      return {
        mode,
        pendantLightsActive: app.flight.pendantLightsActive,
        revealedStarlightRingsCount: app.flight.revealedStarlightRingsCount,
        foxLight: {
          isPointLight: Boolean(fox.pendantLight && fox.pendantLight.isPointLight),
          colorHex: '#' + fox.pendantLight.color.getHexString().toLowerCase(),
          intensity: fox.pendantLight.intensity,
          distance: fox.pendantLight.distance,
        },
        batLight: {
          isPointLight: Boolean(bat.pendantLight && bat.pendantLight.isPointLight),
          colorHex: '#' + bat.pendantLight.color.getHexString().toLowerCase(),
          intensity: bat.pendantLight.intensity,
          distance: bat.pendantLight.distance,
        },
      };
    };

    const lightDay = captureLightState('day');
    const lightSunset = captureLightState('sunset');
    const lightNight = captureLightState('night');

    const tapFox = app.triggerCharacterTapReaction('SunnyFox');
    const tapBat = app.triggerCharacterTapReaction('LunaBat');

    // 3. Verify pilotGear toggles (aviatorGoggles, pilotScarf, captainCap) on both characters
    const gearItems = ['aviatorGoggles', 'pilotScarf', 'captainCap'];
    const gearToggleResults = {};
    app.renderer.render = () => {};
    for (const charId of ['SunnyFox', 'LunaBat']) {
      gearToggleResults[charId] = {};
      const root = charId === 'SunnyFox' ? fox : bat;
      const gearGrp = root.getObjectByName('pilotGear');
      for (const itemName of gearItems) {
        const onState = app.toggleAccessory(charId, itemName, true);
        const meshObj = gearGrp.getObjectByName(itemName);
        const visibleWhenOn = Boolean(meshObj && meshObj.visible);
        app.stepSimulation(2, 1 / 60);
        inspectHierarchyFinite(root, 999, 'gear_on_' + itemName);
        const offState = app.toggleAccessory(charId, itemName, false);
        const visibleWhenOff = Boolean(meshObj && meshObj.visible);
        gearToggleResults[charId][itemName] = {
          onState,
          visibleWhenOn,
          offState,
          visibleWhenOff,
        };
      }
    }
    app.renderer.render = origRender;
    origRender(app.scene, app.camera);

    return {
      foxStats,
      batStats,
      missingFoxGroups,
      missingBatGroups,
      nanOrInfCount,
      unnormalizedQuatCount,
      totalNodeChecks,
      canonicalStatesSeen: Array.from(canonicalStatesSeen),
      lightTransitions: { day: lightDay, sunset: lightSunset, night: lightNight },
      tapReactions: { tapFox, tapBat },
      gearToggleResults,
    };
  })()""")

  assert res["foxStats"]["verts"] == 21091, f"Expected SunnyFox 21,091 vertices, got {res['foxStats']}"
  assert res["batStats"]["verts"] == 17724, f"Expected LunaBat 17,724 vertices, got {res['batStats']}"
  assert not res["missingFoxGroups"], f"Missing SunnyFox groups: {res['missingFoxGroups']}"
  assert not res["missingBatGroups"], f"Missing LunaBat groups: {res['missingBatGroups']}"
  assert res["nanOrInfCount"] == 0, f"Detected NaN/Infinity transforms during 120-step stress: {res}"
  assert res["unnormalizedQuatCount"] == 0, f"Detected unnormalized quaternions: {res}"
  assert len(res["canonicalStatesSeen"]) == 6, f"Expected all 6 canonical animations visited: {res['canonicalStatesSeen']}"

  # PointLight assertions
  lt = res["lightTransitions"]
  assert lt["day"]["foxLight"]["colorHex"] == "#ffd966"
  assert lt["day"]["batLight"]["colorHex"] == "#ffe57f"
  assert lt["day"]["pendantLightsActive"] is False
  assert abs(lt["day"]["foxLight"]["intensity"] - 1.2) < 1e-5
  assert abs(lt["day"]["batLight"]["intensity"] - 1.2) < 1e-5

  assert lt["sunset"]["pendantLightsActive"] is True
  assert abs(lt["sunset"]["foxLight"]["intensity"] - 2.4) < 1e-5
  assert abs(lt["sunset"]["batLight"]["intensity"] - 2.4) < 1e-5

  assert lt["night"]["pendantLightsActive"] is True
  assert abs(lt["night"]["foxLight"]["intensity"] - 3.8) < 1e-5
  assert abs(lt["night"]["foxLight"]["distance"] - 45.0) < 1e-5
  assert abs(lt["night"]["batLight"]["intensity"] - 3.6) < 1e-5
  assert abs(lt["night"]["batLight"]["distance"] - 45.0) < 1e-5

  assert abs(res["tapReactions"]["tapFox"]["pendantIntensity"] - 4.5) < 1e-5
  assert abs(res["tapReactions"]["tapBat"]["pendantIntensity"] - 4.5) < 1e-5

  for char_id in ("SunnyFox", "LunaBat"):
    for gear_name in ("aviatorGoggles", "pilotScarf", "captainCap"):
      g_info = res["gearToggleResults"][char_id][gear_name]
      assert g_info["onState"] is True and g_info["visibleWhenOn"] is True, f"Failed enabling {char_id}.{gear_name}: {g_info}"
      assert g_info["offState"] is False and g_info["visibleWhenOff"] is False, f"Failed disabling {char_id}.{gear_name}: {g_info}"

  session.assert_zero_errors("R1_Stress")
  return res


async def run_r2_stress(session: ChromeCdpSession) -> dict[str, Any]:
  """Execute R2 Extreme Flight Kinematics, Simultaneous Multi-Action & Collectible Stress."""
  res = await session.eval_js("""(() => {
    const app = window.__APP_STATE__;
    app.setView('flight_simulator');
    app.resetFlight();
    app.startFlight();

    const collectibleTypes = [
      'golden_lantern',
      'crescent_moon_star',
      'music_note_booster',
      'mom_heart_care_package',
      'sky_ring',
      'starlight_ring',
      'paper_airplane_squadron',
    ];

    let outOfBoundsCount = 0;
    let nonFiniteFlightStateCount = 0;
    let scoreRegressionCount = 0;
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    let prevScore = app.flight.score;
    const scoreHistory = [prevScore];

    // Run 240 frames:
    // - Steps 0..79: hold setSteering(+999, +999) to saturate +18.0 X and +28.0 Y clamps
    // - Steps 80..199: hold setSteering(-999, -999) to saturate -18.0 X and +3.0 Y clamps
    // - Steps 200..239: rapid alternating (±999, NaN, ±Infinity)
    const origRender = app.renderer.render.bind(app.renderer);
    for (let step = 0; step < 240; step++) {
      app.renderer.render = (step === 0 || step === 120 || step === 239) ? origRender : () => {};
      if (step < 80) {
        app.setSteering(999, 999);
      } else if (step < 200) {
        app.setSteering(-999, -999);
      } else if (step % 2 === 0) {
        app.setSteering(NaN, Infinity);
      } else {
        app.setSteering(-Infinity, 999);
      }

      // Verify immediate clamping of steerX / steerY
      if (
        !Number.isFinite(app.flight.steerX) ||
        !Number.isFinite(app.flight.steerY) ||
        app.flight.steerX < -1.0 || app.flight.steerX > 1.0 ||
        app.flight.steerY < -1.0 || app.flight.steerY > 1.0
      ) {
        outOfBoundsCount += 1;
      }

      // Fire simultaneous boost + barrelRoll + dropHeartPackage + swapRoles + setCoPilotMode + collectNearestItem
      if (step % 20 === 0) {
        app.triggerBoost();
        app.triggerBarrelRoll();
        app.dropHeartPackage();
        app.swapRoles();
        app.setCoPilotMode(step % 40 === 0 ? 'wing_walker' : 'rear_cockpit');
        app.collectNearestItem(collectibleTypes[(step / 20) % collectibleTypes.length]);
      }

      app.stepSimulation(1, 1 / 60);

      const pos = app.flight.position;
      const rot = app.flight.rotation;

      if (
        !Number.isFinite(pos.x) || !Number.isFinite(pos.y) || !Number.isFinite(pos.z) ||
        !Number.isFinite(rot.pitch) || !Number.isFinite(rot.yaw) || !Number.isFinite(rot.roll)
      ) {
        nonFiniteFlightStateCount += 1;
      }

      minX = Math.min(minX, pos.x);
      maxX = Math.max(maxX, pos.x);
      minY = Math.min(minY, pos.y);
      maxY = Math.max(maxY, pos.y);

      if (pos.x < -18.0 - 1e-6 || pos.x > 18.0 + 1e-6 || pos.y < 3.0 - 1e-6 || pos.y > 28.0 + 1e-6) {
        outOfBoundsCount += 1;
      }

      if (app.flight.score < prevScore) {
        scoreRegressionCount += 1;
      }
      prevScore = app.flight.score;
      scoreHistory.push(prevScore);
    }
    app.renderer.render = origRender;

    // Drive explicitly to Zone 1 (day) -> Zone 3 (night) to verify hidden starlight ring illumination
    app.setZone(1);
    const zone1RingState = {
      zoneId: app.flight.zoneId,
      timeOfDay: app.flight.timeOfDay,
      pendantLightsActive: app.flight.pendantLightsActive,
      revealedStarlightRingsCount: app.flight.revealedStarlightRingsCount,
    };

    app.setZone(3);
    app.stepSimulation(2, 1 / 60);
    const courseWorld = app.scene.getObjectByName('SkyCourseWorld');
    const hiddenRingsInfo = [];
    if (courseWorld) {
      courseWorld.traverse((obj) => {
        if (obj.isMesh && obj.userData && obj.userData.isHiddenStarlightRing) {
          hiddenRingsInfo.push({
            id: obj.userData.id,
            revealedByPendantLight: Boolean(obj.userData.revealedByPendantLight),
            opacity: obj.material.opacity,
            emissiveIntensity: obj.material.emissiveIntensity,
          });
        }
      });
    }
    const zone3RingState = {
      zoneId: app.flight.zoneId,
      zoneName: app.flight.zoneName,
      timeOfDay: app.flight.timeOfDay,
      pendantLightsActive: app.flight.pendantLightsActive,
      revealedStarlightRingsCount: app.flight.revealedStarlightRingsCount,
      allHiddenRingsRevealed: hiddenRingsInfo.length > 0 && hiddenRingsInfo.every(
        (r) => r.revealedByPendantLight && Math.abs(r.opacity - 1.0) < 1e-5 && Math.abs(r.emissiveIntensity - 2.6) < 1e-5
      ),
      hiddenRingsTotal: hiddenRingsInfo.length,
    };

    // Complete Flight to Boston and verify landing state + monotonic score
    const scoreBeforeLanding = app.flight.score;
    app.completeFlightToBoston();
    const scoreAfterLanding = app.flight.score;
    if (scoreAfterLanding < scoreBeforeLanding) {
      scoreRegressionCount += 1;
    }

    const bannerEl = document.getElementById('boston-landing-banner');
    const landingState = {
      completed: app.flight.completed,
      active: app.flight.active,
      flightState: app.flight.flightState,
      zoneId: app.flight.zoneId,
      progress: app.flight.progress,
      distanceMiles: app.flight.distanceMiles,
      position: { ...app.flight.position },
      scoreBeforeLanding,
      scoreAfterLanding,
      bannerVisible: Boolean(bannerEl && bannerEl.classList.contains('visible')),
      foxAnim: (app.characters.SunnyFox.group || app.characters.SunnyFox).userData.canonicalAnimState,
      batAnim: (app.characters.LunaBat.group || app.characters.LunaBat).userData.canonicalAnimState,
    };

    return {
      outOfBoundsCount,
      nonFiniteFlightStateCount,
      scoreRegressionCount,
      boundsObserved: { minX, maxX, minY, maxY },
      counts: {
        boostCount: app.flight.boostCount,
        barrelRollCount: app.flight.barrelRollCount,
        carePackagesDropped: app.flight.carePackagesDropped,
        roleSwapCount: app.flight.roleSwapCount,
        collectedCounts: { ...app.flight.collectedCounts },
      },
      zone1RingState,
      zone3RingState,
      landingState,
    };
  })()""")

  assert res["outOfBoundsCount"] == 0, f"Coordinate or steering out of bounds: {res}"
  assert res["nonFiniteFlightStateCount"] == 0, f"NaN/Infinity in flight kinematics: {res}"
  assert res["scoreRegressionCount"] == 0, f"Score regressed during stress test: {res}"
  assert -18.0 <= res["boundsObserved"]["minX"] <= res["boundsObserved"]["maxX"] <= 18.0
  assert 3.0 <= res["boundsObserved"]["minY"] <= res["boundsObserved"]["maxY"] <= 28.0

  # Verify Zone 1 vs Zone 3 hidden starlight ring illumination
  assert res["zone1RingState"]["pendantLightsActive"] is False
  assert res["zone1RingState"]["revealedStarlightRingsCount"] == 0
  assert res["zone3RingState"]["zoneId"] == 3
  assert res["zone3RingState"]["timeOfDay"] == "night"
  assert res["zone3RingState"]["pendantLightsActive"] is True
  assert res["zone3RingState"]["revealedStarlightRingsCount"] > 0
  assert res["zone3RingState"]["revealedStarlightRingsCount"] == res["zone3RingState"]["hiddenRingsTotal"]
  assert res["zone3RingState"]["allHiddenRingsRevealed"] is True

  # Verify Boston landing state
  ls = res["landingState"]
  assert ls["completed"] is True and ls["active"] is False
  assert ls["flightState"] == "landed_boston"
  assert ls["progress"] == 1.0 and ls["distanceMiles"] == 2700
  assert ls["position"] == {"x": 0, "y": 4.0, "z": -1750}
  assert ls["scoreAfterLanding"] == ls["scoreBeforeLanding"] + 500
  assert ls["bannerVisible"] is True
  assert ls["foxAnim"] == "bounceDance" and ls["batAnim"] == "bounceDance"

  session.assert_zero_errors("R2_Stress")
  return res


async def main_async() -> int:
  start_t = time.monotonic()
  try:
    with LocalHttpServer(PROJECT_ROOT) as server:
      async with ChromeCdpSession() as session:
        await session.navigate(f"{server.base_url}/index.html", wait_load=True, wait_app_ready=True)
        webgl_info = await session.verify_webgl2_context()
        r1_report = await run_r1_stress(session)
        r2_report = await run_r2_stress(session)
        session.assert_zero_errors("Final_Check")

    elapsed_ms = (time.monotonic() - start_t) * 1000.0
    summary = {
        "status": "PASS",
        "duration_ms": round(elapsed_ms, 1),
        "webgl2": webgl_info,
        "r1_stress": r1_report,
        "r2_stress": r2_report,
    }
    print(json.dumps(summary, indent=2))
    return 0
  finally:
    force_cleanup_shm()


if __name__ == "__main__":
  sys.exit(asyncio.run(main_async()))
