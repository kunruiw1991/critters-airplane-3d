## 2026-09-22T17:32:23Z

You are `explorer_survey_3`, a read-only Explorer designing the R2 3D Flight Simulator (SF ✈️ Boston), R3 3D Hangar Customizer & Photo Booth, and the `window.__APP_STATE__` verification contract for `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d`.

Your working directory for metadata (`BRIEFING.md`, `progress.md`, `analysis.md`, `handoff.md`) is:
`/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/.agents/explorer_survey_3`

First, read `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/ORIGINAL_REQUEST.md`.
Design a comprehensive technical specification covering:
1. **R2. 3D "Airplane" Sky Adventure & Co-Pilot Flight Simulator (San Francisco ✈️ Boston)**:
   - Strictly Mom in San Francisco (Golden Gate Bridge) ↔ Daughter in Boston (Zakim Bridge & Boston Skyline) — ZERO mentions of Grandma anywhere.
   - Tandem cockpit seating both 3D characters (`SunnyFox` and `LunaBat`) with 1-tap Pilot ↔ Co-Pilot swap (`swapRoles()`).
   - 3D Flight physics & controls: virtual thumbstick / touch-drag + `WASD`/Arrows steering, Turbo Starlight Boost, 360° Barrel Roll / Loop-de-Loop Stunt, and Heart Parachute Care-Package Drop.
   - 3 Sky Zones (Zone 1: Golden Gate Sunrise Takeoff, Zone 2: Rainbow Cloud Archipelago & Paper-Airplane Wind Tunnels, Zone 3: Starry Night Aurora Approach into Boston where Fox's lantern & Bat's moon-star point lights illuminate hidden starlight rings) + Day/Sunset/Night mode switching and landing completion sequence in Boston.
   - Collectibles: Golden Lanterns, Crescent Moon Stars, Music Note Boosters, Mom's Heart Care Packages, glowing 3D rings, paper-airplane squadrons.
2. **R3. 3D Airplane Hangar Builder, Wing Decal Studio & Cockpit Photo Booth**:
   - 3 Selectable 3D Airplanes (`biplane`: Critter Cloud Biplane, `supersonic_jet`: Starlight Supersonic Jet, `origami_glider`: Origami Dream Glider).
   - 4 Paint Palettes (`sunset_fox_amber`, `midnight_bat_indigo`, `huntrx_golden_neon`, `mint_cloud`), Propeller styles, 4 Contrail particle systems (`rainbow_ribbon`, `lantern_fireflies`, `starlight_moon_dust`, `heart_bubbles`), and Wing Emblems.
   - 3D Cockpit & Sky Photo Booth ("Send 3D Flight Postcard to Mom") exporting real WebGL + overlay PNG (`data:image/png;base64,...`) and persisting aircraft configs & saved postcards in `localStorage`.
3. **Deterministic Verification API (`window.__APP_STATE__`)**:
   - Define every property and programmatic helper method on `window.__APP_STATE__` so headless Playwright tests can deterministically inspect the live Three.js scene graph, trigger animations, swap roles, step flight simulation frames, test steering/boost/barrel-roll/collectibles/zone-switches, customize planes, capture PNG postcards, and verify `localStorage` persistence.

Write your complete specification to `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/.agents/explorer_survey_3/handoff.md` and notify parent (`69c90b0b-4184-4b8a-bb46-ef8fe09b7c66`).
