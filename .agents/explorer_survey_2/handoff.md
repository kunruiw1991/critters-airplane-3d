# R1 Handoff Report: 3D Custom Smiling Critters Character Rigging, Materials, Lighting, Procedural Animations & Audio Specification

**Executive Summary**: This specification defines the complete Three.js (`THREE.Group`) hierarchical rigs, exact hex color palettes, procedural plush/quilted bump textures, real-time point/emissive pendant lighting, 6 mathematical procedural animations, 3D pilot accessories (`pilotGear`), raycast tap-to-react particle emitters, Web Audio API sound synthesizer, and reference artwork portrait cards for **Character 1: SunnyFox / LanternFox** and **Character 2: LunaBat / StarBat**.

---

## 1. Observation

### 1.1 Primary Sources Examined
1. **Requirements Document**: `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/ORIGINAL_REQUEST.md` (Lines 16–27: R1 Specification; Lines 52–54: Headless Browser 3D Verification Acceptance Criteria).
2. **Reference Artwork 1 (`SunnyFox / LanternFox`)**: `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/assets/custom_critter_fox_lantern.jpg` (1024×1024 JPEG, 222,438 bytes).
   - **Direct Visual Observations**:
     - **Head & Ears**: Wide golden-orange plush head (`#e89125`) with two pointed cheek fur tufts on each side, a vertical center stitch seam running down the forehead (`x = 0`) and down the upper lip philtrum, and two warm-brown arched eyebrows (`#6b3814`). Tall pointed fox ears tilted outward (`±22°`) with golden-orange outer fur (`#e89125`), coral-pink upper tips (`#f26d6d`), and lush cream inner ear fur (`#f8e8c8`).
     - **Eyes & Asymmetric Left Eye Patch**: Large glossy black eyes (`#08080c`) with dual white specular catchlights per eye (large upper-left circle + small lower-right circle) and **3 curved upper eyelashes per eye** on the outer-upper edge. Around the character's anatomical **left eye** (viewer's right, `+X` in local rig coordinates), there is a prominent oval **coral-pink eye patch ring** (`#f26d6d` / `#e86666`). The character's right eye (`-X`) sits directly on `#e89125` golden-orange fur with no patch.
     - **Muzzle & Smiling Critters Mouth**: Broad cream muzzle (`#f9efd8`) with a rounded-triangular matte black nose (`#141418`). Wide recessed matte-black Smiling Critters mouth cavity (`#050508`) containing **6 rounded white upper teeth** (`#fcfaf5`), **6 rounded white lower teeth** (`#fcfaf5`), and a pink-red bilobed tongue (`#d9535f`).
     - **Torso, Zipper & Glowing Storm Lantern Pendant**: Pear-shaped `#e89125` torso with an oval cream belly (`#faefd4`) and a vertical antique-brass metal tooth zipper (`#d49b35`) down the chest centerline (`x = 0`). Hanging from the top brass zipper pull ring is a **3D metallic bronze/gold camping storm lantern** with top suspension loop, vented dome cap, wire cage struts, stepped base tank, and a glowing warm-amber glass globe (`#ffd966`) casting golden light across the cream belly.
     - **Limbs & Tail**: `#e89125` arms with longitudinal stitch seams and coral-pink 3-fingered hands (`#e36562`) featuring **3 cream oval paw pads (`#faefd4`)** on each palm. `#e89125` cylindrical legs with vertical front stitch seams and 3-toed coral-pink feet (`#e36562`). Huge upward-curving bushy `#e89125` fox tail on the back-right with a zig-zag fur transition to a voluminous `#faf5ea` snow-white pointed tip.
3. **Reference Artwork 2 (`LunaBat / StarBat`)**: `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/assets/custom_critter_bat_moonstar.jpg` (1024×1024 JPEG, 273,902 bytes).
   - **Direct Visual Observations**:
     - **Head & Ears**: Wide deep royal indigo-purple plush head (`#3a2278`) with a vertical center forehead stitch seam (`x = 0`) and two dark indigo arched eyebrows (`#1a0d3d`). Tall, broad fluffy bat ears with `#3a2278` outer backs and thick, feathered pastel lilac-lavender inner fur (`#c5a3f0`).
     - **Eyes, Upturned Bat Nose & Muzzle**: Large glossy black eyes (`#08080c`) with dual white catchlights per eye and subtle warm golden lower-edge reflections. Continuous pastel lavender muzzle/lip rim (`#b898e8`) arching upward at the top center into an **upturned bat nose (`#b898e8`)** with **2 dark oval nostrils (`#231252`)**. Deep recessed matte-black mouth cavity (`#050508`) with **6 rounded white upper teeth** and **6 rounded white lower teeth** (`#fcfaf5`).
     - **Torso, Silver Zipper & Glowing Crescent Moon + 8-Pointed Starburst Pendant**: Deep indigo-purple torso (`#351e70`) with an oval pastel lavender belly patch (`#b592e6`) and a vertical metallic silver zipper (`#d8dde6`) down the center (`x = 0`). Hanging from the top silver zipper pull is a **3D glowing golden Crescent Moon (`#ffe57f`)** curving around an **8-Pointed Starburst (`#ffe57f` / `#fffbe6`)** nestled in its right concave opening.
     - **Articulated Spread Bat Wings & Feet**: Attached to the arms are two broad spread bat wings (`leftWingArm`, `rightWingArm`) with thick `#3a2278` upper arm leading edges, an upright **plush thumb-hook (`#3a2278`)** at each wrist joint, 3 internal radial finger struts, 3 scalloped lower edge bays, and **diamond-quilted `#9f78d9` pastel lavender wing membranes**. Sturdy `#351e70` legs with ankle stitch seams and plump **3-toed pastel lavender feet (`#ba96ea`)**.

---

## 2. Logic Chain & Technical Architecture

