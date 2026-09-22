# Technical Analysis — R2 3D Flight Simulator, R3 Hangar & Photo Booth, and `window.__APP_STATE__` Contract

## 1. Narrative & Architectural Alignment
- **Strict Family Focus**: All routes, landmarks, HUD badges, care packages, and photo booth templates strictly celebrate **Mom in San Francisco (Golden Gate Bridge / Bay Area) ↔ Daughter in Boston (Zakim Bridge & Boston Skyline)**. Zero mentions of "Grandma" or "grandmother" appear anywhere in source code, UI strings, assets, or comments.
- **Unified Scene Graph Architecture**: Rather than recreating separate disconnected canvases that waste WebGL contexts on iPad Safari, a single persistent `THREE.WebGLRenderer` (`preserveDrawingBuffer: true`, `antialias: true`) manages a unified 3D scene graph with mode-specific camera rigs (`character_studio`, `hangar`, `flight_simulator`, `photo_booth`) and reusable hierarchical rigs (`SunnyFox`, `LunaBat`, `AirplaneRig`, `WorldCorridor`).

## 2. Tandem Cockpit & Wing-Walking Attachment Design (R1 ↔ R2 ↔ R3 Bridge)
- Both `SunnyFox` and `LunaBat` rigs (from R1) are reparented cleanly into `AirplaneRig`:
  - `AirplaneRig.getObjectByName('pilotSeatAnchor')`: Front cockpit position (`[0, 0.45, 0.85]`), where the active Pilot wears aviator goggles/cap and executes the `pilotSteer` animation synchronized with `steerX` and `steerY`.
  - `AirplaneRig.getObjectByName('coPilotSeatAnchor')`: Rear tandem cockpit / upper-wing mount (`[0, 0.55, -0.65]` or `[1.65, 0.52, -0.10]` in wing-walker mode), where the active Co-Pilot performs `joyfulWave`, `wingFlap`, or `barrelRollCheer` and holds up their glowing pendant (`foxLanternLight` or `batMoonStarLight`).
- Calling `window.__APP_STATE__.swapRoles()` swaps `pilotId` and `coPilotId`, swaps the character `THREE.Group` parent anchors, swaps their animations, increments `roleSwapCount`, and persists the new seating order in `localStorage`.

## 3. Zone 3 Pendant Point-Light Illumination Physics
- In Zone 3 (`"Starry Night Aurora Approach into Boston"`) or whenever `timeOfDay === 'night'`, `foxLanternLight` (`THREE.PointLight`, `#ffd966`, intensity `3.2`, distance `38`) and `batMoonStarLight` (`THREE.PointLight`, `#ffe57f`, intensity `3.0`, distance `38`) are active in world space.
- Each hidden starlight ring in Zone 3 computes its Euclidean distance `d = ring.position.distanceTo(airplaneRig.position)` on every simulation tick:
  - When `pendantLightsActive && d <= 38.0`, `ring.userData.revealedByPendantLight = true`, `ring.material.opacity = 1.0`, and `ring.material.emissiveIntensity = 2.4`.
- This makes the pendant light interaction both visually magical on iPad and 100% deterministically verifiable in headless Playwright tests.
