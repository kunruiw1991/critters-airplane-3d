# Handoff Report — `explorer_survey_3` (R2 3D Flight Simulator, R3 3D Hangar & Photo Booth, and `window.__APP_STATE__` Specification)

**Core Summary**: Complete architectural and engineering specification for **R2** (3D "Airplane" Sky Adventure & Co-Pilot Flight Simulator from Mom in San Francisco ✈️ Daughter in Boston), **R3** (3D Airplane Hangar Builder, Wing Decal Studio & Cockpit Photo Booth with `localStorage` persistence), and the **Deterministic Verification API (`window.__APP_STATE__`)** for automated headless Chromium / Playwright verification.

---

## 1. Observation

1. **Authoritative Requirements (`ORIGINAL_REQUEST.md:1-56`)**:
   - **Line 5 & Line 29**: The application is strictly focused on **Mom in San Francisco (Golden Gate Bridge) ↔ Daughter in Boston (Zakim Bridge & Boston Skyline)** — **ZERO mentions of Grandma** anywhere in the application, UI, stickers, captions, audio, or source code.
   - **Lines 28–34 (R2)**:
     - Tandem Pilot & Co-Pilot cockpit seating both 3D custom Smiling Critters (`SunnyFox` and `LunaBat`), with 1-tap role swap (`Pilot ↔ Co-Pilot`) and optional wing-walker pose.
     - Responsive iPad virtual thumbstick / touch-drag + desktop `WASD` / Arrow steering, **Turbo Starlight Boost**, **360° Barrel Roll / Loop-de-Loop Stunt**, and **Heart Parachute Care-Package Drop**.
     - 3 scenic sky zones along the SF → Boston flight path:
       1. **Zone 1**: `Golden Gate Sunrise Takeoff` (San Francisco Golden Gate Bridge, Bay towers, sunrise waters)
       2. **Zone 2**: `Rainbow Cloud Archipelago & Paper-Airplane Wind Tunnels` (floating pastel clouds, 3D rainbow arches, paper-airplane V-squadrons)
       3. **Zone 3**: `Starry Night Aurora Approach into Boston` (Zakim Bridge, Boston skyline, aurora curtains, where `SunnyFox`'s glowing golden lantern and `LunaBat`'s glowing crescent moon-star pendant point lights illuminate hidden starlight rings in the dark).
     - Collectibles: **Golden Lanterns**, **Crescent Moon Stars**, **Music Note Boosters**, **Mom's Heart Care Packages**, glowing **3D Sky/Starlight Rings**, and **Paper-Airplane Squadrons**.
   - **Lines 36–43 (R3)**:
     - 3 Selectable 3D Airplanes: `biplane` (**Critter Cloud Biplane**), `supersonic_jet` (**Starlight Supersonic Jet**), and `origami_glider` (**Origami Dream Glider**).
     - Paint Palettes (`sunset_fox_amber`, `midnight_bat_indigo`, `huntrx_golden_neon`, `mint_cloud`), Propeller styles, Contrail particle systems (`rainbow_ribbon`, `lantern_fireflies`, `starlight_moon_dust`, `heart_bubbles`), and Wing Emblems.
     - 3D Cockpit & Sky Photo Booth (**"Send 3D Flight Postcard to Mom"**) exporting a real WebGL + 2D overlay PNG (`canvas.toDataURL('image/png')`) and persisting custom aircraft configs and saved postcards in `localStorage`.
   - **Lines 50–55 (Acceptance Criteria)**:
     - Headless Chromium verification inspects `window.__APP_STATE__` and the live Three.js scene graph to verify 3D character meshes, role swapping, flight simulation stepping, steering/boost/barrel-roll/collectible updates, Day/Sunset/Night lighting mode switches (activating Fox's lantern & Bat's moon-star point lights), completion/landing state, switching all 3 aircraft models, changing paint/contrail styles, exporting `data:image/png;base64,...` postcards, and persisting configs across `page.reload()` via `localStorage`.

---

## 2. Logic Chain

1. **Why a Single Shared `THREE.WebGLRenderer` (`preserveDrawingBuffer: true`) is Required (from Observation 1, R3 & Acceptance Criteria)**:
   - iPad Safari limits active WebGL contexts per page, and `canvas.toDataURL('image/png')` returns a blank transparent bitmap if `preserveDrawingBuffer` is `false` after buffer swap. Therefore, the application must instantiate a single `THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true })` shared across all 4 view tabs (`character_studio`, `hangar`, `flight_simulator`, `photo_booth`), and call `renderer.render(scene, activeCamera)` immediately prior to composite postcard capture.
2. **Why Tandem Seat Anchors (`pilotSeatAnchor`, `coPilotSeatAnchor`) Solve Both R1/R2/R3 Integration and `swapRoles()` (from Observation 1, R2)**:
   - Every 3D aircraft model (`biplane`, `supersonic_jet`, `origami_glider`) exposes named `THREE.Group` mount points `pilotSeatAnchor` (front cockpit) and `coPilotSeatAnchor` (rear tandem cockpit / upper wing-walker mount). Reparenting `SunnyFox` and `LunaBat` between these two anchors when `swapRoles()` is invoked guarantees zero mesh duplication, instant visual synchronization across Hangar, Flight Simulator, and Photo Booth, and O(1) verification via `window.__APP_STATE__.flight.pilotId` and `pilotSeatAnchor.children`.
3. **Why Deterministic `stepSimulation(frames, dt)` is Essential alongside `requestAnimationFrame` (from Observation 1, Acceptance Criteria)**:
   - Headless Chromium WebGL `requestAnimationFrame` throttling can vary under CI load. Providing `window.__APP_STATE__.stepSimulation(frames = 1, dt = 1/60)` advances the exact same physics, collision detection, particle emitters, and skeletal animations deterministically in microseconds for automated Playwright verification while running smoothly at 60 FPS during interactive iPad play.