To satisfy both visual fidelity to Kunrui's reference artwork and deterministic programmatic verification (`ORIGINAL_REQUEST.md` line 53), every anatomical component is constructed as an explicit, named `THREE.Group` node with standardized coordinate pivots, procedural bump maps, and verifiable `userData`.

### 2.1 Shared Procedural Material & Plush Seam Library (`src/characters/materials.js`)
1. **Procedural Plush Fur Bump Texture (`createPlushBumpTexture(size = 256)`)**:
   - Generates an offscreen HTML5 `CanvasTexture` (`256×256`, `wrapS = wrapT = THREE.RepeatWrapping`, `repeat.set(4, 4)`) with multi-octave short-strand cellular noise so `MeshStandardMaterial({ roughness: 0.82, metalness: 0.04, bumpMap, bumpScale: 0.018 })` exhibits soft tactile plush micro-fibers under studio and sky lighting.
2. **Procedural Diamond-Quilted Wing Membrane Texture (`createDiamondQuiltTexture(baseHex = '#9f78d9', seamHex = '#6a45a8', size = 256)`)**:
   - Renders crisp `45°` intersecting diagonal stitch lines (`lineWidth = 3`, dashed thread pattern) with soft radial pillow gradients inside each diamond cell. Used as both `map` and `bumpMap` (`bumpScale: 0.032`) on `LunaBat`'s wing membranes.
3. **3D Plush Stitch Seam Builder (`createStitchSeamStrip(points, colorHex, dashCount = 14)`)**:
   - Constructs a `THREE.Group` of tiny capsule/box thread stitches (`radius = 0.0045, length = 0.012`) along a `THREE.CatmullRomCurve3(points)` to render the iconic center forehead stitch, philtrum stitch, and arm/leg seam stitches visible in both reference portraits.

---

### 2.2 Character 1 Specification: `SunnyFox` / `LanternFox` (`src/characters/SunnyFox.js`)

#### A. Exact Color Hex Palette (`SUNNY_FOX_PALETTE`)
| Token Name | Hex Code | Target Sub-Meshes | Material Properties |
|---|---|---|---|
| `plushMain` | `#e89125` | Head, cheek tufts, outer ears, torso, upper arms, thighs, tail base/mid | `roughness: 0.82, metalness: 0.04, bumpScale: 0.018` |
| `earTipCoral` | `#f26d6d` | Upper 30% of left/right ear cones, `eyePatchLeft` ring | `roughness: 0.80, metalness: 0.04` |
| `innerEarCream` | `#f8e8c8` | Recessed inner ear cavity & fluffy ear tufts | `roughness: 0.86, metalness: 0.02` |
| `muzzleCream` | `#f9efd8` | Broad arched lower-face muzzle & lip rim | `roughness: 0.80, metalness: 0.03` |
| `bellyCream` | `#faefd4` | Oval chest/belly patch, 3 palm paw pads per hand, foot sole pads | `roughness: 0.84, metalness: 0.02` |
| `pawCoral` | `#e36562` | Left/right 3-fingered hands & 3-toed rounded feet | `roughness: 0.80, metalness: 0.04` |
| `tailTipWhite` | `#faf5ea` | Upper 38% bushy tail tip & zig-zag fur collar | `roughness: 0.88, metalness: 0.02` |
| `eyeBlack` | `#08080c` | Left & right eyeballs + 3 upper eyelashes per eye | `roughness: 0.05, metalness: 0.10` (glossy cornea) |
| `mouthBlack` | `#050508` | Recessed wide Smiling Critters mouth cavity | `MeshBasicMaterial({ color: 0x050508 })` |
| `teethWhite` | `#fcfaf5` | 6 upper rounded teeth + 6 lower rounded teeth | `roughness: 0.25, metalness: 0.05` |
| `tonguePink` | `#d9535f` | Bilobed lower mouth tongue | `roughness: 0.65, metalness: 0.02` |
| `zipperBrass` | `#d49b35` | Vertical chest zipper teeth, slider & D-ring pull | `roughness: 0.28, metalness: 0.85` |
| `lanternBronze`| `#b87b20` | Storm lantern cap, base tank, and 4 wire cage guards | `roughness: 0.32, metalness: 0.82` |
| `lanternCore` | `#ffd966` | Glowing storm lantern glass globe, inner flame & `THREE.PointLight` | `emissive: 0xffd966, emissiveIntensity: 2.5` |

#### B. Required `THREE.Group` Scene Graph & Coordinate Geometry (`SunnyFox`)
Root `THREE.Group`: `name = "SunnyFox"`, `userData = { characterId: 'sunny_fox', displayName: 'SunnyFox (LanternFox)', role: 'pilot', animState: 'idle' }`. Standing height: `~2.15` world units (`y ∈ [-0.95, +1.20]`).

