# Project: Smiling Critters 3D Sky & Airplane Adventure: Bay Area ✈️ Boston

## Architecture
- **Overview**: Standalone, zero-backend 3D WebGL / Three.js (`r161`) Interactive Web Application & Flight Adventure Game built for Kunrui's daughter on her iPad in Boston (strictly **Mom in San Francisco / Bay Area ↔ Daughter in Boston** — **ZERO mentions of Grandma** anywhere in code, UI, text, stickers, or audio).
- **3D Engine & Vendor Layout**:
  - Uses local offline Three.js `r161` copied from `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/build/three.min.js` (`window.THREE`) and `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/examples/js/controls/OrbitControls.js` (`window.THREE.OrbitControls`).
  - Single shared `THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true })` across all 4 interactive views (`character_studio`, `flight_simulator`, `hangar`, `photo_booth`) to comply with iPad Safari WebGL context limits and allow instant `canvas.toDataURL('image/png')` capture.
- **Headless Browser WebGL 2.0 Verification Stack**:
  - Because `node`/`npm` are not installed on the host, automated headless browser verification uses `/usr/bin/python3` (`Python 3.13.15` + `websockets`) driving `/usr/bin/google-chrome` (`Chrome 153`) via Chrome DevTools Protocol (CDP) with SwiftShader WebGL 2.0 flags:
    `--headless=new --no-sandbox --use-gl=angle --use-angle=swiftshader --enable-webgl --ignore-gpu-blocklist --enable-unsafe-swiftshader --autoplay-policy=no-user-gesture-required --user-data-dir=/dev/shm/e2e_chrome_<pid>`

