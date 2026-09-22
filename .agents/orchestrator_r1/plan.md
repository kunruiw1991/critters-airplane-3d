# Execution Plan — Smiling Critters 3D Sky & Airplane Adventure (Bay Area ✈️ Boston)

## 1. Survey & Architecture Specification (Phase 1)
- Dispatch 3 parallel `teamwork_preview_explorer` agents:
  - `explorer_survey_1`: Inspect workspace `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d`, view `assets/custom_critter_fox_lantern.jpg` and `assets/custom_critter_bat_moonstar.jpg`, locate available local `three` (Three.js), `playwright` / Chromium binaries on the machine so the Worker can bundle Three.js locally for 100% offline PWA reliability (`R4`) and run headless Chromium verification.
  - `explorer_survey_2`: Design complete 3D skeletal hierarchy, materials, color hexes, point lights, procedural animations, Web Audio synthesis, and UI reference cards for `SunnyFox / LanternFox` and `LunaBat / StarBat` (`R1`).
  - `explorer_survey_3`: Design complete 3D Flight Simulator (`R2`: tandem pilot/co-pilot cockpit, role swap, 3 SF→Boston sky zones, collectibles, controls), 3D Hangar Customizer & Photo Booth (`R3`: 3 selectable 3D aircraft, paint/contrail/emblem customizer, PNG postcard exporter, `localStorage`), and deterministic `window.__APP_STATE__` verification API.
- Synthesize Explorer findings into `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/PROJECT.md`.

## 2. Implementation & E2E Test Suite Construction (Phase 2)
- Dispatch `teamwork_preview_test_writer` (`test_writer_e2e`) to build `TEST_INFRA.md`, `TEST_READY.md`, and the automated Playwright headless Chromium E2E test suite covering Tiers 1-4 and all acceptance criteria.
- Dispatch `teamwork_preview_worker` (`worker_impl_1`) armed with `greenfield-development` skill to implement `src/`, `docs/` (with `.nojekyll`, `manifest.json`, `sw.js`, `assets/`, local `three.min.js`), and single-file `dist/index.html`, and verify 100% pass against Playwright headless Chromium.

## 3. Gate Verification & Adversarial Hardening (Phase 3)
- Dispatch 2 `teamwork_preview_reviewer` agents (`reviewer_1`, `reviewer_2`) to independently inspect the codebase and run the E2E Playwright test suite.
- Dispatch 2 `teamwork_preview_challenger` agents (`challenger_1`, `challenger_2`) armed with `test-coverage-audit` to empirically stress-test 3D scene graph invariants, animations, flight physics, offline PWA service worker, and edge cases.
- Dispatch 1 `teamwork_preview_auditor` (`auditor_1`) to run full forensic integrity checks (no mocks/placeholders, genuine Three.js 3D geometry & lighting, genuine WebGL canvas rendering, no mention of Grandma).
- Record verdicts in `GATE_STATUS.md` and report back to parent.