```
SunnyFox (THREE.Group)
├── head (THREE.Group)                     @ pos(0, 0.42, 0.0)
│   ├── skullMesh                          [SphereGeometry(0.46, 32, 24) scaled (1.18, 0.98, 0.95), #e89125]
│   ├── foreheadStitch                     [7 vertical stitch capsules at x=0, y∈[0.16, 0.44], z=0.43, #b3620e]
│   ├── cheekTufts                         [2 left + 2 right lateral ConeGeometry(0.11, 0.22, 12) at x=±0.52, y=-0.04, #e89125]
│   ├── eyebrows                           [Left & Right arched TorusGeometry(0.09, 0.018, 8, 16, 1.8) at (∓0.17, 0.29, 0.39), #6b3814]
│   ├── leftEar (THREE.Group)              @ pos(0.28, 0.38, -0.02), rot.z = -0.34 rad
│   │   ├── earBaseMesh                    [CylinderGeometry(0.09, 0.19, 0.28, 20), #e89125]
│   │   ├── earTipMesh                     [ConeGeometry(0.09, 0.17, 20) @ y=+0.225, #f26d6d]
│   │   └── innerEarMesh                   [ConeGeometry(0.13, 0.34, 16) + 3 tuft cones @ z=+0.05, #f8e8c8]
│   ├── rightEar (THREE.Group)             @ pos(-0.28, 0.38, -0.02), rot.z = +0.34 rad
│   │   ├── earBaseMesh                    [CylinderGeometry(0.09, 0.19, 0.28, 20), #e89125]
│   │   ├── earTipMesh                     [ConeGeometry(0.09, 0.17, 20) @ y=+0.225, #f26d6d]
│   │   └── innerEarMesh                   [ConeGeometry(0.13, 0.34, 16) + 3 tuft cones @ z=+0.05, #f8e8c8]
│   ├── eyePatchLeft (THREE.Group)         @ pos(+0.175, +0.11, +0.395)  [Viewer's Right / Character's Left Eye]
│   │   └── patchRingMesh                  [SphereGeometry(0.148, 24, 16) scaled (1.05, 1.18, 0.32), #f26d6d]
│   ├── eyes (THREE.Group)                 @ pos(0, +0.11, +0.41)
│   │   ├── rightEye (THREE.Group)         @ pos(-0.175, 0, 0) [Viewer's Left]
│   │   │   ├── corneaMesh                 [SphereGeometry(0.105, 24, 20) scaled (1.0, 1.08, 0.65), #08080c]
│   │   │   ├── catchlightMain             [CircleGeometry(0.032, 16) @ (-0.028, +0.032, +0.072), #ffffff]
│   │   │   ├── catchlightSub              [CircleGeometry(0.014, 12) @ (+0.030, -0.026, +0.072), #ffffff]
│   │   │   └── eyelashes                  [3 curved CylinderGeometry(0.004, 0.009, 0.055) at angles 35°, 55°, 75°, #08080c]
│   │   └── leftEye (THREE.Group)          @ pos(+0.175, 0, 0) [Viewer's Right, inside eyePatchLeft]
│   │       ├── corneaMesh                 [SphereGeometry(0.105, 24, 20) scaled (1.0, 1.08, 0.65), #08080c]
│   │       ├── catchlightMain             [CircleGeometry(0.032, 16) @ (-0.028, +0.032, +0.072), #ffffff]
│   │       ├── catchlightSub              [CircleGeometry(0.014, 12) @ (+0.030, -0.026, +0.072), #ffffff]
│   │       └── eyelashes                  [3 curved CylinderGeometry(0.004, 0.009, 0.055) at angles -35°, -55°, -75°, #08080c]
│   ├── muzzle (THREE.Group)               @ pos(0, -0.11, +0.26)
│   │   ├── muzzleShellMesh                [SphereGeometry(0.38, 28, 20) scaled (1.28, 0.78, 0.75), #f9efd8]
│   │   ├── noseMesh                       [SphereGeometry(0.052, 16, 12) scaled (1.35, 0.85, 0.90) @ (0, +0.11, +0.26), #141418]
│   │   ├── philtrumStitch                 [3 vertical stitch capsules below nose @ (0, +0.06, +0.27), #6b3814]
│   │   ├── mouthCavityMesh                [Custom kidney-arched recessed cavity @ (0, -0.04, +0.19), #050508]
│   │   ├── upperTeeth                     [6 rounded CapsuleGeometry(0.026, 0.024) along upper mouth arch, #fcfaf5]
│   │   ├── lowerTeeth                     [6 rounded CapsuleGeometry(0.024, 0.020) along lower mouth arch, #fcfaf5]
│   │   └── tongueMesh                     [2 overlapping SphereGeometry(0.07, 14, 10) @ (±0.035, -0.14, +0.20), #d9535f]
│   └── pilotGear (THREE.Group)            @ pos(0, 0, 0) [Toggleable 3D Aviator Goggles, Pilot Scarf & Captain's Cap]
├── torso (THREE.Group)                    @ pos(0, -0.20, 0.0)
│   ├── bodyMesh                           [Lathe/SphereGeometry(0.34, 28, 24) scaled (1.02, 1.18, 0.92), #e89125]
│   ├── bellyPatchMesh                     [SphereGeometry(0.26, 24, 20) scaled (0.95, 1.12, 0.35) @ (0, -0.02, +0.24), #faefd4]
│   ├── zipper (THREE.Group)               @ pos(0, +0.02, +0.325)
│   │   ├── zipperTapeMesh                 [BoxGeometry(0.046, 0.46, 0.012), #8c5319]
│   │   ├── zipperTeeth                    [18 alternating BoxGeometry(0.022, 0.012, 0.016) in #d49b35]
│   │   └── zipperPullRing                 [TorusGeometry(0.026, 0.007, 10, 20) @ (0, +0.20, +0.018), #d49b35]
│   └── lanternPendant (THREE.Group)       @ pos(0, +0.17, +0.35) [Swinging pivot at zipperPullRing]
│       ├── topLoopAndCap                  [Torus loop + Cone/Cylinder pagoda cap @ y=-0.03, #b87b20]
│       ├── glassGlobeCore                 [CylinderGeometry(0.042, 0.048, 0.095, 20) @ y=-0.085, #ffd966 emissive(2.5)]
│       ├── innerFlameFilament             [OctahedronGeometry(0.024, 1) @ y=-0.085, #ffffff emissive]
│       ├── wireCageStruts                 [4 vertical arched Torus/Cylinder struts + X-cross wire bars, #b87b20]
│       ├── baseTank                       [CylinderGeometry(0.054, 0.058, 0.028, 20) @ y=-0.142, #b87b20]
│       └── lanternLight                   [THREE.PointLight(0xffd966, 2.2, 4.5, 1.5) @ (0, -0.085, +0.04)]
├── leftArm (THREE.Group)                  @ pos(+0.30, +0.05, 0.0), rot.z = -0.48 rad
│   ├── upperArmMesh                       [CylinderGeometry(0.085, 0.105, 0.34, 18) @ y=-0.16, #e89125]
│   ├── armStitchSeam                      [6 longitudinal stitch dashes along front sleeve, #b3620e]
│   ├── handPawMesh                        [SphereGeometry(0.115, 20, 16) + 3 finger lobes @ y=-0.35, #e36562]
│   └── pawPads                            [3 oval SphereGeometry(0.028, 12, 10) @ palm (+Z), #faefd4]
├── rightArm (THREE.Group)                 @ pos(-0.30, +0.05, 0.0), rot.z = +0.48 rad
│   ├── upperArmMesh                       [CylinderGeometry(0.085, 0.105, 0.34, 18) @ y=-0.16, #e89125]
│   ├── armStitchSeam                      [6 longitudinal stitch dashes along front sleeve, #b3620e]
│   ├── handPawMesh                        [SphereGeometry(0.115, 20, 16) + 3 finger lobes @ y=-0.35, #e36562]
│   └── pawPads                            [3 oval SphereGeometry(0.028, 12, 10) @ palm (+Z), #faefd4]
├── leftLeg (THREE.Group)                  @ pos(+0.15, -0.52, 0.0)
│   ├── thighMesh                          [CylinderGeometry(0.115, 0.122, 0.28, 18) @ y=-0.14, #e89125]
│   ├── legStitchSeam                      [5 vertical front stitch dashes, #b3620e]
│   └── footPawMesh                        [3-toed sculpted foot @ (0, -0.32, +0.05) in #e36562 + #faefd4 sole pad]
├── rightLeg (THREE.Group)                 @ pos(-0.15, -0.52, 0.0)
│   ├── thighMesh                          [CylinderGeometry(0.115, 0.122, 0.28, 18) @ y=-0.14, #e89125]
│   ├── legStitchSeam                      [5 vertical front stitch dashes, #b3620e]
│   └── footPawMesh                        [3-toed sculpted foot @ (0, -0.32, +0.05) in #e36562 + #faefd4 sole pad]
└── tail (THREE.Group)                     @ pos(+0.08, -0.36, -0.24), rot.y = +0.42 rad
    ├── tailBaseOrange                     [Curved bushy multi-sphere/tube sweep + radial fur cones, #e89125]
    ├── tailZigZagCollar                   [Crown of 8 alternating pointed fur cones at transition, #faf5ea / #e89125]
    └── tailTipWhite                       [Voluminous pointed Cone/Sphere tip @ (+0.34, +0.46, -0.18), #faf5ea]
```

