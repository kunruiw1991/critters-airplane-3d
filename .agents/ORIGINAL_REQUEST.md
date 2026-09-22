# Original User Request

## 2026-09-22T17:25:30Z

Build a standalone, zero-backend 3D WebGL / Three.js Interactive Web Application & Flight Adventure Game ("Smiling Critters 3D Sky & Airplane Adventure: Bay Area ✈️ Boston") designed for Kunrui's daughter on her iPad in Boston (no mentions of Grandma—focus strictly on Mom in San Francisco / Bay Area ↔ Daughter in Boston). The application brings Kunrui's two custom-designed Smiling Critters characters to life as fully articulated, animated 3D moving characters and pairs them with today's "Airplane" theme—piloting customizable 3D airplanes from the Golden Gate Bridge in San Francisco across cloud islands, rainbow rings, and starlight skies to land in Boston, complete with a 360° 3D Character & Airplane Hangar, Co-Pilot Wing-Walker stunts, Cockpit Photo Booth, and full offline-ready iPad PWA deployment for GitHub Pages.

Working directory: /usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d
Integrity mode: development

Reference Artwork saved in working directory:
- `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/assets/custom_critter_fox_lantern.jpg` (Character 1: Custom Golden-Orange Fox Smiling Critter with Glowing Lantern Pendant)
- `/usr/local/google/home/kunruiwang/teamwork_projects/critters_airplane_3d/assets/custom_critter_bat_moonstar.jpg` (Character 2: Custom Indigo-Violet Bat Smiling Critter with Quilted Wings & Glowing Crescent Moon + Starburst Pendant)

## Requirements

