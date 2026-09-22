# E2E Test Infrastructure — Smiling Critters 3D Sky & Airplane Adventure (`critters_airplane_3d`)

## 1. Overview & Architecture

Because `node`, `npm`, and `playwright` are not installed on the target host and root disk `/` has a strict space budget, the automated E2E verification suite operates directly over **Chrome DevTools Protocol (CDP)** using:
- **Driver Runtime**: `/usr/bin/python3` (`Python 3.13.15` with pre-installed `asyncio`, `websockets`, `http.server`, and `urllib.request`)
- **Browser Binary**: `/usr/bin/google-chrome` (`Google Chrome 153.0.8010.52`)
- **3D WebGL 2.0 Backend**: Hardware-independent **ANGLE + SwiftShader WebGL 2.0** (`WebGL 2.0 (OpenGL ES 3.0 Chromium)`)

### Mandatory Headless Chrome WebGL 2.0 Launch Flags
To guarantee a real Three.js `r161` `THREE.WebGLRenderer` context (`preserveDrawingBuffer: true`) and valid `canvas.toDataURL('image/png')` exports in headless mode, `tests/cdp_driver.py` launches `/usr/bin/google-chrome` with:

```bash
/usr/bin/google-chrome \
  --headless=new \
  --no-sandbox \
  --use-gl=angle \
  --use-angle=swiftshader \
  --enable-webgl \
  --ignore-gpu-blocklist \
  --enable-unsafe-swiftshader \
  --disable-dev-shm-usage \
  --no-first-run \
  --no-default-browser-check \
  --autoplay-policy=no-user-gesture-required \
  --user-data-dir=/dev/shm/e2e_chrome_<pid>_<uuid> \
  --remote-debugging-port=<free_port> \
  --window-size=1440,900
```

> **Important Note**: Unlike 2D Canvas test drivers, `--disable-gpu` is **intentionally omitted** so that ANGLE + SwiftShader initializes a full `WebGL 2.0 (OpenGL ES 3.0 Chromium)` rendering pipeline. All temporary Chrome profile and cache directories are allocated under `/dev/shm/e2e_chrome_*` and automatically cleaned up via `ChromeCdpSession.close()` and a process-level `atexit` sweep.

---

## 2. Test Suite Organization (`142` E2E Tests Across 4 Tiers)

| File | Responsibility |
|---|---|
| `tests/cdp_driver.py` | Async CDP WebSocket client (`ChromeCdpSession`), background static HTTP server (`LocalHttpServer`), WebGL 2.0 context verifier, PNG `IHDR` binary inspector (`verify_png_data_url`), and `/dev/shm` cleanup lifecycle. |
| `tests/run_e2e_suite.py` | Complete 4-Tier E2E test suite (`142` tests) verifying `F1`–`F11` in `PROJECT.md § Feature Inventory` and `AC-1`–`AC-4` in `ORIGINAL_REQUEST.md`. |