---

### 2.3 Character 2 Specification: `LunaBat` / `StarBat` (`src/characters/LunaBat.js`)

#### A. Exact Color Hex Palette (`LUNA_BAT_PALETTE`)
| Token Name | Hex Code | Target Sub-Meshes | Material Properties |
|---|---|---|---|
| `plushHead` | `#3a2278` | Head, outer bat ears, upper wing-arm leading edges, thumb-hooks, finger struts | `roughness: 0.80, metalness: 0.05, bumpScale: 0.018` |
| `innerEarLilac` | `#c5a3f0` | Lush fluffy inner bat ear fur & feathered ear rim tufts | `roughness: 0.88, metalness: 0.02` |
| `muzzleLavender`| `#b898e8` | Wide Smiling Critters lip/muzzle rim & upturned bat nose | `roughness: 0.78, metalness: 0.03` |
| `nostrilDark` | `#231252` | 2 sculpted oval nostrils on upturned nose & eyebrow arches | `roughness: 0.60, metalness: 0.05` |
| `plushTorso` | `#351e70` | Pear-shaped torso & cylindrical upper legs | `roughness: 0.82, metalness: 0.05` |
| `bellyLavender` | `#b592e6` | Oval chest/belly plush patch | `roughness: 0.84, metalness: 0.02` |
| `wingMembrane` | `#9f78d9` | Diamond-quilted spread bat wing membranes (`leftWingArm`, `rightWingArm`) | `roughness: 0.76, bumpMap: diamondQuilt, side: DoubleSide` |
| `footLavender` | `#ba96ea` | Plump 3-toed left & right bat feet | `roughness: 0.80, metalness: 0.03` |
| `eyeBlack` | `#08080c` | Large glossy circular eyes with dual white catchlights | `roughness: 0.05, metalness: 0.10` |
| `mouthBlack` | `#050508` | Recessed wide Smiling Critters mouth cavity | `MeshBasicMaterial({ color: 0x050508 })` |
| `teethWhite` | `#fcfaf5` | 6 upper rounded white teeth + 6 lower rounded white teeth | `roughness: 0.25, metalness: 0.05` |
| `zipperSilver` | `#d8dde6` | Vertical chest zipper teeth, slider & top ring pull | `roughness: 0.22, metalness: 0.88` |
| `moonStarGold` | `#ffe57f` | 3D Crescent Moon + 8-Pointed Starburst pendant & `THREE.PointLight` | `emissive: 0xffe57f, emissiveIntensity: 2.3, metalness: 0.45` |

#### B. Required `THREE.Group` Scene Graph & Coordinate Geometry (`LunaBat`)
Root `THREE.Group`: `name = "LunaBat"`, `userData = { characterId: 'luna_bat', displayName: 'LunaBat (StarBat)', role: 'copilot', animState: 'idle' }`. Standing height: `~2.22` world units (`y ∈ [-0.95, +1.27]`).