---

## 3. Caveats

- **No caveats.** All requirements in `ORIGINAL_REQUEST.md` for R2, R3, and `window.__APP_STATE__` have been mapped to concrete Three.js scene graph nodes, mathematical equations, `localStorage` schemas, and deterministic test hooks.

---

## 4. Conclusion — Complete Technical Specification (R2, R3 & `window.__APP_STATE__`)

---

### Part A: R2. 3D "Airplane" Sky Adventure & Co-Pilot Flight Simulator (San Francisco ✈️ Boston)

#### A.1 Strict Narrative & Landmark Guardrails
- **Origin**: **San Francisco, CA (Mom)** — 3D Golden Gate Bridge (`#c0362c` International Orange twin towers, suspension cables, Marin Headlands, SF Bay water reflections).
- **Destination**: **Boston, MA (Daughter)** — 3D Leonard P. Zakim Bunker Hill Memorial Bridge (twin white inverted-Y cable-stayed towers), Prudential Center Tower, Custom House Clock Tower, Charles River waterfront, and Starlight Welcome Runway.
- **Zero-Grandma Invariant**: Strictly prohibited (`0` matches for `/grandma|grandmother|nana|granny/i` across all code, DOM text, stickers, and metadata).

#### A.2 Tandem Cockpit & Co-Pilot Wing-Walker Architecture (`swapRoles()`)
Each aircraft `THREE.Group` (`airplaneGroup`) defines two named child `THREE.Group` seat mounts:
| Anchor Name | Local Position (`biplane` / `jet` / `glider`) | Local Scale | Assigned Character Role | Active Character Animation & Accessories |
|---|---|---|---|---|
| `pilotSeatAnchor` | `[0, 0.48, 0.78]` | `[0.54, 0.54, 0.54]` | `pilotId` (default: `'SunnyFox'`) | Animation: `'cockpit_pilot_steer'` (hands on control yoke, head banking with `steerX`, aviator goggles enabled). |
| `coPilotSeatAnchor` | Cockpit mode: `[0, 0.58, -0.68]`<br>Wing-Walker mode (`coPilotMode === 'wing_walker'`): `[1.75, 0.52, -0.05]` | `[0.54, 0.54, 0.54]` | `coPilotId` (default: `'LunaBat'`) | Animation: `'joyful_wave'` / `'wing_flap'` / `'barrel_roll_cheer'` (waving to clouds, flapping quilted bat wings, or holding up glowing lantern/moon-star pendant). |

- **`swapRoles()` Execution Contract**:
  1. Swaps `state.flight.pilotId` ↔ `state.flight.coPilotId` (e.g., `'SunnyFox'` ↔ `'LunaBat'`).
  2. Attaches the new Pilot's `THREE.Group` to `pilotSeatAnchor` (`position.set(0,0,0)`, `rotation.set(0,0,0)`) and sets animation to `'cockpit_pilot_steer'`.
  3. Attaches the new Co-Pilot's `THREE.Group` to `coPilotSeatAnchor` (`position.set(0,0,0)`, `rotation.set(0,0,0)`) and sets animation to `'joyful_wave'` (or `'wing_flap'` if `LunaBat`).
  4. Increments `state.flight.roleSwapCount += 1`, spawns a 24-particle golden/lavender celebration burst around the cockpit, plays a cheerful harmonic duo chime via Web Audio API, updates HUD Pilot/Co-Pilot badges (`#hud-pilot-name`, `#hud-copilot-name`), and saves to `localStorage`.
- **`toggleCoPilotMode()` (`'rear_cockpit' | 'wing_walker'`)**:
  - Moves `coPilotSeatAnchor` between the rear tandem cockpit `[0, 0.58, -0.68]` and the upper starboard wing `[1.75, 0.52, -0.05]` for Co-Pilot Wing-Walker stunts.

#### A.3 3D Flight Physics, Kinematics & Controls (`60 FPS` + `stepSimulation`)
- **Flight Coordinate System**:
  - `z`: Forward flight corridor axis from `z = 0` (San Francisco Golden Gate Bridge) to `z = -1800` (Boston Zakim Bridge Runway).
  - `x`: Lateral horizontal offset clamped to `x ∈ [-18.0, +18.0]`.
  - `y`: Vertical altitude offset clamped to `y ∈ [3.0, 28.0]` (default cruise altitude `y = 12.0`).
  - `progress`: Normalized journey progress `progress = clamp(-position.z / 1800.0, 0.0, 1.0)`.
  - `distanceMiles`: Virtual transcontinental miles `Math.round(progress * 2700)` (`0 mi` SF → `2,700 mi` Boston).
