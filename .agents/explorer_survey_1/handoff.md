# Handoff Report — `explorer_survey_1` (Environment, Reference Artwork & R4 PWA/Build Architecture)

**Core Summary**: Verified the workspace and reference artwork (`SunnyFox / LanternFox` and `LunaBat / StarBat`), located local offline Three.js `r161` + `OrbitControls` bundles in `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/`, confirmed headless WebGL 2.0 (`WebGL 2.0 (OpenGL ES 3.0 Chromium)`) execution in `/usr/bin/google-chrome` via Python 3.13 + `websockets` CDP without Node/npm dependencies, and specified the exact R4 `src/`, `docs/`, and `dist/index.html` PWA build layout.

---

## 1. Observation

### 1.1 Workspace & `assets/` Directory Inventory
- **Project Root** (`/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d`):
  - `.agents/` (directory)
  - `BRIEFING.md` (`2,371` bytes)
  - `ORIGINAL_REQUEST.md` (`9,650` bytes)
  - `assets/` (directory)
- **Assets Directory** (`/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/assets`):
  - `assets/custom_critter_fox_lantern.jpg` (`222,438` bytes, 1024×1024 RGB JPEG)
  - `assets/custom_critter_bat_moonstar.jpg` (`273,902` bytes, 1024×1024 RGB JPEG)

---

### 1.2 Exhaustive Visual Specification of Reference Artwork (`view_file` Verified)