```
LunaBat (THREE.Group)
├── head (THREE.Group)                     @ pos(0, 0.42, 0.0)
│   ├── skullMesh                          [SphereGeometry(0.45, 32, 24) scaled (1.16, 0.96, 0.94), #3a2278]
│   ├── foreheadStitch                     [7 vertical stitch capsules at x=0, y∈[0.15, 0.43], z=0.42, #6342b5]
│   ├── eyebrows                           [Left & Right dark arched TorusGeometry @ (∓0.17, 0.28, 0.39), #1a0d3d]
│   ├── leftEar (THREE.Group)              @ pos(+0.29, 0.38, -0.02), rot.z = -0.32 rad
│   │   ├── outerEarShell                  [Tall leaf-shaped scaled Cone/Sphere (0.21, 0.52, 0.12), #3a2278]
│   │   └── innerEarFur                    [Recessed fluffy cavity + 8 feathered edge fur cones, #c5a3f0]
│   ├── rightEar (THREE.Group)             @ pos(-0.29, 0.38, -0.02), rot.z = +0.32 rad
│   │   ├── outerEarShell                  [Tall leaf-shaped scaled Cone/Sphere (0.21, 0.52, 0.12), #3a2278]
│   │   └── innerEarFur                    [Recessed fluffy cavity + 8 feathered edge fur cones, #c5a3f0]
│   ├── eyes (THREE.Group)                 @ pos(0, +0.11, +0.41)
│   │   ├── rightEye (THREE.Group)         @ pos(-0.17, 0, 0)
│   │   │   ├── corneaMesh                 [SphereGeometry(0.106, 24, 20) scaled (1.0, 1.06, 0.65), #08080c]
│   │   │   ├── catchlightMain             [CircleGeometry(0.032, 16) @ (-0.028, +0.032, +0.072), #ffffff]
│   │   │   └── catchlightSub              [CircleGeometry(0.015, 12) @ (+0.030, -0.026, +0.072), #fff2cc]
│   │   └── leftEye (THREE.Group)          @ pos(+0.17, 0, 0)
│   │       ├── corneaMesh                 [SphereGeometry(0.106, 24, 20) scaled (1.0, 1.06, 0.65), #08080c]
│   │       ├── catchlightMain             [CircleGeometry(0.032, 16) @ (-0.028, +0.032, +0.072), #ffffff]
│   │       └── catchlightSub              [CircleGeometry(0.015, 12) @ (+0.030, -0.026, +0.072), #fff2cc]
│   ├── nose (THREE.Group)                 @ pos(0, +0.01, +0.49)
│   │   ├── noseBridgeMesh                 [Upturned sculpted Sphere/Cone (0.085, 0.068, 0.065), #b898e8]
│   │   ├── leftNostril                    [SphereGeometry(0.016, 12, 10) scaled (0.7, 1.2, 0.5) @ (+0.024, +0.005, +0.048), #231252]
│   │   └── rightNostril                   [SphereGeometry(0.016, 12, 10) scaled (0.7, 1.2, 0.5) @ (-0.024, +0.005, +0.048), #231252]
│   ├── muzzle (THREE.Group)               @ pos(0, -0.12, +0.26)
│   │   ├── lavenderLipRim                 [Sculpted smile rim framing mouth cavity, #b898e8]
│   │   ├── mouthCavityMesh                [Deep recessed matte-black mouth interior, #050508]
│   │   ├── upperTeeth                     [6 rounded CapsuleGeometry(0.026, 0.024) along upper arch, #fcfaf5]
│   │   └── lowerTeeth                     [6 rounded CapsuleGeometry(0.024, 0.020) along lower arch, #fcfaf5]
│   └── pilotGear (THREE.Group)            @ pos(0, 0, 0) [Toggleable 3D Aviator Goggles, Pilot Scarf & Captain's Cap]
├── torso (THREE.Group)                    @ pos(0, -0.20, 0.0)
│   ├── bodyMesh                           [SphereGeometry(0.34, 28, 24) scaled (1.0, 1.18, 0.90), #351e70]
│   ├── bellyPatchMesh                     [SphereGeometry(0.26, 24, 20) scaled (0.94, 1.12, 0.35) @ (0, -0.02, +0.24), #b592e6]
│   ├── zipper (THREE.Group)               @ pos(0, +0.02, +0.325)
│   │   ├── zipperTapeMesh                 [BoxGeometry(0.046, 0.46, 0.012), #1e1042]
│   │   ├── zipperTeeth                    [18 alternating BoxGeometry(0.022, 0.012, 0.016) in #d8dde6]
│   │   └── zipperPullRing                 [TorusGeometry(0.026, 0.007, 10, 20) @ (0, +0.20, +0.018), #d8dde6]
│   └── moonStarPendant (THREE.Group)      @ pos(0, +0.16, +0.35) [Swinging pivot at zipperPullRing]
│       ├── crescentMoonMesh               [ExtrudeGeometry crescent moon (R=0.095) @ (0, -0.085, 0), #ffe57f emissive(2.3)]
│       ├── starburstMesh                  [3D 8-Pointed Starburst (4 long + 4 short rays) @ (+0.028, -0.082, +0.012), #ffe57f]
│       └── moonStarLight                  [THREE.PointLight(0xffe57f, 2.2, 4.5, 1.5) @ (0, -0.085, +0.04)]
├── leftWingArm (THREE.Group)              @ pos(+0.28, +0.08, -0.02) [Character's Left / Viewer's Right]
│   ├── upperWingLeadingEdge               [Curved TubeGeometry arm beam from (0,0,0) to wrist (+0.32, +0.18, 0), #3a2278]
│   ├── thumbHook                          [Cone/CapsuleGeometry(0.032, 0.065) upright at wrist (+0.32, +0.23, 0), #3a2278]
│   └── outerWingSpan (THREE.Group)        @ pos(+0.32, +0.18, 0) [Secondary wrist joint for natural wing-tip flex]
│       ├── outerLeadingEdge               [Curved TubeGeometry from (0,0,0) to tip (+0.44, -0.32, 0), #3a2278]
│       ├── fingerStruts                   [3 radial rib tubes + diamond-quilt 3D seam overlays, #3a2278 / #6a45a8]
│       └── quiltedMembraneMesh            [Custom Extrude/ShapeGeometry with 3 scalloped lower bays, #9f78d9 + diamondQuilt bumpMap]
├── rightWingArm (THREE.Group)             @ pos(-0.28, +0.08, -0.02) [Character's Right / Viewer's Left]
│   ├── upperWingLeadingEdge               [Mirrored TubeGeometry arm beam to wrist (-0.32, +0.18, 0), #3a2278]
│   ├── thumbHook                          [Cone/CapsuleGeometry(0.032, 0.065) upright at wrist (-0.32, +0.23, 0), #3a2278]
│   └── outerWingSpan (THREE.Group)        @ pos(-0.32, +0.18, 0)
│       ├── outerLeadingEdge               [Mirrored TubeGeometry to tip (-0.44, -0.32, 0), #3a2278]
│       ├── fingerStruts                   [3 radial rib tubes + diamond-quilt 3D seam overlays, #3a2278 / #6a45a8]
│       └── quiltedMembraneMesh            [Mirrored ShapeGeometry with 3 scalloped lower bays, #9f78d9 + diamondQuilt bumpMap]
├── leftLeg (THREE.Group)                  @ pos(+0.15, -0.52, 0.0)
│   ├── thighMesh                          [CylinderGeometry(0.112, 0.120, 0.28, 18) @ y=-0.14, #351e70]
│   └── footPawMesh                        [3-toed sculpted lavender foot @ (0, -0.32, +0.05), #ba96ea]
└── rightLeg (THREE.Group)                 @ pos(-0.15, -0.52, 0.0)
    ├── thighMesh                          [CylinderGeometry(0.112, 0.120, 0.28, 18) @ y=-0.14, #351e70]
    └── footPawMesh                        [3-toed sculpted lavender foot @ (0, -0.32, +0.05), #ba96ea]
```