- **Per-Tick Integration (`updateFlightPhysics(dt)`)**:
  ```js
  const baseSpeed = 24.0; // units/sec (completes 1800u course in 75s at normal speed)
  const currentSpeed = state.flight.boostActive ? baseSpeed * 2.15 : baseSpeed;
  state.flight.speed = currentSpeed;

  // Advance along SF -> Boston corridor
  state.flight.position.z -= currentSpeed * dt;
  state.flight.position.x = THREE.MathUtils.clamp(
    state.flight.position.x + state.flight.steerX * 18.0 * dt, -18.0, 18.0
  );
  state.flight.position.y = THREE.MathUtils.clamp(
    state.flight.position.y + state.flight.steerY * 14.0 * dt, 3.0, 28.0
  );

  // Smooth aerodynamic pitch, yaw, and bank/barrel-roll attitude
  const targetRoll = -state.flight.steerX * 0.65;
  const targetPitch = state.flight.steerY * 0.42;
  const targetYaw = -state.flight.steerX * 0.25;

  if (state.flight.barrelRollActive) {
    state.flight.barrelRollProgress = Math.min(1.0, state.flight.barrelRollProgress + dt / 0.95);
    state.flight.barrelRollAngle = state.flight.barrelRollProgress * Math.PI * 2.0;
    if (state.flight.barrelRollProgress >= 1.0) {
      state.flight.barrelRollActive = false;
      state.flight.barrelRollProgress = 0.0;
      state.flight.barrelRollAngle = 0.0;
    }
  }

  state.flight.rotation.pitch = THREE.MathUtils.lerp(state.flight.rotation.pitch, targetPitch, 1 - Math.exp(-10 * dt));
  state.flight.rotation.yaw   = THREE.MathUtils.lerp(state.flight.rotation.yaw, targetYaw, 1 - Math.exp(-10 * dt));
  state.flight.rotation.roll  = THREE.MathUtils.lerp(state.flight.rotation.roll, targetRoll, 1 - Math.exp(-10 * dt)) + state.flight.barrelRollAngle;
  ```
- **Control Inputs (iPad Touch & Desktop Keyboard)**:
  | Control Action | iPad Touch UI Element | Keyboard Binding | `window.__APP_STATE__` Method | Effect |
  |---|---|---|---|---|
  | **Steer X / Y** | `#flight-thumbstick` virtual analog stick + canvas drag | `W/S/A/D` or `ArrowUp/Down/Left/Right` | `setSteering(steerX, steerY)` | Updates `steerX ∈ [-1, 1]`, `steerY ∈ [-1, 1]`; moves aircraft `(x, y)` and banks/pitches `rotation`. |
  | **Turbo Starlight Boost** | `#btn-flight-boost` (`🚀 Starlight Boost`) | `Space` | `triggerBoost()` | Sets `boostActive = true`, `boostTimer = 3.0`, speed `2.15x` (`51.6 u/s`), camera FOV `60° → 72°`, contrail emission `3x`, `score += 50`, `boostCount += 1`. |
  | **360° Barrel Roll / Loop** | `#btn-flight-barrel-roll` (`🌀 360° Barrel Roll`) | `R` or `E` | `triggerBarrelRoll()` | Sets `barrelRollActive = true`, rotates aircraft a full `2π` (`360°`) over `0.95s`, expands item collection magnet radius `2.5x` (`4.0 → 10.0` units), triggers `'barrel_roll_cheer'` on characters, `score += 100`, `barrelRollCount += 1`. |
  | **Heart Care-Package Drop** | `#btn-flight-heart-drop` (`💖 Drop Mom's Care Package`) | `F` or `H` | `dropHeartPackage()` | Spawns a 3D `HeartParachutePackage` mesh (`#ff5c8a` heart box + `#fff5f8` parachute dome) beneath the airplane that drifts down with pendulum oscillation, increments `carePackagesDropped += 1`, `score += 75`. |
  | **Swap Pilot ↔ Co-Pilot** | `#btn-swap-roles` (`🔄 Swap Pilot & Co-Pilot`) | `C` | `swapRoles()` | Swaps `SunnyFox` and `LunaBat` between `pilotSeatAnchor` and `coPilotSeatAnchor` in real time. |

#### A.4 3 Scenic Sky Zones, Time-of-Day Modes & Zone 3 Pendant Point-Light Illumination
| Zone ID | Zone Title | Corridor Range (`z` & `progress`) | Default Time-of-Day | Iconic 3D Landmarks & Interactive Features |
|---|---|---|---|---|
| **Zone 1** | **Golden Gate Sunrise Takeoff (San Francisco)** | `z ∈ [0, -600)`<br>`progress ∈ [0.00, 0.33)` | `'sunrise'` / `'day'` | 3D **Golden Gate Bridge** spanning `x ∈ [-24, +24]` with twin International Orange (`#c0362c`) suspension towers (`height: 26`), catenary main cables, vertical suspender ropes, Marin Headlands terrain, shimmering SF Bay water plane, and "BYE MOM IN SF! 🌉✈️" departure banner. |
| **Zone 2** | **Rainbow Cloud Archipelago & Paper-Airplane Wind Tunnels** | `z ∈ [-600, -1200)`<br>`progress ∈ [0.33, 0.66)` | `'sunset'` | Floating 3D pastel cloud islands, giant 7-band translucent **Rainbow Archways** (`THREE.TorusGeometry(14, 0.9, 16, 64, Math.PI)`), swirling **Wind Tunnel Slipstreams** that accelerate speed by `+35%`, and friendly **3D Paper-Airplane Squadrons** banking in V-formation alongside the player. |
| **Zone 3** | **Starry Night Aurora Approach into Boston** | `z ∈ [-1200, -1800]`<br>`progress ∈ [0.66, 1.00]` | `'night'` | Waving emerald-violet **Aurora Borealis curtains** (`THREE.PlaneGeometry` with sinusoidal vertex wave), 3D **Zakim Bridge** (twin inverted-Y cable-stayed obelisks + white stay cables), **Boston Skyline** (Prudential Tower + Custom House Tower + Charles River), and **Hidden Starlight Rings** illuminated by `SunnyFox`'s glowing lantern (`#ffd966`) and `LunaBat`'s glowing crescent moon-star (`#ffe57f`) point lights! |