### R1. Two Fully Articulated 3D Moving Custom Smiling Critters Characters (WebGL / Three.js)
Faithfully construct, rig, and animate both of Kunrui's custom Smiling Critters designs as interactive 3D articulated character models (`THREE.Group` skeletal/hierarchical rigs with procedural plush textures, normal/bump stitching seams, and real-time point/emissive lighting):
1. **Character 1 — "SunnyFox / LanternFox" (Golden-Orange Fox Smiling Critter)**:
   - **Head & Ears**: Golden-orange plush head (`#e89125`) with fluffy cheek tufts, tall pointed fox ears with coral-pink tips (`#f26d6d`) and cream inner ear fur (`#f8e8c8`), vertical center-seam plush stitching down the forehead and snout, wide Smiling Critters grin with cream muzzle (`#f9efd8`) and black nose, large glossy black eyes with dual white catchlights, 3 upper eyelashes per eye, and her **signature asymmetric coral-pink eye patch ring around her left eye** (viewer's right).
   - **Body, Limbs & Tail**: Golden-orange torso with soft cream oval belly (`#faefd4`), coral-pink hands and feet (`#e36562`) with cream paw pads, huge bushy golden-orange tail with a snow-white tip (`#faf5ea`), vertical brass zipper down the chest, and a **3D glowing golden camping/storm lantern pendant** (`THREE.PointLight` + emissive warm amber core `#ffd966` inside a bronze lantern cage) swinging from the zipper pull.
2. **Character 2 — "LunaBat / StarBat" (Indigo-Violet Bat Smiling Critter)**:
   - **Head & Ears**: Deep royal indigo-purple plush head (`#3a2278`) with tall, fluffy oversized bat ears featuring pastel lilac-lavender inner fur (`#c5a3f0`), vertical center forehead stitch seam, wide Smiling Critters grin framed by a pastel lavender muzzle/lip rim (`#b898e8`), upturned bat nose with two nostrils, and large glossy black eyes with dual white catchlights.
   - **Body, Wings & Pendant**: Deep indigo-purple torso (`#351e70`) with pastel lavender belly patch (`#b592e6`), pastel lavender 3-toed feet (`#ba96ea`), **two articulated spread bat wings** attached to the arms (deep indigo upper wing edges with diamond-quilted pastel lavender wing membranes `#9f78d9` and thumb-hooks at the top joints that flap and glide in 3D!), vertical silver metal zipper down the chest, and a **3D glowing golden Crescent Moon + 8-Pointed Starburst pendant** (`#ffe57f` emissive glow) hanging from the zipper pull.
3. **3D Character Animations & Interactive Expressions**:
   - Real-time 3D procedural animations for both characters: **Idle Breathing & Ear Twitch**, **Joyful Wave**, **Wing Flap / Tail Wag**, **Happy Bounce Dance**, **Barrel-Roll Cheer**, and **Cockpit Pilot Steer** (wearing optional 3D aviator goggles, pilot scarf, or captain's cap).
   - Interactive 360° touch/mouse orbit camera (`OrbitControls`), tap-to-react animations with synthesized plush sound effects & glowing particle bursts (warm lantern fireflies for Fox, starry lavender moon-dust for Bat), and side-by-side reference portrait cards displaying Kunrui's original artwork (`assets/custom_critter_fox_lantern.jpg` and `assets/custom_critter_bat_moonstar.jpg`).

### R2. 3D "Airplane" Sky Adventure & Co-Pilot Flight Simulator (San Francisco ✈️ Boston)
Build a smooth, 60 FPS 3D WebGL flight adventure game where the two custom 3D Smiling Critters fly together from **Mom in San Francisco (Golden Gate Bridge)** to **Daughter in Boston (Zakim Bridge & Boston Skyline)**:
- **Pilot & Co-Pilot Tandem Cockpit**: Both 3D characters sit inside (or wing-walk on!) the 3D airplane in real time—one piloting in the front cockpit while the co-pilot waves, flaps bat wings, or shines the golden lantern from the rear seat / wing! Players can swap Pilot ↔ Co-Pilot roles at any time with 1 tap.
- **3D Flight Controls (iPad Touch & Keyboard)**: Responsive virtual thumbstick / touch-drag flight steering on iPad (plus `WASD` / Arrow keys on desktop), **Turbo Starlight Boost** button, **360° Barrel Roll / Loop-de-Loop Stunt** button, and **Heart Parachute Care-Package Drop** button.
- **3D Sky Course & Weather Time-of-Day Modes**:
  - Fly through 3 scenic sky zones along the SF → Boston flight path: **Zone 1: Golden Gate Sunrise Takeoff**, **Zone 2: Rainbow Cloud Archipelago & Paper-Airplane Wind Tunnels**, and **Zone 3: Starry Night Aurora Approach into Boston** (where Fox's glowing lantern and Bat's glowing moon-star pendant light up hidden starlight rings in the dark!).
  - Collect floating **Golden Lanterns**, **Crescent Moon Stars**, **Music Note Boosters**, and **Mom's Heart Care Packages** while flying through glowing 3D rings and paper-airplane squadrons.

### R3. 3D Airplane Hangar Builder, Wing Decal Studio & Cockpit Photo Booth
Provide an interactive 3D Hangar where she can customize her aircraft and capture 3D postcards:
- **3 Selectable 3D Airplanes**:
  1. **Critter Cloud Biplane** (twin-wing vintage biplane with spinning 3D propeller and duo tandem seats)
  2. **Starlight Supersonic Jet** (sleek swept-wing jet with twin glowing neon afterburners)
  3. **Origami Dream Glider** (giant magical folded paper-airplane cruiser with glowing rune/starlight trails)
- **Airplane Paint, Contrail & Wing Emblem Customizer**: Customize fuselage & wing paint palettes (Sunset Fox Amber, Midnight Bat Indigo, HUNTR/X Golden Neon, Mint Cloud), propeller types, sky-writing contrail particles (Rainbow Ribbon, Lantern Fireflies, Starlight Moon Dust, Heart Bubbles), and wing emblems.
- **3D Cockpit & Sky Photo Booth ("Send 3D Flight Postcard to Mom")**: Pose the 3D Fox & Bat characters with their custom airplane against SF/Boston sky backdrops, add stickers/captions, and export a high-resolution PNG postcard image (`canvas.toDataURL('image/png')`) to share with Mom, with all custom planes and photos persisted in `localStorage`.

### R4. Zero-Backend iPad PWA Packaging & GitHub Pages Readiness
- **Offline-First iPad Web App**: Include iPad PWA meta tags (`apple-mobile-web-app-capable`), `manifest.json`, and `./sw.js` Service Worker with relative paths so it installs to the iPad Home Screen via Safari (**Share → Add to Home Screen**) and caches all 3D code, Three.js engine, and character reference images offline.
- **Standalone & `docs/` Build**: Provide both a modular source tree (`src/`), a GitHub Pages-ready `docs/` directory (with `.nojekyll` and `assets/`), and a single-file bundle (`dist/index.html`) so it can be immediately pushed and served on GitHub Pages.

## Acceptance Criteria

### Automated Functional & Headless Browser 3D Verification
- [ ] Application loads cleanly in headless Chromium with zero `console.error` or uncaught `pageerror` exceptions across all views (3D Character Studio, 3D Airplane Hangar, 3D Sky Flight Adventure, and Photo Booth / Gallery).
- [ ] **3D Custom Smiling Critters Verification**: Programmatic inspection of the live 3D scene graph (`window.__APP_STATE__` / Three.js scene) verifies both **SunnyFox (LanternFox)** and **LunaBat (StarBat)** 3D character meshes are instantiated with non-zero vertex/geometry counts, distinct articulated child groups (ears, eyes, zipper + glowing lantern pendant for Fox; ears, quilted bat wings, zipper + glowing crescent moon/star pendant for Bat), active skeletal/procedural animation updates across frames, and role swapping (Pilot ↔ Co-Pilot).
- [ ] **3D Airplane Flight Simulator Verification**: Programmatic test confirms starting the SF ✈️ Boston 3D flight, advancing simulation frames, verifying 3D airplane position/rotation updates in response to steering/boost/barrel-roll inputs, ring/item collection score increments, Day/Sunset/Night lighting mode switches (activating Fox's lantern & Bat's moon-star point lights), and completion/landing state.
- [ ] **3D Hangar Customizer & Photo Booth Verification**: Programmatic test confirms switching between all 3 3D aircraft models (Biplane, Supersonic Jet, Origami Glider), changing wing paint/contrail styles, rendering the 3D scene to a downloadable PNG Flight Postcard (`data:image/png;base64,...`), and persisting custom aircraft configurations across `page.reload()` via `localStorage`.