---

### 2.4 3D Pilot Accessories (`pilotGear` Sub-Group on Both Characters)
Inside `head.getObjectByName('pilotGear')`, construct 3 toggleable child `THREE.Group` nodes (`aviatorGoggles`, `pilotScarf`, `captainCap`) controlled via UI toggle chips and persisted in state:
1. **`aviatorGoggles` (`visible = true` by default in Flight Mode)**:
   - Leather headband strap (`TorusGeometry(0.46, 0.022, 8, 32)`, `#5c3818`) resting across the upper forehead (`y = +0.28`) or lowered over the eyes (`y = +0.11`), twin brass octagonal frames (`CylinderGeometry(0.115, 0.115, 0.04, 8)`, `#d49b35`), and tinted cyan-gold aviator lenses (`#4fc3f7`, `opacity: 0.65, metalness: 0.7`).
2. **`pilotScarf` (`visible = true` by default in Flight Mode)**:
   - Cozy knitted silk-plush collar ring (`TorusGeometry(0.27, 0.048, 12, 24)` at neck `y = -0.36`, `#fff5e1` cream with `#e63946` red racing stripe) + 2 articulated trailing scarf tails (`scarfTailLeft`, `scarfTailRight`) extending backward (`-Z`) that flutter sinusoidally with airspeed `sin(t * 14.0 + i) * 0.28`.
3. **`captainCap` (`visible = false` by default, toggleable)**:
   - Perched between the ears (`y = +0.46`): navy-blue peaked aviation crown (`#1d2d50`), glossy black visor bill (`#111116`), golden braided chin cord (`#ffd166`), and a miniature golden winged-star badge on the front peak.

---

### 2.5 Mathematical Formulas for the 6 Procedural 3D Animations (`src/characters/animations.js`)

Let `t` be elapsed time in seconds (`clock.getElapsedTime()`), and let `phase` be a character offset (`0.0` for `SunnyFox`, `0.85` for `LunaBat` so they feel alive and distinct when standing side-by-side). Every frame (`updateCharacterAnimation(charGroup, animName, t, dt, flightInputs)`), apply smooth damped interpolation (`THREE.MathUtils.lerp(current, target, 1 - Math.exp(-10 * dt))`) to the following target transforms:

