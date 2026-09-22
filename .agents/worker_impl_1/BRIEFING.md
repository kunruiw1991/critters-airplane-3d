# BRIEFING — 2026-09-22T18:46:00Z

## Mission
Implement the complete zero-backend 3D WebGL / Three.js (`r161`) Interactive Web Application & Flight Adventure Game ("Smiling Critters 3D Sky & Airplane Adventure: Bay Area ✈️ Boston") across `index.html`, `manifest.json`, `sw.js`, `src/**`, `scripts/build_dist.py`, `docs/**`, and `dist/index.html`, fulfilling R1–R4 and the unified `window.__APP_STATE__` verification contract.

## 🔒 My Identity
- Archetype: teamwork_preview_worker (`worker_impl_1`)
- Roles: implementer, qa, specialist
- Working directory: `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/.agents/worker_impl_1`
- Original parent: `69c90b0b-4184-4b8a-bb46-ef8fe09b7c66`
- Milestone: M1 — Unified 3D WebGL Application, PWA & Bundles (`R1–R4`)

## 🔒 Key Constraints
- Strictly **Mom in San Francisco / Bay Area ↔ Daughter in Boston** — **ZERO mentions of Grandma** anywhere in code, UI, text, stickers, or audio.
- Exclusive write ownership: `index.html`, `manifest.json`, `sw.js`, `src/**`, `scripts/build_dist.py`, `docs/**`, `dist/index.html`.
- Do NOT overwrite `TEST_INFRA.md`, `TEST_READY.md`, or `tests/` (owned by `test_writer_e2e`).
- Use local offline Three.js `r161` copied from `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/`.
- Single shared `THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true })` across all 4 views.
- Expose full `window.__APP_STATE__` contract with both `characters.SunnyFox`/`characters.sunnyFox` and `characters.LunaBat`/`characters.lunaBat`.

## Current Parent
- Conversation ID: `69c90b0b-4184-4b8a-bb46-ef8fe09b7c66`
- Updated: 2026-09-22T18:46:00Z

## Task Summary
- **What to build**: R1 (Articulated 3D SunnyFox & LunaBat rigs >1500 vertices each, 6 procedural animations, OrbitControls studio, particle bursts, Web Audio synth, reference portrait cards), R2 (SF -> Boston 3-zone 3D flight simulator, tandem cockpit + wing-walker swap, boost/barrel-roll/care-package drop, 6 collectibles, night mode pendant illumination), R3 (3D Hangar with 3 airplanes >1200 vertices each, 4 paint palettes, 3 propellers, 4 contrails, 4 wing emblems, Photo Booth PNG export, localStorage persistence), R4 (PWA manifest & sw.js, `scripts/build_dist.py` building `docs/` + `.nojekyll` and single-file `dist/index.html`).
- **Success criteria**: Zero console/page errors and 100% E2E pass across `index.html`, `docs/index.html`, and `dist/index.html` in headless Chrome 153 with SwiftShader WebGL 2.0.
- **Interface contracts**: `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/PROJECT.md`
- **Code layout**: `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/PROJECT.md § Code Layout`

## Loaded Skills
- **Source**: `/google/src/files/head/depot/google3/research/omega/teamwork/playbooks/greenfield_development/SKILL.md`
- **Local copy**: `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/.agents/worker_impl_1/skill_greenfield_development.md`
- **Core methodology**: Interface-first greenfield engineering, modular architecture, incremental build/test verification, and zero-stub contract compliance.

## Change Tracker
- **Files modified**:
  - `src/vendor/three.min.js` (`659 KB`) & `src/vendor/OrbitControls.js` (`32 KB`): Local offline Three.js `r161` & `OrbitControls`
  - `src/styles/main.css`: Responsive iPad/Desktop stylesheet for all 4 views
  - `src/audio/soundSynth.js`: Web Audio API plush sound & flight synthesizer
  - `src/characters/materials.js`: Procedural plush bump textures, diamond-quilt membrane textures, stitch seams & 3D pilotGear
  - `src/characters/SunnyFox.js`: `SunnyFox` (`21,091` vertices, `75` meshes) with coral left eye patch ring & glowing storm lantern pendant
  - `src/characters/LunaBat.js`: `LunaBat` (`17,724` vertices, `71` meshes) with diamond-quilted bat wings & glowing crescent moon + starburst pendant
  - `src/characters/animations.js`: 6 mathematical procedural animations (`idle`, `wave`, `wingFlapTailWag`, `bounceDance`, `barrelRollCheer`, `cockpitPilotSteer`)
  - `src/characters/particles.js`: Firefly & lavender stardust 3D particle emitters
  - `src/aircraft/aircraftFactory.js`: 3 selectable 3D airplanes (`biplane`, `supersonic_jet`, `origami_glider`, `2,243–2,500` vertices each), 4 paint palettes, 3 propellers, 4 wing emblems
  - `src/aircraft/contrailSystem.js`: 4 sky-writing contrail particle systems
  - `src/flight/skyCourse.js`: 3-Zone San Francisco (Golden Gate Bridge) ✈️ Boston (Zakim Bridge & Skyline) world, 6 collectible classes & Zone 3 hidden starlight rings
  - `src/main.js`: App controller, `localStorage` persistence & `window.__APP_STATE__` verification API
  - `index.html`, `manifest.json`, `sw.js`, `scripts/build_dist.py`, `docs/**`, `dist/index.html`
- **Build status**: PASS (`142/142` E2E tests passed in `tests/run_e2e_suite.py`).
- **Pending issues**: None.

## Quality Status
- **Build/test result**: `142/142 PASSED (0 FAILED)` across Tiers 1–4 (`66/66` Tier 1, `56/56` Tier 2, `14/14` Tier 3, `6/6` Tier 4).
- **Lint status**: Clean.
- **Tests added/modified**: Verified all 142 E2E test cases in `tests/run_e2e_suite.py`.