### Tier Breakdown
1. **Tier 1 — Feature Coverage (`66` tests, `6` per feature across `F1`–`F11`)**:
   - `F1` (`T1-F1-01..06`): `SunnyFox` (`LanternFox`) 3D articulated hierarchy (`>1500` vertices), all 16 named sub-groups (`head`, `leftEar`, `rightEar`, `eyes`, `eyePatchLeft`, `leftEyePatchRing`, `muzzle`, `torso`, `zipper`, `lanternPendant`, `leftArm`, `rightArm`, `leftLeg`, `rightLeg`, `tail`, `pilotGear`), asymmetric coral-pink left eye patch (`+X`), exact hex palette, and `#ffd966` `THREE.PointLight`.
   - `F2` (`T1-F2-01..06`): `LunaBat` (`StarBat`) 3D articulated hierarchy (`>1500` vertices), all 14 named sub-groups (`head`, `leftEar`, `rightEar`, `eyes`, `muzzle`, `nose`, `torso`, `zipper`, `moonStarPendant`, `leftWingArm`, `rightWingArm`, `leftLeg`, `rightLeg`, `pilotGear`), diamond-quilted `#9f78d9` spread bat wings with thumb-hooks, upturned bat nose with 2 nostrils, and `#ffe57f` Crescent Moon + 8-Pointed Starburst `THREE.PointLight`.
   - `F3` (`T1-F3-01..06`): All 6 procedural 3D animations (`idle`, `wave`/`joyful_wave`, `wingFlapTailWag`/`wing_flap_tail_wag`, `bounceDance`/`happy_bounce_dance`, `barrelRollCheer`/`barrel_roll_cheer`, `cockpitPilotSteer`/`cockpit_pilot_steer`) and 3D `pilotGear` accessories (`aviatorGoggles`, `pilotScarf`, `captainCap`).
   - `F4` (`T1-F4-01..06`): 360° `OrbitControls`, `triggerCharacterTapReaction` particle bursts (golden fireflies & lavender moon-dust), Web Audio API plush sound synthesizer, and side-by-side reference artwork portrait cards (`custom_critter_fox_lantern.jpg` & `custom_critter_bat_moonstar.jpg`).
   - `F5` (`T1-F5-01..06`): Tandem Cockpit (`pilotSeatAnchor`, `coPilotSeatAnchor`), `swapRoles()`, and `setCoPilotMode('wing_walker' | 'rear_cockpit')`.
   - `F6` (`T1-F6-01..06`): 3D Flight Controls (`setSteering`, `triggerBoost`, `triggerBarrelRoll`, `dropHeartPackage`), aerodynamic attitude updates, and HUD/keyboard bindings.
   - `F7` (`T1-F7-01..06`): 3 Scenic Sky Zones along San Francisco (Golden Gate Bridge) ✈️ Boston (Zakim Bridge), `day`/`sunset`/`night` modes activating pendant `PointLight` illumination of hidden starlight rings, and `completeFlightToBoston()`.
   - `F8` (`T1-F8-01..06`): All 6 collectible classes (`golden_lantern`, `crescent_moon_star`, `music_note_booster`, `mom_heart_care_package`, `sky_ring`/`starlight_ring`, `paper_airplane_squadron`) and score increments.
   - `F9` (`T1-F9-01..06`): 3 selectable 3D aircraft (`biplane`, `supersonic_jet`, `origami_glider` each `>1000` vertices), 4 paint palettes, 3 propeller styles, 4 contrail particle systems, and 4 wing emblems.
   - `F10` (`T1-F10-01..06`): 3D Cockpit & Sky Photo Booth (`capturePostcard()` exporting valid `data:image/png;base64,...` `>5000` bytes) and `localStorage` persistence (`critters_airplane_3d_config_v1` & `critters_airplane_3d_postcards_v1`) across `page.reload()`.
   - `F11` (`T1-F11-01..06`): Offline-first iPad PWA meta tags (`apple-mobile-web-app-capable`), `manifest.json`, `./sw.js`, `docs/.nojekyll`, `docs/index.html`, standalone `dist/index.html`, and the **strict Zero-Grandma invariant**.
2. **Tier 2 — Boundary & Corner Cases (`56` tests, `T2-01..56`)**:
   - Lateral `x ∈ [-18, +18]` and altitude `y ∈ [3, 28]` clamping under extreme steering inputs (`±10`), `NaN`/`Infinity` input guards, rapid 20x role swaps, double-triggered boosts/barrel rolls, invalid ID fallbacks, special/long/empty postcard captions, corrupted `localStorage` recovery, rapid view tab switching, and zero `console.error` / `pageerror` enforcement.
3. **Tier 3 — Cross-Feature Combinations (`14` pairwise tests, `T3-01..14`)**:
   - Multi-feature workflows combining Hangar aircraft/paint/contrail customization, Pilot/Co-Pilot role swapping, Wing-Walker stunts, Zone 3 Night starlight ring illumination, Photo Booth PNG capture, and browser reload persistence.
4. **Tier 4 — Real-World Application Scenarios (`6` end-to-end user journeys, `T4-01..06`)**:
   - Complete iPad Pro user journey from Character Studio inspection → Hangar build → SF Golden Gate takeoff → Zone 2 Rainbow Clouds → Zone 3 Night Aurora Boston landing → Sending 3D Flight Postcard to Mom → `docs/index.html` GitHub Pages verification → `dist/index.html` offline single-file verification.

---

## 3. Running the Test Suite

```bash
cd /usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d
/usr/bin/python3 tests/run_e2e_suite.py
```