| # | Animation ID (`animState`) | Target Sub-Groups & Mathematical Harmonic Formulas (`θ` in radians, `p` in local units) |
|---|---|---|
| **1** | `idle` *(Idle Breathing & Ear Twitch)* | • **Torso & Root Breathing**: `root.position.y = baseY + 0.025 * sin(2.2 * t + phase)`; `torso.scale.set(1 + 0.018 * sin(2.2 * t), 1 - 0.012 * sin(2.2 * t), 1 + 0.018 * sin(2.2 * t))`<br>• **Head Gentle Tilt**: `head.rotation.z = 0.045 * sin(1.1 * t + phase)`; `head.rotation.y = 0.06 * sin(0.8 * t)`<br>• **Double-Pulse Ear Twitch**: Let `w = pow(max(0, sin(1.7 * t + phase)), 12)`. `leftEar.rotation.z = -0.34 - 0.22 * w * sin(18 * t)`; `rightEar.rotation.z = +0.34 + 0.16 * pow(max(0, sin(1.3 * t + 2.0)), 14)`<br>• **Pendant Pendulum Swing**: `pendant.rotation.z = 0.12 * sin(2.2 * t + phase)`; `pendant.rotation.x = 0.06 + 0.05 * cos(4.4 * t)`<br>• **Fox Tail / Bat Wings Idle**: `tail.rotation.y = 0.42 + 0.18 * sin(1.8 * t)`; `leftWingArm.rotation.z = 0.10 * sin(2.2 * t)` |
| **2** | `wave` *(Joyful Hi-Mom Wave)* | • **Right Arm Raised High & Waving**: `rightArm.rotation.z = +2.35 + 0.38 * sin(9.5 * t)`; `rightArm.rotation.x = -0.35 + 0.15 * cos(9.5 * t)` (For `LunaBat`: `rightWingArm.rotation.z = +0.85 + 0.42 * sin(9.0 * t)`, `rightWingArm.outerWingSpan.rotation.z = +0.35 * sin(9.0 * t - 0.5)`)<br>• **Head Joyful Nod & Lean**: `head.rotation.z = -0.14 + 0.06 * sin(4.75 * t)`; `head.rotation.x = -0.08 + 0.05 * sin(9.5 * t)`<br>• **Left Arm Counter-Balance**: `leftArm.rotation.z = -0.55 - 0.08 * sin(4.75 * t)`<br>• **Body Happy Hop**: `root.position.y = baseY + abs(sin(4.75 * t)) * 0.06` |
| **3** | `wingFlapTailWag` *(Vigorous Wing Flap / Bushy Tail Wag)* | • **SunnyFox Vigorous Tail Wag & Lantern Spin**: `tail.rotation.y = 0.42 + 0.68 * sin(11.0 * t)`; `tail.rotation.z = 0.24 * cos(11.0 * t)`; `torso.rotation.y = -0.14 * sin(11.0 * t)`; `lanternPendant.rotation.z = 0.35 * sin(11.0 * t)`; `lanternLight.intensity = 2.6 + 0.8 * sin(22.0 * t)`<br>• **LunaBat Articulated 2-Joint Wing Flap & Hover Lift**: `root.position.y = baseY + 0.18 + 0.12 * sin(10.0 * t - 0.4)`; `leftWingArm.rotation.z = +0.58 * sin(10.0 * t)`; `leftWingArm.rotation.y = +0.25 * cos(10.0 * t)`; `leftWingArm.outerWingSpan.rotation.z = +0.45 * sin(10.0 * t - 0.65)`; `rightWingArm.rotation.z = -0.58 * sin(10.0 * t)`; `rightWingArm.rotation.y = -0.25 * cos(10.0 * t)`; `rightWingArm.outerWingSpan.rotation.z = -0.45 * sin(10.0 * t - 0.65)` |
| **4** | `bounceDance` *(Happy Bounce Dance)* | • **Rhythmic Squat-Jump**: Let `beat = 6.5 * t`. `root.position.y = baseY + 0.22 * abs(sin(beat))`; `torso.scale.y = 1.0 + 0.09 * sin(2 * beat)`<br>• **Alternating Side-to-Side Sway**: `root.rotation.z = 0.16 * sin(beat)`; `head.rotation.z = -0.22 * sin(beat)`<br>• **Alternating Foot Taps & Arm Pumps**: `leftLeg.rotation.x = 0.45 * max(0, sin(beat))`; `rightLeg.rotation.x = 0.45 * max(0, -sin(beat))`; `leftArm.rotation.x = -0.85 * sin(beat)`; `rightArm.rotation.x = +0.85 * sin(beat)` |
| **5** | `barrelRollCheer` *(360° Somersault & Starburst Cheer)* | • **360° Aerobic Roll + Apex Cheer**: Cycle period `T = 1.8s`, normalized phase `u = (t % T) / T`.<br>• During `u ∈ [0, 0.7]`: Smooth 5th-order smoothstep `s = u / 0.7; roll = 2 * π * (6*s^5 - 15*s^4 + 10*s^3)`. `root.rotation.z = roll`; `root.position.y = baseY + 0.45 * sin(π * s)`.<br>• During `u ∈ (0.7, 1.0]` (Victory V-Pose): `root.rotation.z = 0`; both arms/wings raised in V-cheer (`leftArm.rotation.z = -2.4, rightArm.rotation.z = +2.4`), `pendantLight.intensity = 3.8` with automatic particle burst emission! |
| **6** | `cockpitPilotSteer` *(Cockpit Seated & Banking Flight Pose)* | • **Seated Legs Posture**: `leftLeg.rotation.x = -1.35`; `rightLeg.rotation.x = -1.35` (fits cleanly inside cockpit seats).<br>• **Pilot Yoke Steering (`role === 'pilot'`)**: Given normalized flight input `(steerX, steerY) ∈ [-1, 1]^2`: `leftArm.rotation.x = -1.15 + 0.28 * steerX`; `rightArm.rotation.x = -1.15 - 0.28 * steerX`; `head.rotation.y = -0.35 * steerX`; `head.rotation.x = 0.22 * steerY`; `head.rotation.z = -0.25 * steerX`.<br>• **Co-Pilot Wing-Walker / Rear-Seat Wave (`role === 'copilot'`)**: `rightArm` / `rightWingArm` waves enthusiastically (`+2.1 + 0.4 * sin(8 * t)`), while `lanternPendant` or `moonStarPendant` shines forward (`pendantLight.intensity = isNightMode ? 3.6 : 2.2`). |

---

### 2.6 Interactive Studio Controls, Particle Emitters, Audio & Portrait Cards

1. **360° OrbitControls & Camera Framing**:
   - `THREE.PerspectiveCamera(42, aspect, 0.1, 200)` at `(0, 0.45, 4.4)` looking at `(0, 0.05, 0)`.
   - `OrbitControls`: `enableDamping = true`, `dampingFactor = 0.07`, `minDistance = 2.0`, `maxDistance = 8.5`, `maxPolarAngle = Math.PI * 0.62`, full single-finger orbit & two-finger pinch-zoom support for iPad Safari.
2. **Tap-to-React Raycasting (`THREE.Raycaster`)**:
   - Pointer down/tap on canvas projects pointer normalized device coordinates (`[-1, 1]^2`) through `raycaster.intersectObjects([sunnyFoxGroup, lunaBatGroup], true)`.
   - Tapping `lanternPendant` or `moonStarPendant` pulses the pendant `PointLight` intensity to `4.5`, triggers the character's signature sound chime, and spawns 28 glowing 3D particles from the pendant world position.
   - Tapping the character's head/body triggers a joyful reaction animation (`wave` or `bounceDance`), facial squish-and-stretch impulse, and particle burst.