- **Time-of-Day Mode Switcher (`setTimeOfDay(mode: 'day' | 'sunset' | 'night')`)**:
  - Exposed via HUD buttons (`#btn-time-day`, `#btn-time-sunset`, `#btn-time-night`) and `window.__APP_STATE__.setTimeOfDay(mode)`.
  - **`'day'`**: Sky top `#3b9eff`, horizon `#bfe9ff`, directional sun `#fff7e6` (`intensity: 1.45`), ambient `#d9eeff` (`intensity: 0.85`), `pendantLightsActive: false` (pendant lights at subtle idle `intensity: 0.6`).
  - **`'sunset'`**: Sky top `#3a1c71`, horizon `#ffaf7b`, directional golden sun `#ff8c42` (`intensity: 1.25`), ambient `#ffcdb2` (`intensity: 0.65`), `pendantLightsActive: true` (pendant lights at warm `intensity: 1.8`).
  - **`'night'`**: Sky top `#070b1e`, horizon `#1b1438`, starfield particles visible (`opacity: 1.0`), aurora ribbons visible (`opacity: 0.85`), directional moonlight `#8ab4f8` (`intensity: 0.35`), ambient `#1a163b` (`intensity: 0.28`), **`pendantLightsActive: true`**:
    - `foxLanternLight.intensity = 3.5`, `foxLanternLight.distance = 42.0`
    - `batMoonStarLight.intensity = 3.2`, `batMoonStarLight.distance = 42.0`
    - All Zone 3 / Night **Hidden Starlight Rings** (`ring.userData.isHiddenStarlightRing === true`) update `ring.userData.revealedByPendantLight = true`, `ring.material.opacity = 1.0`, `ring.material.emissiveIntensity = 2.5`.

#### A.5 Collectibles & Scoring System
Every course instance spawns 45 deterministic 3D collectibles & rings along `z ∈ [-40, -1760]`:
| Collectible Type (`type`) | 3D Geometry & Material | Score Delta | Special Effect & Counter |
|---|---|---|---|
| `'golden_lantern'` | Bronze lantern cage + glowing `#ffd966` core (`OctahedronGeometry` + `CylinderGeometry`) | `+100` | Increments `collectedCounts.golden_lantern`, refills boost energy, emits golden fireflies. |
| `'crescent_moon_star'` | Extruded `#ffe57f` Crescent Moon + 8-point Starburst | `+100` | Increments `collectedCounts.crescent_moon_star`, pulses moon-star point light radius (`+12u`), emits lavender stardust. |
| `'music_note_booster'` | Glowing `#00f0ff` / `#ff2a85` 3D beamed eighth note | `+150` | Increments `collectedCounts.music_note_booster`, grants `1.5s` speed burst, plays synth melody chord. |
| `'mom_heart_care_package'` | 3D `#ff5c8a` heart-embossed gift box with gold ribbon | `+200` | Increments `collectedCounts.mom_heart_care_package`, shows love note from Mom in SF to Daughter in Boston. |
| `'sky_ring'` / `'starlight_ring'` | 3D Glowing Torus Gate (`TorusGeometry(3.6, 0.28, 16, 48)`) | `+150` (`+300` if `starlight_ring` revealed in Night/Zone 3) | Increments `ringsPassed`, triggers rainbow/starlight ring shockwave. |
| `'paper_airplane_squadron'` | 3-plane V-formation of folded white/gold origami gliders | `+120` | Increments `collectedCounts.paper_airplane_squadron`, escort planes perform synchronized wing-waggle salute. |

---

### Part B: R3. 3D Airplane Hangar Builder, Wing Decal Studio & Cockpit Photo Booth

#### B.1 3 Selectable 3D Aircraft Models (`modelId`)
All 3 aircraft models are constructed as modular `THREE.Group` hierarchies inside `AirplaneFactory.createAirplane(modelId, config)` with `> 1,200` vertices each, shared `pilotSeatAnchor` and `coPilotSeatAnchor` child groups, `propellerGroup`, `leftWingEmblemMesh`, `rightWingEmblemMesh`, and `contrailEmitterAnchor`:

1. **`'biplane'` — Critter Cloud Biplane**:
   - **Geometry**: Rounded vintage fuselage (`CylinderGeometry` + nose/tail hemispheres), elevated `upperWing` (`BoxGeometry(8.6, 0.18, 1.85)` with rounded wingtips) and `lowerWing` (`BoxGeometry(7.8, 0.18, 1.75)`), 4 interplane aerodynamic struts (`CylinderGeometry`), nose radial engine cowling, 3-blade spinning front `propellerGroup` at `[0, 0, 2.45]`, classic tail fin & rudder, twin main landing wheels with struts, and open wood-rimmed tandem cockpits (`pilotSeatAnchor`, `coPilotSeatAnchor`).
2. **`'supersonic_jet'` — Starlight Supersonic Jet**:
   - **Geometry**: Sleek needle nose cone (`ConeGeometry`), sculpted delta-swept fuselage, swept-back aerodynamic wings (`ExtrudeGeometry` swept delta profile `span: 8.8`), twin canted V-tail vertical stabilizers, retractable crystal-tinted canopy frame over the tandem cockpit, and **twin glowing neon afterburner exhaust cones** (`afterburnerLeft`, `afterburnerRight` at `[-0.65, 0, -2.6]` and `[+0.65, 0, -2.6]`) with animated pulsing emissive plasma rings (`#00f0ff` / `#ff2a85` / `#ffd966`).
3. **`'origami_glider'` — Origami Dream Glider**:
   - **Geometry**: Giant magical folded paper-airplane cruiser built from crisp creased triangular paper facets (`BufferGeometry` with explicit normal creases for center keel valley fold, inner wing ridges, upturned winglets, and layered tail pleats), glowing gold & lavender starlight rune trim along every paper fold (`THREE.LineSegments` + emissive edge strips), and a floating crystal nose spinner + dorsal tandem saddle seats for `SunnyFox` and `LunaBat`.