## Feature Inventory
Every feature from `ORIGINAL_REQUEST.md` and the Survey phase is mapped below:
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | **3D SunnyFox / LanternFox Rig (`R1.1`)** | Articulated `THREE.Group('SunnyFox')` (`>1500` vertices): `#e89125` plush head/torso, `#f26d6d` ear tips, `#f8e8c8` inner ear fur, forehead/snout center stitch seam, `#f9efd8` muzzle with wide Smiling Critters grin & teeth, 3 upper eyelashes/eye, **asymmetric coral-pink eye patch ring (`#f26d6d`) around her left eye (viewer's right, `+X`)**, `#faefd4` belly, `#e36562` hands/3-toed feet with cream paw pads, bushy tail with `#faf5ea` white tip, brass chest zipper (`#d49b35`), and 3D glowing golden storm lantern pendant (`#ffd966` emissive core inside bronze cage + `THREE.PointLight`). | M1 | ORIGINAL_REQUEST §R1.1, Survey 1 & 2 |
| F2 | **3D LunaBat / StarBat Rig (`R1.2`)** | Articulated `THREE.Group('LunaBat')` (`>1500` vertices): `#3a2278` royal indigo-purple plush head, `#c5a3f0` fluffy lilac-lavender inner ear fur, center forehead stitch seam, `#b898e8` lavender muzzle/lip rim & upturned bat nose with 2 nostrils (`#231252`), `#351e70` torso with `#b592e6` belly patch, `#ba96ea` 3-toed feet, **two articulated spread bat wings** on arms (`leftWingArm`, `rightWingArm`) with `#9f78d9` diamond-quilted membranes & thumb-hooks, silver chest zipper (`#d8dde6`), and 3D glowing golden Crescent Moon + 8-Pointed Starburst pendant (`#ffe57f` emissive glow + `THREE.PointLight`). | M1 | ORIGINAL_REQUEST §R1.2, Survey 1 & 2 |
| F3 | **6 Procedural 3D Animations & Pilot Accessories (`R1.3`)** | Real-time procedural animations for both characters: (1) `idle` (Breathing & Ear Twitch), (2) `wave` / `joyful_wave` (Joyful Wave), (3) `wingFlapTailWag` / `wing_flap_tail_wag` (Wing Flap / Tail Wag), (4) `bounceDance` / `happy_bounce_dance` (Happy Bounce Dance), (5) `barrelRollCheer` / `barrel_roll_cheer` (Barrel-Roll Cheer), and (6) `cockpitPilotSteer` / `cockpit_pilot_steer` (Cockpit Pilot Steer), plus toggleable 3D `pilotGear` (`aviatorGoggles`, `pilotScarf`, `captainCap`). | M1 | ORIGINAL_REQUEST §R1.3, Survey 2 |
| F4 | **360° Studio OrbitControls, Tap-to-React Particles, Synth Audio & Reference Cards (`R1.3`)** | Interactive 360° `OrbitControls`, raycast tap-to-react animations with synthesized Web Audio API plush sound effects (`soundSynth`) & 3D particle bursts (lantern fireflies for Fox, lavender moon-dust for Bat), and side-by-side reference portrait cards displaying `assets/custom_critter_fox_lantern.jpg` and `assets/custom_critter_bat_moonstar.jpg`. | M1 | ORIGINAL_REQUEST §R1.3, Survey 1 & 2 |
| F5 | **Tandem Cockpit & Co-Pilot Wing-Walker Role Swap (`R2.1`)** | Both 3D characters sit inside (`pilotSeatAnchor`, `coPilotSeatAnchor`) or wing-walk on (`coPilotMode: 'wing_walker'`) the 3D airplane in real time, with 1-tap Pilot ↔ Co-Pilot role swap (`swapRoles()`). | M1 | ORIGINAL_REQUEST §R2, Survey 3 |
| F6 | **3D Flight Controls & Stunts (`R2.2`)** | Responsive iPad virtual thumbstick / touch-drag + desktop `WASD`/Arrows steering (`setSteering`), **Turbo Starlight Boost** (`triggerBoost`), **360° Barrel Roll / Loop-de-Loop Stunt** (`triggerBarrelRoll`), and **Heart Parachute Care-Package Drop** (`dropHeartPackage`). | M1 | ORIGINAL_REQUEST §R2, Survey 3 |
| F7 | **3 Scenic Sky Zones (SF ✈️ Boston) & Time-of-Day Pendant Illumination (`R2.3`)** | Fly from Mom in SF (Golden Gate Bridge) to Daughter in Boston (Zakim Bridge & Skyline) across **Zone 1: Golden Gate Sunrise Takeoff**, **Zone 2: Rainbow Cloud Archipelago & Paper-Airplane Wind Tunnels**, and **Zone 3: Starry Night Aurora Approach into Boston** (`day`, `sunset`, `night` lighting modes where Fox's lantern & Bat's moon-star `THREE.PointLight`s illuminate hidden starlight rings in the dark), plus full Boston landing celebration (`completeFlightToBoston`). | M1 | ORIGINAL_REQUEST §R2, Survey 3 |
| F8 | **6 Collectible Classes & Scoring (`R2.4`)** | Collect floating **Golden Lanterns** (`golden_lantern`), **Crescent Moon Stars** (`crescent_moon_star`), **Music Note Boosters** (`music_note_booster`), **Mom's Heart Care Packages** (`mom_heart_care_package`), glowing **3D Sky/Starlight Rings** (`sky_ring`, `starlight_ring`), and **Paper-Airplane Squadrons** (`paper_airplane_squadron`). | M1 | ORIGINAL_REQUEST §R2, Survey 3 |
| F9 | **3 Selectable 3D Airplanes & Hangar Customizer (`R3.1–R3.2`)** | Switch between (1) **Critter Cloud Biplane** (`biplane`), (2) **Starlight Supersonic Jet** (`supersonic_jet`), and (3) **Origami Dream Glider** (`origami_glider`); customize 4 paint palettes (`sunset_fox_amber`, `midnight_bat_indigo`, `huntrx_golden_neon`, `mint_cloud`), 3 propeller styles, 4 contrail particle systems (`rainbow_ribbon`, `lantern_fireflies`, `starlight_moon_dust`, `heart_bubbles`), and 4 wing emblems. | M1 | ORIGINAL_REQUEST §R3, Survey 3 |
| F10 | **3D Cockpit & Sky Photo Booth & `localStorage` Persistence (`R3.3`)** | "Send 3D Flight Postcard to Mom" posing both 3D characters with their custom airplane against SF/Boston backdrops, adding stickers/captions, exporting a high-res PNG (`canvas.toDataURL('image/png')` via `capturePostcard()`), and persisting custom planes (`critters_airplane_3d_config_v1`) & postcards (`critters_airplane_3d_postcards_v1`) across reloads in `localStorage`. | M1 | ORIGINAL_REQUEST §R3, Survey 3 |
| F11 | **Offline-First iPad PWA, `docs/` GitHub Pages & Single-File `dist/index.html` (`R4`)** | iPad PWA meta tags (`apple-mobile-web-app-capable`), `manifest.json`, `./sw.js` Service Worker caching all 3D engine/code/assets offline, modular `src/`, GitHub Pages `docs/` (with `.nojekyll` and `assets/`), and single-file bundle `dist/index.html` built by `scripts/build_dist.py`. | M1 | ORIGINAL_REQUEST §R4, Survey 1 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | **Unified 3D WebGL Application, PWA & Bundles (`R1–R4`)** | Implement complete `src/`, `index.html`, `manifest.json`, `sw.js`, `scripts/build_dist.py`, `docs/`, and `dist/index.html` with `window.__APP_STATE__` contract (`worker_impl_1`). | Survey (Done) | DONE (`142/142` E2E passed) |
| E2E | **Opaque-Box Headless Chromium WebGL 2.0 E2E Test Suite (`Tiers 1–4`)** | Create `TEST_INFRA.md`, `tests/cdp_driver.py`, `tests/run_e2e_suite.py`, and `TEST_READY.md` (`test_writer_e2e`). | Survey (Done) | DONE (`142/142` E2E passed) |
| M2 | **Gate Verification & Tier 5 Adversarial Coverage Hardening** | 2 Reviewers (`reviewer_1`, `reviewer_2`), 2 Challengers (`challenger_1`, `challenger_2`), and 1 Forensic Auditor (`auditor_1`) verify 100% E2E pass and integrity. | M1, E2E | DONE (`Gate Result: PASS`) |

## Code Layout
```text
/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/
├── index.html                        # Root modular entry point
├── manifest.json                     # iPad PWA Web App Manifest
├── sw.js                             # Offline-First Service Worker
├── assets/
│   ├── custom_critter_fox_lantern.jpg
│   └── custom_critter_bat_moonstar.jpg
├── src/
│   ├── vendor/
│   │   ├── three.min.js              # Local copy from google3/third_party/javascript/threejs/r161/build/three.min.js
│   │   └── OrbitControls.js          # Local copy from google3/third_party/javascript/threejs/r161/examples/js/controls/OrbitControls.js
│   ├── styles/
│   │   └── main.css
│   ├── characters/                   # R1 SunnyFox & LunaBat 3D rigs, textures, animations & particles
│   ├── aircraft/                     # R3 3D Biplane, Supersonic Jet, Origami Glider & contrail systems
│   ├── flight/                       # R2 SF -> Boston 3-Zone course, landmarks, collectibles & flight physics
│   ├── audio/                        # Web Audio API plush sound & flight synthesizer
│   └── main.js                       # App controller, UI bindings, localStorage & window.__APP_STATE__
├── docs/                             # GitHub Pages-ready folder (.nojekyll, index.html, manifest.json, sw.js, assets/, vendor/, src/)
├── dist/
│   └── index.html                    # Self-contained single-file bundle (inlines CSS, Three.js, OrbitControls, base64 assets & app JS)
├── scripts/
│   └── build_dist.py                 # Python 3 build script producing docs/ and dist/index.html
└── tests/
    ├── cdp_driver.py                 # Headless Chrome 153 WebGL 2.0 CDP driver
    └── run_e2e_suite.py              # Comprehensive Tier 1-4 E2E test runner
```

## Interface Contracts

### Unified `window.__APP_STATE__` Contract (Mandatory for `worker_impl_1` & `test_writer_e2e`)
To ensure seamless compatibility across all verification scripts, `window.__APP_STATE__` MUST expose:
1. **Engine & Readiness**:
   - `ready`: `true` once Three.js scene, characters, aircraft, and `localStorage` are initialized.
   - `activeView`: `'character_studio' | 'flight_simulator' | 'hangar' | 'photo_booth'`
   - `renderer`: `THREE.WebGLRenderer` (`preserveDrawingBuffer: true`)
   - `scene`: `THREE.Scene`
   - `camera`: `THREE.PerspectiveCamera`
   - `frameCount`: number, `elapsedTime`: number
2. **`characters` Object (supports BOTH `SunnyFox`/`sunnyFox` and `LunaBat`/`lunaBat` keys)**:
   - `window.__APP_STATE__.characters.SunnyFox` (and alias `window.__APP_STATE__.characters.sunnyFox` pointing to the `THREE.Group` or wrapper where `.group` is the root `THREE.Group('SunnyFox')` and `.getObjectByName(...)` works on both the wrapper and `.group`!):
     - Specifically: attach all metadata properties (`id: 'SunnyFox'`, `displayName: 'SunnyFox (LanternFox)'`, `group: sunnyFoxGroup`, `vertexCount`, `meshCount`, `currentAnimation`, `pendantLight`, `pendantEmissiveMesh`, `parts`) directly onto `sunnyFoxGroup` AND expose `window.__APP_STATE__.characters.SunnyFox = sunnyFoxGroup` AND `window.__APP_STATE__.characters.sunnyFox = sunnyFoxGroup` (with `sunnyFoxGroup.group = sunnyFoxGroup`). That way, whether a test accesses `characters.SunnyFox.group.getObjectByName('lanternPendant')`, `characters.sunnyFox.getObjectByName('lanternPendant')`, `characters.SunnyFox.vertexCount`, or `characters.SunnyFox.pendantLight.intensity`, **BOTH work identically**!
     - Do the exact same for `LunaBat`: `lunaBatGroup.group = lunaBatGroup`, attach `id: 'LunaBat'`, `displayName: 'LunaBat (StarBat)'`, `vertexCount`, `meshCount`, `currentAnimation`, `pendantLight`, `pendantEmissiveMesh`, `parts` onto `lunaBatGroup`, and set `window.__APP_STATE__.characters.LunaBat = lunaBatGroup` and `window.__APP_STATE__.characters.lunaBat = lunaBatGroup`.
   - Required named child groups on `SunnyFox` (`sunnyFoxGroup.getObjectByName(...)`):
     `head`, `leftEar`, `rightEar`, `eyes`, `eyePatchLeft`, `leftEyePatchRing`, `muzzle`, `torso`, `zipper`, `lanternPendant`, `leftArm`, `rightArm`, `leftLeg`, `rightLeg`, `tail`, `pilotGear`.
   - Required named child groups on `LunaBat` (`lunaBatGroup.getObjectByName(...)`):
     `head`, `leftEar`, `rightEar`, `eyes`, `muzzle`, `nose`, `torso`, `zipper`, `moonStarPendant`, `leftWingArm`, `rightWingArm`, `leftLeg`, `rightLeg`, `pilotGear`.
3. **`flight` State Object**:
   - `active`, `paused`, `completed`, `flightState` (`'ready_sf' | 'cruising' | 'approaching_boston' | 'landed_boston'`), `originCity` (`'San Francisco (Golden Gate Bridge)'`), `destinationCity` (`'Boston (Zakim Bridge & Skyline)'`), `pilotId` (`'SunnyFox' | 'LunaBat'`), `coPilotId` (`'LunaBat' | 'SunnyFox'`), `coPilotMode` (`'rear_cockpit' | 'wing_walker'`), `roleSwapCount`, `zoneId` (`1 | 2 | 3`), `zoneName`, `timeOfDay` (`'day' | 'sunset' | 'night'`), `pendantLightsActive` (`boolean`), `revealedStarlightRingsCount` (`number`), `progress` (`0..1`), `distanceMiles` (`0..2700`), `speed`, `steerX`, `steerY`, `position` (`{x, y, z}`), `rotation` (`{pitch, yaw, roll}`), `boostActive`, `boostCount`, `barrelRollActive`, `barrelRollCount`, `carePackagesDropped`, `score`, `ringsPassed`, `collectedCounts` (`{ golden_lantern, crescent_moon_star, music_note_booster, mom_heart_care_package, sky_ring, starlight_ring, paper_airplane_squadron }`).
4. **`hangar` State Object**:
   - `modelId` (`'biplane' | 'supersonic_jet' | 'origami_glider'`), `paintPaletteId` (`'sunset_fox_amber' | 'midnight_bat_indigo' | 'huntrx_golden_neon' | 'mint_cloud'`), `propellerStyleId` (`'classic_wood_brass' | 'starlight_crystal_turbine' | 'rainbow_flower_pinwheel'`), `contrailStyleId` (`'rainbow_ribbon' | 'lantern_fireflies' | 'starlight_moon_dust' | 'heart_bubbles'`), `wingEmblemId` (`'fox_lantern_crest' | 'bat_moonstar_crest' | 'sf_boston_heart_wings' | 'golden_star_crown'`), `airplaneGroup`, `pilotSeatAnchor`, `coPilotSeatAnchor`, `propellerGroup`, `contrailSystem`, `vertexCount` (`>1200`), `primaryColorHex`, `secondaryColorHex`, `storageKey` (`'critters_airplane_3d_config_v1'`).
5. **`photoBooth` State Object**:
   - `backdropId`, `poseId`, `captionText`, `stickerIds`, `lastCapturedDataUrl` (`'data:image/png;base64,...'`), `savedPostcards` (`Array`), `storageKey` (`'critters_airplane_3d_postcards_v1'`).
6. **Programmatic Control Methods on `window.__APP_STATE__`**:
   - `setView(view)`
   - `stepSimulation(frames = 1, dt = 1/60)` (accepts either `(frames, dt)` or `(dt)` if first arg `< 1.0` so `stepSimulation(0.25)` and `stepSimulation(30, 1/60)` both advance simulation cleanly!)
   - `setCharacterAnimation(charIdOrAnimName, maybeAnimName)` (if called with 1 arg `setCharacterAnimation('wave')`, sets animation on both characters; if called with 2 args `setCharacterAnimation('SunnyFox', 'wave')`, sets on target character. Normalizes both camelCase and snake_case animation names!)
   - `triggerCharacterTapReaction(charId)`
   - `swapRoles()` → returns `{ pilotId, coPilotId, roleSwapCount }`
   - `setCoPilotMode(mode)`
   - `startFlight()`, `resetFlight()`, `setSteering(steerX, steerY)`, `triggerBoost()`, `triggerBarrelRoll()`, `dropHeartPackage()`, `collectNearestItem(type)`, `setZone(zoneId)`, `setTimeOfDay(mode)`, `completeFlightToBoston()`
   - `setPlaneModel(modelId)`, `setPaintPalette(paletteId)`, `setPropellerStyle(styleId)`, `setContrailStyle(styleId)`, `setWingEmblem(emblemId)`
   - `setPhotoBackdrop(backdropId)`, `setPhotoPose(poseId)`, `setPhotoCaption(text)`, `capturePostcard()` → returns `{ id, dataUrl, width, height, captionText, backdropId }`
   - `saveConfigToLocalStorage()`, `loadConfigFromLocalStorage()`