#### Character 1: **"SunnyFox / LanternFox"** (`assets/custom_critter_fox_lantern.jpg`)
| Anatomical Region | Visual Details Observed in Reference Artwork | Exact Color Palette (Hex) & 3D Modeling / Rigging Guidance |
|---|---|---|
| **Proportions & Silhouette** | Classic *Smiling Critters* plush proportions (~1:1.2 head-to-body ratio): wide rounded head with fluffy side cheek tufts, pear-shaped plush torso, stubby outward-angled arms, cylindrical legs with chunky 3-toed paws, and an oversized bushy S-curved tail rising behind her left hip to ear level. | Root `THREE.Group('SunnyFox')` with articulated subgroups: `headGroup`, `leftEarGroup`, `rightEarGroup`, `torsoGroup`, `leftArmGroup`, `rightArmGroup`, `leftLegGroup`, `rightLegGroup`, `tailGroup`, `lanternPendantGroup`. |
| **Head, Fur & Plush Seams** | Warm golden-orange short-pile plush fur with soft micro-velour bump texture. Two 3-pointed fluffy cheek tufts flare horizontally from the left and right lower cheeks. **Prominent vertical center stitch seam** (dashed thread stitches) runs down the middle of the forehead from crown to muzzle bridge, plus a short vertical stitch directly below the nose (` philtrum`). Two thick arched dark-brown floating eyebrows above the eyes. | Primary Fur: `#e89125` (warm golden-orange, `roughness: 0.82`, procedural plush normal/bump texture).<br>Stitch Seam & Eyebrows: `#4a2511` / `#5c3116` (`TubeGeometry` or dashed torus/box stitch beads along `x = 0`). |
| **Pointed Fox Ears** | Tall, wide triangular fox ears tilted slightly outward at the top of the head. **Upper ~35% ear tips are coral-pink** (`#f26d6d`) with a softly curved horizontal transition into the golden-orange outer ear base. **Inner ear cavity** is recessed and filled with thick, fluffy cream-ivory fur (`#f8e8c8`) with feathered inner tuft edges. | Outer Ear Base: `#e89125`<br>Coral-Pink Ear Tips: `#f26d6d`<br>Inner Ear Fluffy Fur: `#f8e8c8` |
| **Eyes & Signature Asymmetric Eye Patch** | **Asymmetric Coral-Pink Eye Patch**: Surrounding her **anatomical left eye (viewer's right)** is a distinct rounded oval/teardrop coral-pink patch (`#e86565` / `#f26d6d`) extending from just under the left eyebrow around the outer and lower eyelid onto the upper cheek. Her **anatomical right eye (viewer's left)** has NO patch (surrounded by golden-orange fur).<br>**Eyes**: Large glossy pitch-black spherical eyes (`#0d0d12`) ringed by a thin white scleral border, each containing **2 white catchlights** (1 large upper-left circle + 1 smaller lower-right dot) and **3 curved black upper eyelashes** on the outer corner. | Left Eye Patch (Viewer's Right, `+X` in character space): `#f26d6d`<br>Eyeballs: `#0d0d12` (`roughness: 0.08`, `metalness: 0.1` for glossy wet shine)<br>Catchlights: `#ffffff` (`MeshBasicMaterial`)<br>Eyelashes: `#0a0a0f` (3 curved cylinders/cones per eye) |
| **Cream Muzzle, Nose & Grin** | Wide cream-ivory lower face muzzle (`#f9efd8`) curving upward around the wide grin corners. Centered at the top of the muzzle is a rounded inverted-triangle dark charcoal/black plush nose (`#1c1817`). **Cavernous black Smiling Critters grin** (`#08070a`) spanning ~80% of head width, lined inside with **8 rounded white scalloped upper teeth** and **8 rounded white scalloped lower teeth**, plus a bilobed coral-rose plush tongue (`#c94452`) at the bottom center. | Cream Muzzle & Teeth: `#f9efd8` / `#ffffff`<br>Nose: `#1c1817`<br>Mouth Cavity: `#08070a`<br>Tongue: `#c94452` |
| **Torso, Belly, Paws & Bushy Tail** | Pear-shaped golden-orange torso (`#e89125`) with a large oval cream belly patch (`#faefd4`). Visible dashed plush stitch seams run along the front center of both arms and down the front center of both legs. **Hands**: Mitten-style coral-pink hands (`#e36562`) with **cream paw pads on the palms** (1 central oval pad + 3 small toe-bean pads `#f8e4bc`). **Feet**: Chunky 3-toed coral-pink feet (`#e36562`) with stitched toe dividers and ankle seam cuffs. **Tail**: Massive sweeping bushy tail on her left/rear side — lower 60% golden-orange (`#e89125`) transitioning with jagged fur tufts into a **snow-white upper 40% pointed tip** (`#faf5ea`). | Belly Patch: `#faefd4`<br>Hands & 3-Toed Feet: `#e36562`<br>Palm Paw Pads: `#f8e4bc`<br>Tail Base (60%): `#e89125`<br>Tail Tip (40%): `#faf5ea` |
| **Chest Zipper & Glowing Storm Lantern Pendant** | Heavy vertical antique-brass/gold metal zipper (`#d4942a`) running down the center of the cream belly patch from collar to lower belly, with interlocking metal teeth and a large brass zipper pull ring at the neck. Hanging from the pull ring is a **3D vintage bronze/gold camping storm lantern pendant**: tiered metal cap, circular wire bail handle, side guard struts, round pedestal base (`#8c5818` / `#c88a28`), and a glass globe housing a **brightly glowing warm amber-gold X-filament/flame core** (`#ffd966` / `#fff4b8`) that casts warm golden light onto her chest fur. | Zipper Track & Slider: `#d4942a` (`metalness: 0.75`, `roughness: 0.3`)<br>Lantern Cage: `#9c641c`<br>Emissive Lantern Core: `#ffd966` (`emissive: 0xffb732`, `emissiveIntensity: 2.2`) + attached `THREE.PointLight(0xffcf56, 1.8, 6.0)` |

---

#### Character 2: **"LunaBat / StarBat"** (`assets/custom_critter_bat_moonstar.jpg`)
| Anatomical Region | Visual Details Observed in Reference Artwork | Exact Color Palette (Hex) & 3D Modeling / Rigging Guidance |
|---|---|---|
| **Proportions & Silhouette** | Matched *Smiling Critters* sibling proportions with SunnyFox (~1:1.2 head-to-body ratio), distinguished by towering fluffy bat ears and wide spread diamond-quilted bat wings extending laterally from both arms. | Root `THREE.Group('LunaBat')` with articulated subgroups: `headGroup`, `leftEarGroup`, `rightEarGroup`, `torsoGroup`, `leftWingArmGroup`, `rightWingArmGroup`, `leftLegGroup`, `rightLegGroup`, `moonStarPendantGroup`. |
| **Head, Fur & Forehead Stitch** | Deep royal indigo-violet plush head (`#3a2278`) with a prominent **vertical center forehead stitch seam** running from the top crown down between the eyes to the nose bridge. Two arched dark indigo-black eyebrows (`#160b36`) float above the eyes. | Primary Fur: `#3a2278` / `#351e70` (`roughness: 0.82`)<br>Forehead Seam & Eyebrows: `#160b36` / `#5a3ca8` |
| **Oversized Fluffy Bat Ears** | Very tall, wide-cupped pointed bat ears (~45% of head height) set upright on the crown. Outer shell and inner base are deep indigo (`#3a2278`), while the **entire wide inner ear cup and outer rim are filled with long, ultra-fluffy pastel lilac-lavender fur** (`#c5a3f0` / `#d6bcf8`). | Outer Ear Shell: `#3a2278`<br>Fluffy Inner Ear Fur: `#c5a3f0` / `#d6bcf8` |
| **Eyes** | Large glossy pitch-black spherical eyes (`#0a0910`) set inside subtle lavender eye-socket rims, each featuring a large upper-left white catchlight circle and a smaller lower-right white catchlight dot. | Eyeballs: `#0a0910` (`roughness: 0.08`)<br>Catchlights: `#ffffff` |
| **Upturned Bat Nose, Lavender Lip Rim & Grin** | Instead of a separate black nose button, a **thick continuous pastel lilac-lavender plush lip/muzzle border** (`#b898e8`) frames the entire wide grin and swells upward in the center into a **rounded bat nose bridge with two dark purple-black teardrop nostrils** (`#23114d`). Inside the cavernous black mouth (`#07060c`) are **6 rounded white upper teeth** and **6 rounded white lower teeth** (`#f4f2fa`) with subtle stitched gum outlines. | Lavender Muzzle/Lip Rim & Nose: `#b898e8`<br>Nostrils: `#23114d`<br>Mouth Cavity: `#07060c`<br>Teeth (6 upper, 6 lower): `#f4f2fa` |
| **Torso, Belly, Legs & 3-Toed Feet** | Deep indigo-purple pear-shaped torso (`#351e70`) with a large oval pastel lavender plush belly patch (`#b592e6`). Cylindrical deep-indigo legs with ankle stitch cuffs and **chunky 3-toed pastel lavender plush feet** (`#ba96ea`) with vertical toe seams. | Torso & Legs: `#351e70`<br>Belly Patch: `#b592e6`<br>3-Toed Feet: `#ba96ea` |
| **Articulated Quilted Bat Wings** | Attached along the arms: the **upper leading edge of each wing** is a thick deep-indigo arm tube (`#351e70`) topped with an **upturned rounded thumb-hook digit** at the mid-wing wrist joint, curving down to the wingtip. Spanning below the arm to the side of the torso is a **pastel violet-lavender wing membrane** (`#9f78d9` / `#b28ce8`) divided by **3 dark-stitched radial wing ribs** into **3 scalloped lower bat-wing arches**, embossed across the entire surface with a **diagonal diamond-quilted stitch grid**. | Wing Leading Arm & Thumb Hook: `#351e70`<br>Quilted Wing Membrane: `#9f78d9` / `#b28ce8`<br>Wing Ribs & Diamond Quilting Seams: `#563694` |
| **Silver Chest Zipper & Glowing Crescent Moon + 8-Pointed Starburst Pendant** | Vertical metallic silver/chrome zipper (`#c4ccd9`) running down the center of the lavender belly patch from collar to lower abdomen with a silver slider at the throat. Hanging from the zipper ring is a **3D glowing golden Crescent Moon + 8-Pointed Starburst pendant** (`#ffe57f` / `#ffd54f`): a **left-curving C-shaped golden Crescent Moon** cradling an **8-pointed golden Starburst** (4 long cardinal points + 4 shorter diagonal points) inside its inner curve, emitting a warm golden-champagne glow onto the lavender chest. | Silver Zipper Track & Pull: `#c4ccd9` (`metalness: 0.8`, `roughness: 0.25`)<br>Crescent Moon + 8-Pointed Starburst Pendant: `#ffe57f` (`emissive: 0xffd54f`, `emissiveIntensity: 2.2`) + attached `THREE.PointLight(0xffe57f, 1.8, 6.0)` |

---

### 1.3 Local System Environment & Verified Tooling Paths

1. **Node / NPM Status**:
   - `node`, `npm`, and `npx` are **NOT installed** on this host, and root disk `/` has a strict space safety budget (`PROJECT.md` / `TEST_INFRA.md` in sibling project `/usr/local/google/home/kunruiwang/teamwork_projects/cheer_up_studio`). **Workers must NOT run `npm install`.**
2. **Local Offline Three.js (`r161`) Library Paths (Ready to Copy/Vendor)**:
   - Located in the active CitC workspace at `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/`:
     - **Core Engine (Minified UMD/Global `window.THREE`, includes `THREE.CapsuleGeometry` and zero deprecation warnings)**:
       `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/build/three.min.js` (`659 KB`)
     - **OrbitControls (IIFE attaching `THREE.OrbitControls` directly onto `window.THREE`)**:
       `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/examples/js/controls/OrbitControls.js` (`32 KB`)
     - *(Alternative ES Module versions if needed)*:
       - `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/build/three.module.js` (`1.3 MB`)
       - `/google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/examples/jsm/controls/OrbitControls.js` (`31 KB`)
3. **Headless Browser & WebGL 2.0 Automation Stack (Zero-Network Verified)**:
   - **Python Driver Runtime**: `/usr/bin/python3` (`Python 3.13.15`) with `websockets`, `asyncio`, `http.server`, and `urllib.request` pre-installed.
   - **Browser Binary**: `/usr/bin/google-chrome` (`Google Chrome 153.0.8010.52`).
   - **Verified Headless WebGL 2.0 Launch Flags**:
     We executed a live verification against `/usr/bin/google-chrome` and confirmed that launching Chrome with ANGLE + SwiftShader flags initializes a full hardware-independent **WebGL 2.0 (`WebGL 2.0 (OpenGL ES 3.0 Chromium)`)** context for Three.js:
     ```bash
     /usr/bin/google-chrome \
       --headless=new \
       --no-sandbox \
       --use-gl=angle \
       --use-angle=swiftshader \
       --enable-webgl \
       --ignore-gpu-blocklist \
       --enable-unsafe-swiftshader \
       --autoplay-policy=no-user-gesture-required \
       --user-data-dir=/dev/shm/e2e_chrome_<pid> \
       --remote-debugging-port=<free_port> \
       --window-size=1440,900
     ```
   - **Reusable CDP Test Harness Reference**:
     `/usr/local/google/home/kunruiwang/teamwork_projects/cheer_up_studio/tests/cdp_driver.py` (`27,881` bytes) provides a ready-to-adapt Python async CDP WebSocket client and local HTTP server manager that stores all browser profiles in `/dev/shm` and cleans them up on exit.

---

## 2. Logic Chain

1. **Why vendor `threejs/r161/build/three.min.js` + `r161/examples/js/controls/OrbitControls.js`?**
   - From Observation 1.3, `r161/build/three.min.js` (`659 KB`) defines `window.THREE` globally, includes modern primitives like `THREE.CapsuleGeometry` (which `r134` lacks), and has Google3's patch removing the `r150+` console deprecation warning (`deprecated warn: False`).
   - Pairing it with `r161/examples/js/controls/OrbitControls.js` (`32 KB`) attaches `THREE.OrbitControls` directly onto `window.THREE`. This allows all application ES modules under `src/` to access `window.THREE` and `window.THREE.OrbitControls` seamlessly both when served as modular ES scripts (`index.html` / `docs/index.html`) AND when bundled into the single-file `dist/index.html` via Python (`scripts/build_dist.py`) without any import-map or bare-specifier resolution failures on `file://` or GitHub Pages.
2. **Why use Python 3.13 + `websockets` CDP with SwiftShader flags instead of Playwright/Node?**
   - From Observation 1.3, Node/npm/Playwright are absent on the machine and root `/` disk space must be preserved. Using `/usr/bin/python3` + `websockets` + `/usr/bin/google-chrome` with `--use-gl=angle --use-angle=swiftshader --enable-webgl --ignore-gpu-blocklist --enable-unsafe-swiftshader` and `--user-data-dir=/dev/shm/...` gives 100% real Chromium WebGL 2.0 rendering (`ctx.getParameter(gl.VERSION) === 'WebGL 2.0 (OpenGL ES 3.0 Chromium)'`), `canvas.toDataURL('image/png')` export verification, `window.__APP_STATE__` scene graph inspection, and zero disk footprint.

---

## 3. Caveats

- **Important WebGL Flag Caveat for Headless Chrome 153**: In `cheer_up_studio/tests/cdp_driver.py` (which was a 2D Canvas app), Chrome was launched with `--disable-gpu`. For `critters_airplane_3d` (a 3D WebGL / Three.js app), **do NOT pass `--disable-gpu` alone**; instead pass `--use-gl=angle --use-angle=swiftshader --enable-webgl --ignore-gpu-blocklist --enable-unsafe-swiftshader` (and preserve `preserveDrawingBuffer: true` on `THREE.WebGLRenderer` so `canvas.toDataURL('image/png')` in the Photo Booth exports non-blank 3D frames).
- **Bundle Size Ceiling**: Because `three.min.js` (`659 KB`) + `OrbitControls.js` (`32 KB`) + base64-encoded reference images (`222 KB` + `274 KB` raw, ~`660 KB` base64) total ~`1.45 MB`, `scripts/build_dist.py` should set `MAX_BUNDLE_BYTES = 3 * 1024 * 1024` (`3.0 MB`) rather than `cheer_up_studio`'s 350 KB ceiling.

---

## 4. Conclusion & R4 Directory / Build Architecture Design

### 4.1 Complete R4 Project Directory Layout
```text
/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/
├── index.html                        # Root modular entry point (loads src/vendor/three.min.js, OrbitControls.js, src/main.js)
├── manifest.json                     # Root iPad PWA Web App Manifest (relative paths "./")
├── sw.js                             # Root Offline-First Service Worker (caches engine, modules & assets)
├── assets/
│   ├── custom_critter_fox_lantern.jpg   # Original reference portrait 1 (SunnyFox / LanternFox)
│   └── custom_critter_bat_moonstar.jpg  # Original reference portrait 2 (LunaBat / StarBat)
├── src/
│   ├── vendor/
│   │   ├── three.min.js              # Copied from google3/third_party/javascript/threejs/r161/build/three.min.js
│   │   └── OrbitControls.js          # Copied from google3/third_party/javascript/threejs/r161/examples/js/controls/OrbitControls.js
│   ├── styles/
│   │   └── main.css                  # Responsive iPad landscape/portrait UI, HUD, Hangar & Studio styles
│   ├── core/
│   │   ├── state-store.js            # Versioned localStorage persistence (custom planes, postcards, pilot roles)
│   │   ├── sound-engine.js           # Synthesized Web Audio API plush squeaks, engine hum, chimes & music boosters
│   │   └── reference-assets.js       # Resolves ./assets/*.jpg in modular mode & embedded data:image/jpeg URI in dist
│   ├── characters/
│   │   ├── sunny-fox-rig.js          # 3D SunnyFox (LanternFox) hierarchical rig, textures & glowing storm lantern
│   │   ├── luna-bat-rig.js           # 3D LunaBat (StarBat) hierarchical rig, diamond-quilted wings & moon-star pendant
│   │   └── character-animator.js     # Procedural 6-clip animation mixer (Idle, Wave, WingFlap/TailWag, Bounce, BarrelRoll, PilotSteer)
│   ├── aircraft/
│   │   ├── aircraft-factory.js       # 3D Biplane, Starlight Supersonic Jet & Origami Dream Glider builders + paint/emblems
│   │   └── contrail-system.js        # 3D particle contrails (Rainbow Ribbon, Lantern Fireflies, Starlight Moon Dust, Heart Bubbles)
│   ├── views/
│   │   ├── studio-view.js            # R1: 360° 3D Character Studio + side-by-side reference artwork cards + accessories
│   │   ├── flight-sim-view.js        # R2: SF (Golden Gate) ✈️ Boston (Zakim Bridge) 3-Zone 3D Sky Flight Simulator
│   │   ├── hangar-view.js            # R3: 3D Airplane Hangar Customizer & Wing Decal Studio
│   │   └── photobooth-view.js        # R3: 3D Cockpit & Sky Photo Booth ("Send 3D Flight Postcard to Mom") + Gallery
│   └── main.js                       # Application bootstrapper & window.__APP_STATE__ deterministic test API
├── docs/                             # GitHub Pages Ready Deployment Directory (exact mirror served at https://<user>.github.io/<repo>/)
│   ├── .nojekyll                     # Prevents Jekyll from ignoring files or altering paths on GitHub Pages
│   ├── index.html                    # Production entry HTML with Apple iPad PWA meta tags & relative paths
│   ├── manifest.json                 # iPad PWA manifest ("display": "standalone", "start_url": "./", "scope": "./")
│   ├── sw.js                         # Offline-first Service Worker pre-caching ./index.html, ./vendor/*, ./src/*, ./assets/*
│   ├── assets/
│   │   ├── custom_critter_fox_lantern.jpg
│   │   └── custom_critter_bat_moonstar.jpg
│   ├── vendor/
│   │   ├── three.min.js
│   │   └── OrbitControls.js
│   └── src/                          # Complete modular ES source tree copied by scripts/build_dist.py
├── dist/
│   └── index.html                    # Self-contained single-file bundle (inlines CSS, Three.js, OrbitControls, base64 assets & all modules)
├── scripts/
│   └── build_dist.py                 # Zero-dependency Python 3 builder that populates both docs/ and single-file dist/index.html
└── tests/
    ├── cdp_driver.py                 # Async CDP WebSocket driver launching headless Chrome 153 with SwiftShader WebGL 2.0
    └── run_e2e_suite.py              # Automated E2E verification suite checking AC-1..AC-4 & window.__APP_STATE__
```

### 4.2 Exact Copy Commands for the Worker to Vendor Three.js `r161`
```bash
mkdir -p /usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/src/vendor
cp /google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/build/three.min.js \
   /usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/src/vendor/three.min.js
cp /google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/examples/js/controls/OrbitControls.js \
   /usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/src/vendor/OrbitControls.js
```

### 4.3 Required iPad PWA Headers (`index.html` & `docs/index.html`)
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="Critters 3D Sky" />
<link rel="manifest" href="./manifest.json" />
```

---

## 5. Verification Method

To independently verify all findings in this report:
1. **Verify Three.js `r161` & `OrbitControls.js` presence**:
   ```bash
   ls -lh /google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/build/three.min.js \
          /google/src/cloud/kunruiwang/cheer_up_gift_ideas/google3/third_party/javascript/threejs/r161/examples/js/controls/OrbitControls.js
   ```
2. **Verify Reference Images**:
   ```bash
   ls -lh /usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/assets/
   ```
3. **Verify Headless Chrome 153 WebGL 2.0 Execution**:
   Run `/usr/bin/google-chrome --headless=new --no-sandbox --use-gl=angle --use-angle=swiftshader --enable-webgl --ignore-gpu-blocklist --enable-unsafe-swiftshader` via `/usr/bin/python3` + `websockets` and assert `gl.getParameter(gl.VERSION)` returns `"WebGL 2.0 (OpenGL ES 3.0 Chromium)"`.