#### B.2 Paint Palettes, Propellers, Contrails & Wing Emblems
1. **4 Fuselage & Wing Paint Palettes (`paintPaletteId`)**:
   | Palette ID | Display Name | Primary Fuselage/Wing Hex | Secondary Wing/Strut Hex | Emissive/Trim Hex | Cockpit/Belly Accent Hex |
   |---|---|---|---|---|---|
   | `'sunset_fox_amber'` | **Sunset Fox Amber** | `#e89125` | `#f26d6d` | `#ffd966` | `#faefd4` |
   | `'midnight_bat_indigo'` | **Midnight Bat Indigo** | `#3a2278` | `#9f78d9` | `#ffe57f` | `#c5a3f0` |
   | `'huntrx_golden_neon'` | **HUNTR/X Golden Neon** | `#1a103c` | `#ff2a85` | `#ffd700` | `#00f0ff` |
   | `'mint_cloud'` | **Mint Cloud** | `#56d8c0` | `#fff8eb` | `#ff8da1` | `#7ec8ff` |

2. **3 Propeller / Thruster Styles (`propellerStyleId`)**:
   - `'classic_wood_brass'` (Warm carved mahogany blades + polished brass nose cone)
   - `'starlight_crystal_turbine'` (5-blade glowing cyan/gold translucent crystal fan)
   - `'rainbow_flower_pinwheel'` (6-petal pastel rainbow pinwheel spinner)

3. **4 Sky-Writing Contrail Particle Systems (`contrailStyleId`)**:
   - Instantiated as a live `THREE.Group` / `THREE.Points` / instanced mesh emitter (`contrailSystem`) trailing from the wingtips and tail (`maxParticles: 180`):
     - `'rainbow_ribbon'`: 6-color pastel rainbow ribbon trail (`#ff6b8b`, `#ffa36b`, `#ffd966`, `#6be89b`, `#6bc5ff`, `#b88cff`).
     - `'lantern_fireflies'`: Warm amber & golden glowing lantern firefly orbs (`#ffd966`, `#ff9e2c`) with sinusoidal bobbing.
     - `'starlight_moon_dust'`: Indigo-lavender crescent & 8-point star dust sparkles (`#ffe57f`, `#c5a3f0`, `#8ab4f8`).
     - `'heart_bubbles'`: Iridescent coral-pink & rose floating heart particles (`#ff5c8a`, `#ff9ebb`, `#fff0f5`).

4. **4 Wing Emblems (`wingEmblemId`)**:
   - Rendered via high-DPI `256×256` `HTMLCanvasElement` → `THREE.CanvasTexture` applied to `leftWingEmblemMesh` and `rightWingEmblemMesh`:
     - `'fox_lantern_crest'` (Golden Lantern & Fox Paw Star Crest)
     - `'bat_moonstar_crest'` (Crescent Moon & 8-Point Starburst Wings Crest)
     - `'sf_boston_heart_wings'` (Golden Gate ↔ Zakim Bridge Heart Wings Emblem)
     - `'golden_star_crown'` (Smiling Critters Golden Crown & Rainbow Star Badge)

#### B.3 3D Cockpit & Sky Photo Booth ("Send 3D Flight Postcard to Mom") & `localStorage`
- **Photo Booth Controls**:
  - **Backdrop Selector (`backdropId`)**:
    1. `'sf_golden_gate_sunrise'` ("San Francisco Golden Gate Sunrise")
    2. `'rainbow_cloud_archipelago'` ("Rainbow Cloud Archipelago")
    3. `'boston_zakim_starlight'` ("Boston Zakim Bridge Starlight")
    4. `'sweet_hangar_studio'` ("Starlight Hangar Studio")
  - **Character Duo Pose Selector (`poseId`)**:
    1. `'tandem_wave'` (Pilot steering + Co-Pilot joyful wave)
    2. `'wing_walker_cheer'` (Co-Pilot standing on upper wing cheering + Pilot barrel-roll grin)
    3. `'lantern_and_moonstar_glow'` (Both pendants shining at peak intensity with firefly + stardust burst)
    4. `'happy_bounce_duet'` (Synchronized Happy Bounce Dance beside the aircraft)
  - **Postcard Stickers & Caption (`stickerIds`, `captionText`)**:
    - Default caption: `"Flying from Mom in San Francisco ✈️ to Boston with SunnyFox & LunaBat! 💖"`
    - Selectable stickers: `"🌉 SFO ✈️ BOS 🏙️"`, `"🦊 SunnyFox & LunaBat 🦇"`, `"💖 Love You Mom! 💖"`, `"🌟 Starlight Captain 🌟"`, `"🌈 Cloud Surfer 🌈"`.
- **PNG Postcard Export (`capturePostcard(options)`)**:
  1. Forces an immediate synchronous `renderer.render(scene, activeCamera)` pass on the Three.js WebGL canvas.
  2. Creates an offscreen `1280×720` 2D canvas (`postcardCanvas`), draws the rendered 3D WebGL canvas onto it via `ctx.drawImage(webglCanvas, 0, 0, 1280, 720)`.
  3. Renders a decorative airmail/starlight border, route stamp (`SAN FRANCISCO ✈️ BOSTON`), active aircraft & crew badge (`SunnyFox + LunaBat`), selected stickers, and `captionText`.
  4. Calls `const dataUrl = postcardCanvas.toDataURL('image/png')` (guaranteed valid `data:image/png;base64,...` string with length `> 5000` bytes).
  5. Appends `{ id, createdAt, dataUrl, captionText, backdropId, poseId, stickerIds, aircraftConfig: { ...state.hangar } }` to `state.photoBooth.savedPostcards` and persists to `localStorage.setItem('critters_airplane_3d_postcards_v1', JSON.stringify(savedPostcards))`.
  6. Updates the DOM preview (`#photo-booth-preview-img` `src = dataUrl`) and download link (`#btn-download-postcard` `href = dataUrl`, `download = 'sf-to-boston-3d-postcard.png'`).
  7. Returns `{ id, dataUrl, width: 1280, height: 720, captionText, backdropId }`.

