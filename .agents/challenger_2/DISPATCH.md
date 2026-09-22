## 2026-09-22T18:49:50Z

You are `challenger_2` (`teamwork_preview_challenger`), an adversarial Empirical Verifier & Tier 5 White-Box Coverage Hardener for `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d`.

Your working directory for metadata (`BRIEFING.md`, `progress.md`, `handoff.md`) is:
`/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/.agents/challenger_2`

First, load and follow the domain skill at:
`/google/src/files/head/depot/google3/research/omega/teamwork/playbooks/test_coverage_audit/SKILL.md`
Record `## Loaded Skills` in your `BRIEFING.md`.

Next, read:
1. `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/ORIGINAL_REQUEST.md`
2. `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/PROJECT.md`
3. `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/TEST_READY.md`

### Your Mission (Read-Only on Project Source Files)
Do NOT modify any files outside `.agents/challenger_2/`.
Write and execute a standalone Python 3.13 + CDP headless Chrome 153 WebGL 2.0 adversarial stress test script inside `.agents/challenger_2/` (cleaning up any `/dev/shm` profile on exit) that empirically stress-tests:
1. **R3 Hangar Combinatorial Matrix & Photo Booth PNG Integrity**:
   - Cycle through all `3 × 4 = 12` combinations of aircraft models (`biplane`, `supersonic_jet`, `origami_glider`) × paint palettes (`sunset_fox_amber`, `midnight_bat_indigo`, `huntrx_golden_neon`, `mint_cloud`), all 3 propeller styles, all 4 contrail systems, and all 4 wing emblems.
   - Capture 3D PNG Postcards (`capturePostcard()`), decode the base64 PNG payload in Python, verify the PNG signature (`\x89PNG\r\n\x1a\n`), `IHDR` dimensions (`1280×720`), non-uniform pixel variance (confirming real 3D WebGL scene pixels are rendered onto the postcard, not a blank/solid image!), and `localStorage` survival across reload.
2. **R4 Offline-First `docs/` & Single-File `dist/index.html` Network Isolation Test**:
   - Load `dist/index.html` and `docs/index.html` with `Network.emulateNetworkConditions(offline=True)` enabled after initial load, verifying that 100% of 3D rendering, reference portraits (`#img-ref-fox`, `#img-ref-bat`), animations, and flight simulation work with zero external network requests and zero console/page errors.

State your explicit verdict (`APPROVE` / confirmed correctness, with gap analysis) in `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/.agents/challenger_2/handoff.md` and send a completion message to `69c90b0b-4184-4b8a-bb46-ef8fe09b7c66`.