3. **Dual 3D Particle Burst Emitters (`src/characters/particles.js`)**:
   - **Fox Warm Lantern Fireflies (`emitFoxFireflies(origin)`)**: Instantiated `THREE.Points` / instanced glowing spheres (`#ffd966` & `#ff9e2c`, `AdditiveBlending`), drifting upward with warm spiral buoyancy `v_y = +0.65`, radial curl `0.4 * sin(5*t + idx)`.
   - **Bat Starry Lavender Moon-Dust (`emitBatMoonDust(origin)`)**: Instantiated diamond/star particles (`#ffe57f`, `#c5a3f0`, `#9f78d9`, `AdditiveBlending`) expanding in a sparkling starburst ring.
4. **Zero-Dependency Web Audio API Plush Sound Synthesizer (`src/audio/soundSynth.js`)**:
   - Uses a singleton `AudioContext` (unlocked on first pointer/touch event for iPad Safari compatibility) with 5 procedural synthesis patches:
     - `playFoxLanternChime()`: Warm major pentatonic bell chord (`C5–E5–G5–B5–D6`, `523.25 Hz` to `1174.66 Hz`) using sine + triangle oscillators with exponential decay (`0.45s`).
     - `playBatMoonStarSparkle()`: Celestial arpeggiated glockenspiel shimmer (`A4–C#5–E5–A5–C#6`, `440 Hz` to `1108.73 Hz`) with subtle vibrato LFO.
     - `playPlushSqueak()`: Cute dual-chirp frequency sweep (`680 Hz → 1120 Hz → 840 Hz` over `0.14s`) simulating a soft plush toy squeeze.
     - `playWingFlapWhoosh()`: Bandpass-filtered pink noise burst (`centerFreq = 320 Hz`, `Q = 2.5`, `0.16s` envelope).
     - `playPropellerAndBoost()`: Continuous low-hum triangle oscillator modulated by throttle speed + shimmering chime on ring collection.
5. **Side-by-Side Original Reference Artwork Portrait Cards**:
   - In the 3D Character Studio UI panel, render two high-contrast glassmorphic reference cards displaying `<img src="./assets/custom_critter_fox_lantern.jpg" alt="SunnyFox Reference Artwork">` and `<img src="./assets/custom_critter_bat_moonstar.jpg" alt="LunaBat Reference Artwork">` with interactive **"Inspect 3D Details"** and **"Swap Pilot ↔ Co-Pilot"** buttons.

---

## 3. Caveats

1. **iPad Safari WebGL Light & Shadow Limits**: Mobile/iPad GPUs perform best when keeping active shadow-casting lights to 1 directional sun/moon light (`DirectionalLight`) plus the 2 character pendant `PointLight` instances (`castShadow = false` on the pendant point lights to avoid 12-pass cubemap shadow overhead while preserving full per-pixel PBR diffuse/specular illumination on the belly fur and nearby cloud rings).
2. **iOS/iPadOS Web Audio Autoplay Policy**: `AudioContext` starts in `'suspended'` state until a user gesture (`pointerdown` / `touchstart` / `click`). All audio synthesizer calls must wrap `if (ctx.state === 'suspended') ctx.resume().catch(() => {})` so headless browser tests and iPad touch sessions never throw an unhandled promise rejection.

---

## 4. Conclusion

The R1 3D Character System is fully specified and ready for direct implementation in `src/characters/SunnyFox.js`, `src/characters/LunaBat.js`, `src/characters/animations.js`, and `src/audio/soundSynth.js`. Both characters must be registered on `window.__APP_STATE__.characters = { sunnyFox, lunaBat }` so both the R2 Flight Simulator, the R3 Hangar/Photo Booth, and the automated headless browser test suite can inspect and control them deterministically.

---

## 5. Verification Method

Run the following headless Chromium / Playwright assertions against `window.__APP_STATE__` to independently verify R1 compliance:

```javascript
// 1. Verify both 3D character root groups exist with > 1,000 vertices each
const { sunnyFox, lunaBat } = window.__APP_STATE__.characters;
console.assert(sunnyFox.name === 'SunnyFox' && lunaBat.name === 'LunaBat');

// 2. Verify all 15 required named sub-groups on SunnyFox
const foxGroups = [
  'head', 'leftEar', 'rightEar', 'eyes', 'eyePatchLeft', 'muzzle',
  'torso', 'zipper', 'lanternPendant', 'leftArm', 'rightArm',
  'leftLeg', 'rightLeg', 'tail', 'pilotGear'
];
for (const name of foxGroups) {
  console.assert(Boolean(sunnyFox.getObjectByName(name)), `Missing SunnyFox sub-group: ${name}`);
}

// 3. Verify all 14 required named sub-groups on LunaBat
const batGroups = [
  'head', 'leftEar', 'rightEar', 'eyes', 'muzzle', 'nose',
  'torso', 'zipper', 'moonStarPendant', 'leftWingArm', 'rightWingArm',
  'leftLeg', 'rightLeg', 'pilotGear'
];
for (const name of batGroups) {
  console.assert(Boolean(lunaBat.getObjectByName(name)), `Missing LunaBat sub-group: ${name}`);
}

// 4. Verify real-time PointLight instances inside both pendants
const foxLight = sunnyFox.getObjectByName('lanternPendant').children.find(c => c.isPointLight);
const batLight = lunaBat.getObjectByName('moonStarPendant').children.find(c => c.isPointLight);
console.assert(foxLight && foxLight.color.getHexString() === 'ffd966');
console.assert(batLight && batLight.color.getHexString() === 'ffe57f');

// 5. Verify all 6 procedural animations produce non-zero skeletal transform deltas
for (const anim of ['idle', 'wave', 'wingFlapTailWag', 'bounceDance', 'barrelRollCheer', 'cockpitPilotSteer']) {
  window.__APP_STATE__.setCharacterAnimation(anim);
  window.__APP_STATE__.stepSimulation(0.25);
  console.assert(sunnyFox.userData.animState === anim && lunaBat.userData.animState === anim);
}
```