- **`localStorage` Persistence Schema**:
  - **`'critters_airplane_3d_config_v1'`**:
    ```json
    {
      "modelId": "biplane",
      "paintPaletteId": "sunset_fox_amber",
      "propellerStyleId": "classic_wood_brass",
      "contrailStyleId": "rainbow_ribbon",
      "wingEmblemId": "fox_lantern_crest",
      "pilotId": "SunnyFox",
      "coPilotId": "LunaBat",
      "coPilotMode": "rear_cockpit",
      "timeOfDay": "day",
      "characterAccessories": {
        "SunnyFox": { "aviatorGoggles": true, "pilotScarf": true, "captainCap": false },
        "LunaBat": { "aviatorGoggles": true, "pilotScarf": false, "captainCap": true }
      }
    }
    ```
  - **`'critters_airplane_3d_postcards_v1'`**: JSON array of saved postcard objects (`[{ id, createdAt, dataUrl, captionText, backdropId, poseId, aircraftConfig }]`).
  - Automatic boot hydration: On `DOMContentLoaded`, the app reads both `localStorage` keys before the first render frame so that `page.reload()` immediately restores the exact aircraft model (`biplane` / `supersonic_jet` / `origami_glider`), paint palette, propeller style, contrail style, wing emblem, Pilot/Co-Pilot assignment, and saved postcard gallery.

---

### Part C: Complete `window.__APP_STATE__` Verification API Contract

To ensure 100% deterministic inspection and manipulation by `test_writer_e2e` and Gate Auditors in headless Chromium, `window.__APP_STATE__` MUST expose the following state tree and synchronous/promise-returning helper methods at all times once initialized (`window.__APP_STATE__.ready === true`):

```ts
interface AppStateContract {
  // 1. Readiness & Core Engine References
  ready: boolean;                        // true as soon as Three.js scene, characters, airplane & localStorage hydrate
  activeView: 'character_studio' | 'flight_simulator' | 'hangar' | 'photo_booth';
  renderer: THREE.WebGLRenderer;
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  frameCount: number;                    // Increments on every render / stepSimulation frame
  elapsedTime: number;                   // Cumulative simulation time in seconds
  audioMuted: boolean;

  // 2. R1 Character References & State (SunnyFox & LunaBat)
  characters: {
    SunnyFox: {
      id: 'SunnyFox';
      displayName: 'SunnyFox (LanternFox)';
      group: THREE.Group;                // Root 3D group with head, ears, leftEyePatch, zipper, lanternPendant, tail, limbs
      vertexCount: number;               // > 1500 vertices
      meshCount: number;                 // >= 18 distinct child meshes
      currentAnimation: 'idle' | 'joyful_wave' | 'wing_flap_tail_wag' | 'happy_bounce_dance' | 'barrel_roll_cheer' | 'cockpit_pilot_steer';
      animationTime: number;
      pendantLight: THREE.PointLight;    // #ffd966 warm amber lantern PointLight
      pendantEmissiveMesh: THREE.Mesh;
      parts: {
        head: THREE.Group;
        leftEar: THREE.Group;
        rightEar: THREE.Group;
        leftEyePatchRing: THREE.Mesh;    // Signature asymmetric coral-pink eye patch ring (#f26d6d)
        muzzleSmile: THREE.Group;
        chestZipper: THREE.Group;
        lanternPendant: THREE.Group;
        bushyTail: THREE.Group;
        leftArm: THREE.Group;
        rightArm: THREE.Group;
        leftLeg: THREE.Group;
        rightLeg: THREE.Group;
      };
    };
    LunaBat: {
      id: 'LunaBat';
      displayName: 'LunaBat (StarBat)';
      group: THREE.Group;                // Root 3D group with head, ears, quilted bat wings, zipper, moonStarPendant, feet
      vertexCount: number;               // > 1500 vertices
      meshCount: number;                 // >= 18 distinct child meshes
      currentAnimation: 'idle' | 'joyful_wave' | 'wing_flap_tail_wag' | 'happy_bounce_dance' | 'barrel_roll_cheer' | 'cockpit_pilot_steer';
      animationTime: number;
      pendantLight: THREE.PointLight;    // #ffe57f golden crescent moon + starburst PointLight
      pendantEmissiveMesh: THREE.Mesh;
      parts: {
        head: THREE.Group;
        leftEar: THREE.Group;
        rightEar: THREE.Group;
        muzzleSmile: THREE.Group;
        chestZipper: THREE.Group;
        moonStarPendant: THREE.Group;
        leftWingArm: THREE.Group;        // Articulated bat wing with diamond-quilted lavender membrane (#9f78d9)
        rightWingArm: THREE.Group;
        leftFoot: THREE.Group;
        rightFoot: THREE.Group;
      };
    };
  };

  // 3. R2 Flight Simulator State (San Francisco ✈️ Boston)
  flight: {
    active: boolean;
    paused: boolean;
    completed: boolean;                  // true when landed in Boston (progress >= 1.0 or completeFlightToBoston())
    flightState: 'ready_sf' | 'cruising' | 'approaching_boston' | 'landed_boston';
    originCity: 'San Francisco (Golden Gate Bridge)';
    destinationCity: 'Boston (Zakim Bridge & Skyline)';
    pilotId: 'SunnyFox' | 'LunaBat';
    coPilotId: 'LunaBat' | 'SunnyFox';
    coPilotMode: 'rear_cockpit' | 'wing_walker';
    roleSwapCount: number;
    zoneId: 1 | 2 | 3;
    zoneName: 'Golden Gate Sunrise Takeoff' | 'Rainbow Cloud Archipelago & Paper-Airplane Wind Tunnels' | 'Starry Night Aurora Approach into Boston';
    timeOfDay: 'day' | 'sunset' | 'night';
    pendantLightsActive: boolean;        // true in 'night' / Zone 3; illuminates hidden starlight rings
    revealedStarlightRingsCount: number; // Number of Zone 3 hidden rings illuminated by Fox/Bat pendant PointLights
    progress: number;                    // 0.0 (SF) -> 1.0 (Boston)
    distanceMiles: number;               // 0 -> 2700 miles
    speed: number;
    steerX: number;                      // [-1, 1]
    steerY: number;                      // [-1, 1]
    position: { x: number; y: number; z: number };
    rotation: { pitch: number; yaw: number; roll: number };
    boostActive: boolean;
    boostTimer: number;
    boostCount: number;
    barrelRollActive: boolean;
    barrelRollProgress: number;
    barrelRollAngle: number;
    barrelRollCount: number;
    carePackagesDropped: number;
    score: number;
    ringsPassed: number;
    collectedCounts: {
      golden_lantern: number;
      crescent_moon_star: number;
      music_note_booster: number;
      mom_heart_care_package: number;
      sky_ring: number;
      starlight_ring: number;
      paper_airplane_squadron: number;
    };
  };

  // 4. R3 Hangar & Aircraft State
  hangar: {
    modelId: 'biplane' | 'supersonic_jet' | 'origami_glider';
    paintPaletteId: 'sunset_fox_amber' | 'midnight_bat_indigo' | 'huntrx_golden_neon' | 'mint_cloud';
    propellerStyleId: 'classic_wood_brass' | 'starlight_crystal_turbine' | 'rainbow_flower_pinwheel';
    contrailStyleId: 'rainbow_ribbon' | 'lantern_fireflies' | 'starlight_moon_dust' | 'heart_bubbles';
    wingEmblemId: 'fox_lantern_crest' | 'bat_moonstar_crest' | 'sf_boston_heart_wings' | 'golden_star_crown';
    airplaneGroup: THREE.Group;
    pilotSeatAnchor: THREE.Group;
    coPilotSeatAnchor: THREE.Group;
    propellerGroup: THREE.Group;
    contrailSystem: THREE.Object3D;
    vertexCount: number;                 // > 1200 vertices for active aircraft
    primaryColorHex: string;             // Current primary paint material hex (e.g. '#e89125')
    secondaryColorHex: string;
    storageKey: 'critters_airplane_3d_config_v1';
  };

  // 5. R3 Photo Booth State
  photoBooth: {
    backdropId: 'sf_golden_gate_sunrise' | 'rainbow_cloud_archipelago' | 'boston_zakim_starlight' | 'sweet_hangar_studio';
    poseId: 'tandem_wave' | 'wing_walker_cheer' | 'lantern_and_moonstar_glow' | 'happy_bounce_duet';
    captionText: string;
    stickerIds: string[];
    lastCapturedDataUrl: string | null;  // 'data:image/png;base64,...'
    savedPostcards: Array<{
      id: string;
      createdAt: string;
      dataUrl: string;
      captionText: string;
      backdropId: string;
      poseId: string;
      aircraftConfig: Record<string, any>;
    }>;
    storageKey: 'critters_airplane_3d_postcards_v1';
  };

  // 6. Deterministic Programmatic Control Methods (for Playwright E2E Verification)
  setView(view: 'character_studio' | 'flight_simulator' | 'hangar' | 'photo_booth'): void;
  stepSimulation(frames?: number, dt?: number): void; // Advances physics, animations, particles & renders synchronously
  setCharacterAnimation(charId: 'SunnyFox' | 'LunaBat' | 'both', animName: string): void;
  triggerCharacterTapReaction(charId: 'SunnyFox' | 'LunaBat'): void;
  swapRoles(): { pilotId: string; coPilotId: string; roleSwapCount: number };
  setCoPilotMode(mode: 'rear_cockpit' | 'wing_walker'): void;
  startFlight(): void;
  resetFlight(): void;
  setSteering(steerX: number, steerY: number): void;
  triggerBoost(): void;
  triggerBarrelRoll(): void;
  dropHeartPackage(): void;
  collectNearestItem(type?: string): boolean; // Moves nearest uncollected ring/item into collection radius & collects it
  setZone(zoneId: 1 | 2 | 3): void;           // Warps aircraft to start of Zone 1 (z=0), Zone 2 (z=-620), or Zone 3 (z=-1220)
  setTimeOfDay(mode: 'day' | 'sunset' | 'night'): void;
  completeFlightToBoston(): void;             // Advances progress to 1.0, lands on Boston Zakim Runway, sets completed = true
  setPlaneModel(modelId: 'biplane' | 'supersonic_jet' | 'origami_glider'): void;
  setPaintPalette(paletteId: 'sunset_fox_amber' | 'midnight_bat_indigo' | 'huntrx_golden_neon' | 'mint_cloud'): void;
  setPropellerStyle(styleId: 'classic_wood_brass' | 'starlight_crystal_turbine' | 'rainbow_flower_pinwheel'): void;
  setContrailStyle(styleId: 'rainbow_ribbon' | 'lantern_fireflies' | 'starlight_moon_dust' | 'heart_bubbles'): void;
  setWingEmblem(emblemId: 'fox_lantern_crest' | 'bat_moonstar_crest' | 'sf_boston_heart_wings' | 'golden_star_crown'): void;
  setPhotoBackdrop(backdropId: string): void;
  setPhotoPose(poseId: string): void;
  setPhotoCaption(text: string): void;
  capturePostcard(): { id: string; dataUrl: string; width: number; height: number };
  saveConfigToLocalStorage(): void;
  loadConfigFromLocalStorage(): boolean;
}
```

---

## 5. Verification Method

Independent reviewers, test writers, and gate auditors can verify R2, R3, and `window.__APP_STATE__` in headless Playwright Chromium using the following deterministic checks:

1. **Verify Tandem Cockpit & Role Swap (`R2`)**:
   ```js
   const initialPilot = await page.evaluate(() => window.__APP_STATE__.flight.pilotId);
   const swapped = await page.evaluate(() => window.__APP_STATE__.swapRoles());
   expect(swapped.pilotId).not.toBe(initialPilot);
   expect(swapped.roleSwapCount).toBeGreaterThanOrEqual(1);
   ```
2. **Verify Flight Physics, Steering, Boost, Barrel Roll, Collectibles & Zone 3 Pendant Point Lights (`R2`)**:
   ```js
   await page.evaluate(() => {
     const app = window.__APP_STATE__;
     app.setView('flight_simulator');
     app.startFlight();
     app.setSteering(0.6, 0.4);
     app.triggerBoost();
     app.triggerBarrelRoll();
     app.dropHeartPackage();
     app.stepSimulation(30, 1 / 60);
     app.collectNearestItem('golden_lantern');
     app.setZone(3);
     app.setTimeOfDay('night');
     app.stepSimulation(15, 1 / 60);
   });
   const flightSnap = await page.evaluate(() => ({
     pos: window.__APP_STATE__.flight.position,
     rot: window.__APP_STATE__.flight.rotation,
     score: window.__APP_STATE__.flight.score,
     pendantLightsActive: window.__APP_STATE__.flight.pendantLightsActive,
     foxLightIntensity: window.__APP_STATE__.characters.SunnyFox.pendantLight.intensity,
     batLightIntensity: window.__APP_STATE__.characters.LunaBat.pendantLight.intensity,
     revealedRings: window.__APP_STATE__.flight.revealedStarlightRingsCount
   }));
   expect(flightSnap.pos.x).toBeGreaterThan(0);
   expect(flightSnap.pos.y).toBeGreaterThan(12);
   expect(flightSnap.pos.z).toBeLessThan(0);
   expect(flightSnap.score).toBeGreaterThan(0);
   expect(flightSnap.pendantLightsActive).toBe(true);
   expect(flightSnap.foxLightIntensity).toBeGreaterThan(2.5);
   expect(flightSnap.batLightIntensity).toBeGreaterThan(2.5);
   expect(flightSnap.revealedRings).toBeGreaterThan(0);
   ```
3. **Verify Boston Landing Completion (`R2`)**:
   ```js
   const landed = await page.evaluate(() => {
     window.__APP_STATE__.completeFlightToBoston();
     return {
       completed: window.__APP_STATE__.flight.completed,
       flightState: window.__APP_STATE__.flight.flightState,
       progress: window.__APP_STATE__.flight.progress
     };
   });
   expect(landed.completed).toBe(true);
   expect(landed.flightState).toBe('landed_boston');
   expect(landed.progress).toBe(1.0);
   ```
4. **Verify Hangar 3 Aircraft Models, Paint/Contrail Customizer, PNG Postcard Export & `localStorage` Persistence across `page.reload()` (`R3`)**:
   ```js
   for (const modelId of ['biplane', 'supersonic_jet', 'origami_glider']) {
     const vCount = await page.evaluate((m) => {
       window.__APP_STATE__.setPlaneModel(m);
       return window.__APP_STATE__.hangar.vertexCount;
     }, modelId);
     expect(vCount).toBeGreaterThan(1000);
   }
   const postcard = await page.evaluate(() => {
     const app = window.__APP_STATE__;
     app.setPlaneModel('supersonic_jet');
     app.setPaintPalette('midnight_bat_indigo');
     app.setContrailStyle('starlight_moon_dust');
     app.setWingEmblem('bat_moonstar_crest');
     return app.capturePostcard();
   });
   expect(postcard.dataUrl.startsWith('data:image/png;base64,')).toBe(true);
   expect(postcard.dataUrl.length).toBeGreaterThan(5000);

   await page.reload({ waitUntil: 'networkidle' });
   const restored = await page.evaluate(() => ({
     modelId: window.__APP_STATE__.hangar.modelId,
     paintPaletteId: window.__APP_STATE__.hangar.paintPaletteId,
     contrailStyleId: window.__APP_STATE__.hangar.contrailStyleId,
     wingEmblemId: window.__APP_STATE__.hangar.wingEmblemId,
     savedPostcardsCount: window.__APP_STATE__.photoBooth.savedPostcards.length
   }));
   expect(restored.modelId).toBe('supersonic_jet');
   expect(restored.paintPaletteId).toBe('midnight_bat_indigo');
   expect(restored.contrailStyleId).toBe('starlight_moon_dust');
   expect(restored.wingEmblemId).toBe('bat_moonstar_crest');
   expect(restored.savedPostcardsCount).toBeGreaterThanOrEqual(1);
   ```
