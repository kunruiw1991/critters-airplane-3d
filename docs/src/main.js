// Main Application Controller & Unified window.__APP_STATE__ Verification Contract
// Strictly Mom in San Francisco (Golden Gate Bridge) <-> Daughter in Boston (Zakim Bridge & Skyline)

import { soundSynth } from './audio/soundSynth.js';
import { buildSunnyFox } from './characters/SunnyFox.js';
import { buildLunaBat } from './characters/LunaBat.js';
import { updateCharacterAnimation, normalizeAnimationName } from './characters/animations.js';
import { ParticleBurstSystem } from './characters/particles.js';
import { createAirplane, PAINT_PALETTES } from './aircraft/aircraftFactory.js';
import { ContrailSystem } from './aircraft/contrailSystem.js';
import { SkyCourseManager, ZONE_DEFINITIONS } from './flight/skyCourse.js';

const THREE = window.THREE;

const CONFIG_STORAGE_KEY = 'critters_airplane_3d_config_v1';
const POSTCARDS_STORAGE_KEY = 'critters_airplane_3d_postcards_v1';

export class CrittersAirplaneApp {
  constructor() {
    this.canvas = document.getElementById('webgl-canvas');
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: false,
      preserveDrawingBuffer: true,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.setSize(window.innerWidth || 1280, window.innerHeight || 720);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color('#2b6cb0');
    this.scene.fog = new THREE.FogExp2('#87ceeb', 0.0022);

    this.camera = new THREE.PerspectiveCamera(
      48,
      (window.innerWidth || 1280) / (window.innerHeight || 720),
      0.1,
      2500
    );
    this.camera.position.set(0, 0.85, 5.2);

    const OrbitControlsCtor =
      THREE.OrbitControls ||
      (globalThis.THREE_examples_js_controls_OrbitControls &&
        globalThis.THREE_examples_js_controls_OrbitControls.OrbitControls);
    if (OrbitControlsCtor && !THREE.OrbitControls) {
      THREE.OrbitControls = OrbitControlsCtor;
    }
    this.controls = new OrbitControlsCtor(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.minDistance = 2.0;
    this.controls.maxDistance = 16.0;
    this.controls.target.set(0, 0.1, 0);

    // Scene Lighting
    this.ambientLight = new THREE.AmbientLight(0xd9eeff, 0.9);
    this.scene.add(this.ambientLight);

    this.sunLight = new THREE.DirectionalLight(0xfff7e6, 1.45);
    this.sunLight.position.set(18, 32, 24);
    this.scene.add(this.sunLight);

    this.rimLight = new THREE.DirectionalLight(0xc5a3f0, 0.55);
    this.rimLight.position.set(-16, 12, -18);
    this.scene.add(this.rimLight);

    // Starfield & Aurora Curtains for Night / Zone 3
    this._buildSkyEnvironment();

    // Build Articulated 3D Characters (R1)
    this.sunnyFox = buildSunnyFox();
    this.lunaBat = buildLunaBat();

    const makeCharProxy = (grp, strId) => {
      const proxyTarget = { id: strId, group: grp };
      return new Proxy(proxyTarget, {
        get(target, prop) {
          if (prop === 'id') return strId;
          if (prop === 'group') return grp;
          const val = grp[prop];
          return typeof val === 'function' ? val.bind(grp) : val;
        },
        set(target, prop, val) {
          if (prop === 'id') return true;
          grp[prop] = val;
          return true;
        },
      });
    };

    this.sunnyFoxProxy = makeCharProxy(this.sunnyFox, 'SunnyFox');
    this.lunaBatProxy = makeCharProxy(this.lunaBat, 'LunaBat');

    // Particle Bursts & Contrails
    this.particleBursts = new ParticleBurstSystem(this.scene);
    this.contrailSystem = new ContrailSystem('rainbow_ribbon');
    this.scene.add(this.contrailSystem.group);

    // Build 3-Zone SF -> Boston Sky Course (R2)
    this.skyCourse = new SkyCourseManager(this.scene);

    // Initialize State Tree
    this.state = {
      ready: false,
      activeView: 'character_studio',
      renderer: this.renderer,
      scene: this.scene,
      camera: this.camera,
      controls: this.controls,
      frameCount: 0,
      elapsedTime: 0,
      audioMuted: false,
      soundSynth,
      characters: {
        SunnyFox: this.sunnyFoxProxy,
        sunnyFox: this.sunnyFoxProxy,
        LunaBat: this.lunaBatProxy,
        lunaBat: this.lunaBatProxy,
      },
      flight: {
        active: false,
        paused: false,
        completed: false,
        flightState: 'ready_sf',
        originCity: 'San Francisco (Golden Gate Bridge)',
        destinationCity: 'Boston (Zakim Bridge & Skyline)',
        pilotId: 'SunnyFox',
        coPilotId: 'LunaBat',
        coPilotMode: 'rear_cockpit',
        roleSwapCount: 0,
        zoneId: 1,
        zoneName: ZONE_DEFINITIONS[1].name,
        timeOfDay: 'day',
        pendantLightsActive: false,
        revealedStarlightRingsCount: 0,
        progress: 0,
        distanceMiles: 0,
        speed: 0,
        steerX: 0,
        steerY: 0,
        position: { x: 0, y: 12.0, z: 0 },
        rotation: { pitch: 0, yaw: 0, roll: 0 },
        boostActive: false,
        boostTimer: 0,
        boostCount: 0,
        barrelRollActive: false,
        barrelRollProgress: 0,
        barrelRollAngle: 0,
        barrelRollCount: 0,
        carePackagesDropped: 0,
        score: 0,
        ringsPassed: 0,
        collectedCounts: {
          golden_lantern: 0,
          crescent_moon_star: 0,
          music_note_booster: 0,
          mom_heart_care_package: 0,
          sky_ring: 0,
          starlight_ring: 0,
          paper_airplane_squadron: 0,
        },
      },
      hangar: {
        modelId: 'biplane',
        paintPaletteId: 'sunset_fox_amber',
        propellerStyleId: 'classic_wood_brass',
        contrailStyleId: 'rainbow_ribbon',
        wingEmblemId: 'fox_lantern_crest',
        airplaneGroup: null,
        pilotSeatAnchor: null,
        coPilotSeatAnchor: null,
        propellerGroup: null,
        contrailSystem: this.contrailSystem.group,
        vertexCount: 0,
        primaryColorHex: '#e89125',
        secondaryColorHex: '#f26d6d',
        storageKey: CONFIG_STORAGE_KEY,
      },
      photoBooth: {
        backdropId: 'sf_golden_gate_sunrise',
        poseId: 'tandem_wave',
        captionText: 'Flying from Mom in San Francisco ✈️ to Boston with SunnyFox & LunaBat! 💖',
        stickerIds: ['🌉 SFO ✈️ BOS 🏙️', '🦊 SunnyFox & LunaBat 🦇', '💖 Love You Mom! 💖'],
        lastCapturedDataUrl: null,
        savedPostcards: [],
        storageKey: POSTCARDS_STORAGE_KEY,
      },
    };

    // Hydrate saved configuration & postcards from localStorage
    this.loadConfigFromLocalStorage();

    // Build initial 3D Airplane and mount characters
    this._rebuildAirplane();

    // Apply initial view and time-of-day lighting
    this.setTimeOfDay(this.state.flight.timeOfDay);
    this.setView('character_studio');

    // Bind UI & Input Listeners
    this._bindDomEvents();
    this._exposeAppStateContract();

    this.state.ready = true;
    this.stepSimulation(1, 1 / 60);

    // Start 60 FPS loop
    this._lastRafTime = performance.now();
    const animate = (now) => {
      requestAnimationFrame(animate);
      const rawDt = Math.min((now - this._lastRafTime) / 1000, 0.05);
      this._lastRafTime = now;
      this.stepSimulation(1, rawDt > 0 ? rawDt : 1 / 60);
    };
    requestAnimationFrame(animate);
  }

  _buildSkyEnvironment() {
    // Starfield particles
    const starCount = 450;
    const positions = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 400;
      positions[i * 3 + 1] = 10 + Math.random() * 140;
      positions[i * 3 + 2] = -Math.random() * 1900;
    }
    const starGeom = new THREE.BufferGeometry();
    starGeom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.starfieldMat = new THREE.PointsMaterial({
      color: 0xffe57f,
      size: 0.9,
      transparent: true,
      opacity: 0.0,
    });
    this.starfield = new THREE.Points(starGeom, this.starfieldMat);
    this.starfield.name = 'NightStarfield';
    this.scene.add(this.starfield);

    // Aurora Borealis Ribbon Curtains
    const auroraGeom = new THREE.PlaneGeometry(180, 32, 32, 4);
    this.auroraMat = new THREE.MeshBasicMaterial({
      color: 0x56d8c0,
      transparent: true,
      opacity: 0.0,
      side: THREE.DoubleSide,
    });
    this.auroraMesh = new THREE.Mesh(auroraGeom, this.auroraMeshMat || this.auroraMat);
    this.auroraMesh.name = 'AuroraCurtain';
    this.auroraMesh.position.set(0, 42, -1500);
    this.scene.add(this.auroraMesh);
  }

  _rebuildAirplane() {
    if (this.airplaneGroup) {
      // Detach characters before removing old aircraft
      if (this.sunnyFox.parent) this.sunnyFox.parent.remove(this.sunnyFox);
      if (this.lunaBat.parent) this.lunaBat.parent.remove(this.lunaBat);
      this.scene.remove(this.airplaneGroup);
    }

    this.airplaneGroup = createAirplane({
      modelId: this.state.hangar.modelId,
      paintPaletteId: this.state.hangar.paintPaletteId,
      propellerStyleId: this.state.hangar.propellerStyleId,
      wingEmblemId: this.state.hangar.wingEmblemId,
      coPilotMode: this.state.flight.coPilotMode,
    });
    this.scene.add(this.airplaneGroup);

    this.state.hangar.airplaneGroup = this.airplaneGroup;
    this.state.hangar.pilotSeatAnchor = this.airplaneGroup.pilotSeatAnchor;
    this.state.hangar.coPilotSeatAnchor = this.airplaneGroup.coPilotSeatAnchor;
    this.state.hangar.propellerGroup = this.airplaneGroup.propellerGroup;
    this.state.hangar.vertexCount = this.airplaneGroup.vertexCount;
    this.state.hangar.primaryColorHex = this.airplaneGroup.primaryColorHex;
    this.state.hangar.secondaryColorHex = this.airplaneGroup.secondaryColorHex;

    this._mountCrewIntoSeats();
    this._syncAirplaneTransform();
  }

  _mountCrewIntoSeats() {
    const pilotChar = this.state.flight.pilotId === 'SunnyFox' ? this.sunnyFox : this.lunaBat;
    const coPilotChar = this.state.flight.coPilotId === 'SunnyFox' ? this.sunnyFox : this.lunaBat;

    pilotChar.userData.role = 'pilot';
    coPilotChar.userData.role = 'copilot';

    const pilotAnchor = this.airplaneGroup.pilotSeatAnchor;
    const coPilotAnchor = this.airplaneGroup.coPilotSeatAnchor;

    if (pilotChar.parent) pilotChar.parent.remove(pilotChar);
    if (coPilotChar.parent) coPilotChar.parent.remove(coPilotChar);

    pilotChar.position.set(0, 0, 0);
    pilotChar.rotation.set(0, 0, 0);
    coPilotChar.position.set(0, 0, 0);
    coPilotChar.rotation.set(0, 0, 0);

    pilotAnchor.add(pilotChar);
    coPilotAnchor.add(coPilotChar);

    this._updateSeatAnchorsForActiveView();
    this._updateRoleLabelsInDom();
  }

  _updateSeatAnchorsForActiveView() {
    if (!this.airplaneGroup) return;
    const pilotAnchor = this.airplaneGroup.pilotSeatAnchor;
    const coPilotAnchor = this.airplaneGroup.coPilotSeatAnchor;

    if (this.state.activeView === 'character_studio') {
      // In Character Studio, display SunnyFox & LunaBat standing full-scale side-by-side in front of the aircraft!
      pilotAnchor.position.set(-1.12, 0.15, 2.25);
      pilotAnchor.scale.setScalar(1.0);
      coPilotAnchor.position.set(1.12, 0.15, 2.25);
      coPilotAnchor.scale.setScalar(1.0);
    } else {
      pilotAnchor.position.set(0, 0.48, 0.78);
      pilotAnchor.scale.setScalar(0.56);
      if (this.state.flight.coPilotMode === 'wing_walker') {
        coPilotAnchor.position.set(1.85, 0.62, -0.05);
      } else {
        coPilotAnchor.position.set(0, 0.56, -0.68);
      }
      coPilotAnchor.scale.setScalar(0.56);
    }
  }

  _syncAirplaneTransform() {
    if (!this.airplaneGroup) return;
    if (this.state.activeView === 'flight_simulator') {
      const pos = this.state.flight.position;
      const rot = this.state.flight.rotation;
      this.airplaneGroup.position.set(pos.x, pos.y, pos.z);
      this.airplaneGroup.rotation.set(rot.pitch, Math.PI + rot.yaw, rot.roll);
    } else if (this.state.activeView === 'character_studio') {
      this.airplaneGroup.position.set(0, -0.15, 0);
      this.airplaneGroup.rotation.set(0, 0, 0);
    } else if (this.state.activeView === 'hangar') {
      this.airplaneGroup.position.set(0, 0.2, 0);
      this.airplaneGroup.rotation.set(0.08, this.state.elapsedTime * 0.35, 0);
    } else if (this.state.activeView === 'photo_booth') {
      this.airplaneGroup.position.set(0, 0.25, 0);
      this.airplaneGroup.rotation.set(0.06, -0.35, 0.08);
    }
    this.airplaneGroup.updateMatrixWorld(true);
  }

  // ==================== PUBLIC API METHODS ====================

  setView(view) {
    const validViews = ['character_studio', 'flight_simulator', 'hangar', 'photo_booth'];
    if (!validViews.includes(view)) return;
    this.state.activeView = view;

    document.querySelectorAll('.nav-tab-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.view === view);
    });
    document.querySelectorAll('.view-overlay').forEach((panel) => {
      panel.classList.toggle('active', panel.dataset.view === view);
    });

    this._updateSeatAnchorsForActiveView();

    if (view === 'character_studio') {
      this.controls.enabled = true;
      this.camera.position.set(0, 0.55, 5.5);
      this.controls.target.set(0, 0.15, 2.25);
      this.controls.update();
    } else if (view === 'hangar') {
      this.controls.enabled = true;
      this.camera.position.set(4.6, 2.8, 6.2);
      this.controls.target.set(0, 0.3, 0);
      this.controls.update();
    } else if (view === 'photo_booth') {
      this.controls.enabled = true;
      this.camera.position.set(0.6, 1.65, 5.2);
      this.controls.target.set(0, 0.45, 0.2);
      this.controls.update();
      this.setPhotoPose(this.state.photoBooth.poseId);
    } else if (view === 'flight_simulator') {
      this.controls.enabled = false;
      this.setCharacterAnimation('SunnyFox', 'cockpitPilotSteer');
      this.setCharacterAnimation('LunaBat', 'cockpitPilotSteer');
    }

    this._syncAirplaneTransform();
    this.renderer.render(this.scene, this.camera);
  }

  setCharacterAnimation(charIdOrAnimName, maybeAnimName) {
    if (!maybeAnimName) {
      // Single argument sets animation on both characters
      const anim = charIdOrAnimName;
      updateCharacterAnimation(this.sunnyFox, anim, this.state.elapsedTime, 1 / 60, this.state.flight);
      updateCharacterAnimation(this.lunaBat, anim, this.state.elapsedTime, 1 / 60, this.state.flight);
    } else {
      const target = charIdOrAnimName.toLowerCase();
      if (target === 'sunnyfox' || target === 'sunny_fox' || target === 'both') {
        updateCharacterAnimation(this.sunnyFox, maybeAnimName, this.state.elapsedTime, 1 / 60, this.state.flight);
      }
      if (target === 'lunabat' || target === 'luna_bat' || target === 'both') {
        updateCharacterAnimation(this.lunaBat, maybeAnimName, this.state.elapsedTime, 1 / 60, this.state.flight);
      }
    }

    document.querySelectorAll('[data-anim-btn]').forEach((btn) => {
      btn.classList.toggle(
        'active',
        normalizeAnimationName(btn.dataset.animBtn) ===
          normalizeAnimationName(this.sunnyFox.currentAnimation)
      );
    });
  }

  triggerCharacterTapReaction(charId = 'SunnyFox') {
    const isFox = String(charId).toLowerCase().includes('fox');
    const charGroup = isFox ? this.sunnyFox : this.lunaBat;
    const worldPos = new THREE.Vector3();
    charGroup.getWorldPosition(worldPos);
    worldPos.y += 0.4;

    if (isFox) {
      this.sunnyFox.pendantLight.intensity = 4.5;
      this.particleBursts.emitFoxFireflies(worldPos);
      soundSynth.playFoxLanternChime();
      this.setCharacterAnimation('SunnyFox', 'wave');
    } else {
      this.lunaBat.pendantLight.intensity = 4.5;
      this.particleBursts.emitBatMoonDust(worldPos);
      soundSynth.playBatMoonStarSparkle();
      this.setCharacterAnimation('LunaBat', 'wingFlapTailWag');
    }
    return {
      characterId: isFox ? 'SunnyFox' : 'LunaBat',
      pendantIntensity: charGroup.pendantLight.intensity,
      particlesEmitted: this.particleBursts.totalEmitted,
    };
  }

  toggleAccessory(charId, accessoryName, forceValue) {
    const isFox = String(charId).toLowerCase().includes('fox');
    const charGroup = isFox ? this.sunnyFox : this.lunaBat;
    const gear = charGroup.parts.pilotGear;
    if (!gear) return false;
    const item = gear.getObjectByName(accessoryName);
    if (!item) return false;
    item.visible = typeof forceValue === 'boolean' ? forceValue : !item.visible;
    this.saveConfigToLocalStorage();
    return item.visible;
  }

  swapRoles() {
    const prevPilot = this.state.flight.pilotId;
    this.state.flight.pilotId = this.state.flight.coPilotId;
    this.state.flight.coPilotId = prevPilot;
    this.state.flight.roleSwapCount += 1;

    this._mountCrewIntoSeats();

    const burstOrigin = new THREE.Vector3();
    this.airplaneGroup.getWorldPosition(burstOrigin);
    this.particleBursts.emitCelebrationBurst(burstOrigin);
    soundSynth.playRoleSwapDuoChime();
    this.saveConfigToLocalStorage();

    return {
      pilotId: this.state.flight.pilotId,
      coPilotId: this.state.flight.coPilotId,
      roleSwapCount: this.state.flight.roleSwapCount,
    };
  }

  setCoPilotMode(mode) {
    const valid = mode === 'wing_walker' ? 'wing_walker' : 'rear_cockpit';
    this.state.flight.coPilotMode = valid;
    this._updateSeatAnchorsForActiveView();
    this.saveConfigToLocalStorage();
    const btn = document.getElementById('btn-copilot-mode');
    if (btn) {
      btn.textContent =
        valid === 'wing_walker' ? '🦇 Mode: Wing-Walker' : '🪑 Mode: Rear Cockpit';
    }
    return valid;
  }

  toggleCoPilotMode() {
    return this.setCoPilotMode(
      this.state.flight.coPilotMode === 'rear_cockpit' ? 'wing_walker' : 'rear_cockpit'
    );
  }

  startFlight() {
    this.state.flight.active = true;
    this.state.flight.paused = false;
    if (this.state.flight.completed) {
      this.resetFlight();
      this.state.flight.active = true;
    }
    this.state.flight.flightState = 'cruising';
    this.state.flight.speed = 24.0;
    this.setCharacterAnimation('SunnyFox', 'cockpitPilotSteer');
    this.setCharacterAnimation('LunaBat', 'cockpitPilotSteer');
    const banner = document.getElementById('boston-landing-banner');
    if (banner) banner.classList.remove('visible');
    this._updateFlightHudDom();
  }

  resetFlight() {
    const f = this.state.flight;
    f.active = false;
    f.paused = false;
    f.completed = false;
    f.flightState = 'ready_sf';
    f.zoneId = 1;
    f.zoneName = ZONE_DEFINITIONS[1].name;
    f.progress = 0;
    f.distanceMiles = 0;
    f.speed = 0;
    f.steerX = 0;
    f.steerY = 0;
    f.position = { x: 0, y: 12.0, z: 0 };
    f.rotation = { pitch: 0, yaw: 0, roll: 0 };
    f.boostActive = false;
    f.boostTimer = 0;
    f.barrelRollActive = false;
    f.barrelRollProgress = 0;
    f.barrelRollAngle = 0;
    this.skyCourse.resetCollectibles();
    const banner = document.getElementById('boston-landing-banner');
    if (banner) banner.classList.remove('visible');
    this._syncAirplaneTransform();
    this._updateFlightHudDom();
  }

  setSteering(steerX, steerY) {
    this.state.flight.steerX = THREE.MathUtils.clamp(Number(steerX) || 0, -1.0, 1.0);
    this.state.flight.steerY = THREE.MathUtils.clamp(Number(steerY) || 0, -1.0, 1.0);
  }

  triggerBoost() {
    this.state.flight.boostActive = true;
    this.state.flight.boostTimer = 3.0;
    this.state.flight.boostCount += 1;
    this.state.flight.score += 50;
    this.state.flight.speed = 51.6;
    soundSynth.playPropellerAndBoost();
    this._updateFlightHudDom();
  }

  triggerBarrelRoll() {
    this.state.flight.barrelRollActive = true;
    this.state.flight.barrelRollProgress = 0.0;
    this.state.flight.barrelRollCount += 1;
    this.state.flight.score += 100;
    this.setCharacterAnimation('SunnyFox', 'barrelRollCheer');
    this.setCharacterAnimation('LunaBat', 'barrelRollCheer');
    soundSynth.playWingFlapWhoosh();
    this._updateFlightHudDom();
  }

  dropHeartPackage() {
    const origin = new THREE.Vector3(
      this.state.flight.position.x,
      this.state.flight.position.y - 1.2,
      this.state.flight.position.z
    );
    this.skyCourse.spawnHeartCarePackageDrop(origin);
    this.state.flight.carePackagesDropped += 1;
    this.state.flight.score += 75;
    soundSynth.playHeartDropChime();
    this._updateFlightHudDom();
  }

  collectNearestItem(preferredType) {
    const uncollected = this.skyCourse.collectibles.filter(
      (c) => !c.collected && (!preferredType || c.type === preferredType)
    );
    const target = uncollected[0] || this.skyCourse.collectibles.find((c) => !c.collected);
    if (!target) return false;
    target.collected = true;
    target.mesh.userData.collected = true;
    target.mesh.visible = false;
    this._handleItemCollected(target);
    return true;
  }

  _handleItemCollected(item) {
    const f = this.state.flight;
    const type = item.type;
    if (f.collectedCounts[type] !== undefined) {
      f.collectedCounts[type] += 1;
    }
    if (type === 'sky_ring' || type === 'starlight_ring') {
      f.ringsPassed += 1;
    }
    f.score += item.mesh.userData.scoreValue || 100;
    soundSynth.playRingCollectChime();
    this.particleBursts.emitCelebrationBurst(item.mesh.position);
    this._updateFlightHudDom();
  }

  setZone(zoneId) {
    const zId = Number(zoneId) === 3 ? 3 : Number(zoneId) === 2 ? 2 : 1;
    const def = ZONE_DEFINITIONS[zId];
    this.state.flight.zoneId = zId;
    this.state.flight.zoneName = def.name;
    this.state.flight.position.z = zId === 1 ? -20 : zId === 2 ? -620 : -1220;
    this.state.flight.progress = THREE.MathUtils.clamp(-this.state.flight.position.z / 1800, 0, 1);
    this.state.flight.distanceMiles = Math.round(this.state.flight.progress * 2700);
    if (zId === 3) {
      this.setTimeOfDay('night');
    } else if (zId === 2) {
      this.setTimeOfDay('sunset');
    } else {
      this.setTimeOfDay('day');
    }
    this._syncAirplaneTransform();
    this._updateFlightHudDom();
  }

  setTimeOfDay(mode) {
    const valid = mode === 'night' || mode === 'sunset' ? mode : 'day';
    this.state.flight.timeOfDay = valid;

    if (valid === 'day') {
      this.scene.background.set('#3b9eff');
      this.scene.fog.color.set('#bfe9ff');
      this.sunLight.color.set('#fff7e6');
      this.sunLight.intensity = 1.45;
      this.ambientLight.color.set('#d9eeff');
      this.ambientLight.intensity = 0.88;
      this.starfieldMat.opacity = 0.0;
      this.auroraMat.opacity = 0.0;
      this.state.flight.pendantLightsActive = false;
      this.sunnyFox.pendantLight.intensity = 1.2;
      this.lunaBat.pendantLight.intensity = 1.2;
    } else if (valid === 'sunset') {
      this.scene.background.set('#4a2574');
      this.scene.fog.color.set('#ffaf7b');
      this.sunLight.color.set('#ff8c42');
      this.sunLight.intensity = 1.25;
      this.ambientLight.color.set('#ffcdb2');
      this.ambientLight.intensity = 0.68;
      this.starfieldMat.opacity = 0.35;
      this.auroraMat.opacity = 0.15;
      this.state.flight.pendantLightsActive = true;
      this.sunnyFox.pendantLight.intensity = 2.4;
      this.lunaBat.pendantLight.intensity = 2.4;
    } else {
      // 'night' — Fox's glowing lantern & Bat's glowing moon-star illuminate hidden starlight rings!
      this.scene.background.set('#070b1e');
      this.scene.fog.color.set('#1b1438');
      this.sunLight.color.set('#8ab4f8');
      this.sunLight.intensity = 0.38;
      this.ambientLight.color.set('#1a163b');
      this.ambientLight.intensity = 0.32;
      this.starfieldMat.opacity = 1.0;
      this.auroraMat.opacity = 0.85;
      this.state.flight.pendantLightsActive = true;
      this.sunnyFox.pendantLight.intensity = 3.8;
      this.sunnyFox.pendantLight.distance = 45.0;
      this.lunaBat.pendantLight.intensity = 3.6;
      this.lunaBat.pendantLight.distance = 45.0;
    }

    const revealed = this.skyCourse.updatePendantRingIllumination(this.state.flight.pendantLightsActive);
    this.state.flight.revealedStarlightRingsCount = revealed;

    document.querySelectorAll('[data-time-btn]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.timeBtn === valid);
    });
    this.saveConfigToLocalStorage();
    this._updateFlightHudDom();
  }

  completeFlightToBoston() {
    const f = this.state.flight;
    f.active = false;
    f.completed = true;
    f.flightState = 'landed_boston';
    f.zoneId = 3;
    f.zoneName = ZONE_DEFINITIONS[3].name;
    f.progress = 1.0;
    f.distanceMiles = 2700;
    f.position.set ? f.position.set(0, 4.0, -1750) : (f.position = { x: 0, y: 4.0, z: -1750 });
    f.rotation = { pitch: 0, yaw: 0, roll: 0 };
    f.score += 500;
    this.setCharacterAnimation('SunnyFox', 'bounceDance');
    this.setCharacterAnimation('LunaBat', 'bounceDance');
    soundSynth.playRoleSwapDuoChime();

    const banner = document.getElementById('boston-landing-banner');
    if (banner) banner.classList.add('visible');
    this._syncAirplaneTransform();
    this._updateFlightHudDom();
  }

  // ==================== R3 HANGAR & PHOTO BOOTH METHODS ====================

  setPlaneModel(modelId) {
    const valid = ['biplane', 'supersonic_jet', 'origami_glider'].includes(modelId)
      ? modelId
      : 'biplane';
    this.state.hangar.modelId = valid;
    this._rebuildAirplane();
    this.saveConfigToLocalStorage();
    this._updateHangarActiveChips();
    return this.state.hangar.vertexCount;
  }

  setPaintPalette(paletteId) {
    if (!PAINT_PALETTES[paletteId]) return;
    this.state.hangar.paintPaletteId = paletteId;
    this._rebuildAirplane();
    this.saveConfigToLocalStorage();
    this._updateHangarActiveChips();
  }

  setPropellerStyle(styleId) {
    const validStyles = [
      'classic_wood_brass',
      'starlight_crystal_turbine',
      'rainbow_flower_pinwheel',
    ];
    const valid = validStyles.includes(styleId) ? styleId : 'classic_wood_brass';
    this.state.hangar.propellerStyleId = valid;
    this._rebuildAirplane();
    this.saveConfigToLocalStorage();
    this._updateHangarActiveChips();
  }

  setContrailStyle(styleId) {
    const validStyles = [
      'rainbow_ribbon',
      'lantern_fireflies',
      'starlight_moon_dust',
      'heart_bubbles',
    ];
    const valid = validStyles.includes(styleId) ? styleId : 'rainbow_ribbon';
    this.state.hangar.contrailStyleId = valid;
    this.contrailSystem.setStyle(valid);
    this.saveConfigToLocalStorage();
    this._updateHangarActiveChips();
  }

  setWingEmblem(emblemId) {
    const validEmblems = [
      'fox_lantern_crest',
      'bat_moonstar_crest',
      'sf_boston_heart_wings',
      'golden_star_crown',
    ];
    const valid = validEmblems.includes(emblemId) ? emblemId : 'fox_lantern_crest';
    this.state.hangar.wingEmblemId = valid;
    this._rebuildAirplane();
    this.saveConfigToLocalStorage();
    this._updateHangarActiveChips();
  }

  setPhotoBackdrop(backdropId) {
    this.state.photoBooth.backdropId = backdropId;
    if (backdropId === 'boston_zakim_starlight') {
      this.setTimeOfDay('night');
    } else if (backdropId === 'rainbow_cloud_archipelago') {
      this.setTimeOfDay('sunset');
    } else {
      this.setTimeOfDay('day');
    }
    this._updatePhotoBoothChips();
  }

  setPhotoPose(poseId) {
    this.state.photoBooth.poseId = poseId;
    if (poseId === 'wing_walker_cheer') {
      this.setCoPilotMode('wing_walker');
      this.setCharacterAnimation('SunnyFox', 'barrelRollCheer');
      this.setCharacterAnimation('LunaBat', 'barrelRollCheer');
    } else if (poseId === 'lantern_and_moonstar_glow') {
      this.sunnyFox.pendantLight.intensity = 4.2;
      this.lunaBat.pendantLight.intensity = 4.2;
      this.setCharacterAnimation('SunnyFox', 'wingFlapTailWag');
      this.setCharacterAnimation('LunaBat', 'wingFlapTailWag');
    } else if (poseId === 'happy_bounce_duet') {
      this.setCharacterAnimation('SunnyFox', 'bounceDance');
      this.setCharacterAnimation('LunaBat', 'bounceDance');
    } else {
      this.setCoPilotMode('rear_cockpit');
      this.setCharacterAnimation('SunnyFox', 'wave');
      this.setCharacterAnimation('LunaBat', 'wave');
    }
    this._updatePhotoBoothChips();
  }

  setPhotoCaption(text) {
    this.state.photoBooth.captionText = String(text || '').slice(0, 140);
    const input = document.getElementById('photobooth-caption-input');
    if (input && input.value !== this.state.photoBooth.captionText) {
      input.value = this.state.photoBooth.captionText;
    }
  }

  capturePostcard() {
    this._syncAirplaneTransform();
    this.renderer.render(this.scene, this.camera);

    const outCanvas = document.createElement('canvas');
    outCanvas.width = 1280;
    outCanvas.height = 720;
    const ctx = outCanvas.getContext('2d');

    // 1. Draw live 3D WebGL buffer
    ctx.drawImage(this.canvas, 0, 0, 1280, 720);

    // 2. Decorative Postcard Frame & Route Stamp (Strictly Mom in SF <-> Daughter in Boston)
    ctx.strokeStyle = '#ffd966';
    ctx.lineWidth = 14;
    ctx.strokeRect(16, 16, 1248, 688);

    ctx.fillStyle = 'rgba(12, 16, 44, 0.84)';
    ctx.fillRect(28, 608, 1224, 84);

    ctx.fillStyle = '#ffd966';
    ctx.font = 'bold 24px sans-serif';
    ctx.fillText('✈️ SAN FRANCISCO (MOM) ➔ BOSTON (DAUGHTER) SKY POSTCARD', 48, 642);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 20px sans-serif';
    ctx.fillText(this.state.photoBooth.captionText, 48, 675);

    // 3. Stickers overlay
    const stickersText = (this.state.photoBooth.stickerIds || []).join('   ');
    ctx.font = 'bold 22px sans-serif';
    ctx.fillStyle = '#ff9ebb';
    ctx.fillText(stickersText, 48, 58);

    const dataUrl = outCanvas.toDataURL('image/png');
    const postcardRecord = {
      id: `postcard_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
      createdAt: new Date().toISOString(),
      dataUrl,
      width: 1280,
      height: 720,
      captionText: this.state.photoBooth.captionText,
      backdropId: this.state.photoBooth.backdropId,
      poseId: this.state.photoBooth.poseId,
      aircraftConfig: {
        modelId: this.state.hangar.modelId,
        paintPaletteId: this.state.hangar.paintPaletteId,
        propellerStyleId: this.state.hangar.propellerStyleId,
        contrailStyleId: this.state.hangar.contrailStyleId,
        wingEmblemId: this.state.hangar.wingEmblemId,
      },
    };

    this.state.photoBooth.lastCapturedDataUrl = dataUrl;
    this.state.photoBooth.savedPostcards.push(postcardRecord);
    if (this.state.photoBooth.savedPostcards.length > 12) {
      this.state.photoBooth.savedPostcards.shift();
    }

    const previewCanvas = document.getElementById('photo-booth-preview-img');
    if (previewCanvas && previewCanvas.getContext) {
      const pCtx = previewCanvas.getContext('2d');
      pCtx.drawImage(outCanvas, 0, 0, previewCanvas.width, previewCanvas.height);
    }

    try {
      localStorage.setItem(
        POSTCARDS_STORAGE_KEY,
        JSON.stringify(this.state.photoBooth.savedPostcards)
      );
    } catch (e) {
      // Ignore storage quota errors
    }

    this._renderPostcardGalleryDom();
    soundSynth.playFoxLanternChime();
    return postcardRecord;
  }

  saveConfigToLocalStorage() {
    try {
      const payload = {
        modelId: this.state.hangar.modelId,
        paintPaletteId: this.state.hangar.paintPaletteId,
        propellerStyleId: this.state.hangar.propellerStyleId,
        contrailStyleId: this.state.hangar.contrailStyleId,
        wingEmblemId: this.state.hangar.wingEmblemId,
        pilotId: this.state.flight.pilotId,
        coPilotId: this.state.flight.coPilotId,
        coPilotMode: this.state.flight.coPilotMode,
        timeOfDay: this.state.flight.timeOfDay,
      };
      localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(payload));
    } catch (e) {
      // Ignore localStorage security errors in restricted environments
    }
  }

  loadConfigFromLocalStorage() {
    let loaded = false;
    try {
      const rawConfig = localStorage.getItem(CONFIG_STORAGE_KEY);
      if (rawConfig) {
        const parsed = JSON.parse(rawConfig);
        if (parsed.modelId) this.state.hangar.modelId = parsed.modelId;
        if (parsed.paintPaletteId) this.state.hangar.paintPaletteId = parsed.paintPaletteId;
        if (parsed.propellerStyleId) this.state.hangar.propellerStyleId = parsed.propellerStyleId;
        if (parsed.contrailStyleId) {
          this.state.hangar.contrailStyleId = parsed.contrailStyleId;
          this.contrailSystem.setStyle(parsed.contrailStyleId);
        }
        if (parsed.wingEmblemId) this.state.hangar.wingEmblemId = parsed.wingEmblemId;
        if (parsed.pilotId && parsed.coPilotId) {
          this.state.flight.pilotId = parsed.pilotId;
          this.state.flight.coPilotId = parsed.coPilotId;
        }
        if (parsed.coPilotMode) this.state.flight.coPilotMode = parsed.coPilotMode;
        if (parsed.timeOfDay) this.state.flight.timeOfDay = parsed.timeOfDay;
        loaded = true;
      }

      const rawPostcards = localStorage.getItem(POSTCARDS_STORAGE_KEY);
      if (rawPostcards) {
        const cards = JSON.parse(rawPostcards);
        if (Array.isArray(cards)) {
          this.state.photoBooth.savedPostcards = cards;
          if (cards[0] && cards[0].dataUrl) {
            this.state.photoBooth.lastCapturedDataUrl = cards[0].dataUrl;
          }
        }
      }
    } catch (e) {
      loaded = false;
    }
    return loaded;
  }

  // ==================== DETERMINISTIC SIMULATION STEP ====================

  stepSimulation(framesOrDt = 1, maybeDt = 1 / 60) {
    let frames = 1;
    let dt = 1 / 60;
    if (typeof framesOrDt === 'number' && framesOrDt < 1.0 && framesOrDt > 0) {
      frames = 1;
      dt = framesOrDt;
    } else {
      frames = Math.max(1, Math.round(Number(framesOrDt) || 1));
      dt = Number(maybeDt) || 1 / 60;
    }

    for (let step = 0; step < frames; step++) {
      this.state.frameCount += 1;
      this.state.elapsedTime += dt;
      const t = this.state.elapsedTime;

      // Spin airplane propeller
      if (this.airplaneGroup && this.airplaneGroup.propellerGroup) {
        const propSpeed = this.state.flight.boostActive ? 38.0 : 20.0;
        this.airplaneGroup.propellerGroup.rotation.z += propSpeed * dt;
      }

      // Advance Flight Physics when active
      const f = this.state.flight;
      if (f.active && !f.paused && !f.completed) {
        if (f.boostActive) {
          f.boostTimer -= dt;
          if (f.boostTimer <= 0) {
            f.boostActive = false;
            f.boostTimer = 0;
          }
        }

        const baseSpeed = 24.0;
        const currentSpeed = f.boostActive ? baseSpeed * 2.15 : baseSpeed;
        f.speed = currentSpeed;

        f.position.z -= currentSpeed * dt;
        f.position.x = THREE.MathUtils.clamp(f.position.x + f.steerX * 18.0 * dt, -18.0, 18.0);
        f.position.y = THREE.MathUtils.clamp(f.position.y + f.steerY * 14.0 * dt, 3.0, 28.0);

        const targetRoll = -f.steerX * 0.65;
        const targetPitch = f.steerY * 0.42;
        const targetYaw = -f.steerX * 0.25;

        if (f.barrelRollActive) {
          f.barrelRollProgress = Math.min(1.0, f.barrelRollProgress + dt / 0.95);
          f.barrelRollAngle = f.barrelRollProgress * Math.PI * 2.0;
          if (f.barrelRollProgress >= 1.0) {
            f.barrelRollActive = false;
            f.barrelRollProgress = 0;
            f.barrelRollAngle = 0;
          }
        }

        const blend = 1 - Math.exp(-10 * dt);
        f.rotation.pitch = THREE.MathUtils.lerp(f.rotation.pitch, targetPitch, blend);
        f.rotation.yaw = THREE.MathUtils.lerp(f.rotation.yaw, targetYaw, blend);
        f.rotation.roll =
          THREE.MathUtils.lerp(f.rotation.roll, targetRoll, blend) + f.barrelRollAngle;

        f.progress = THREE.MathUtils.clamp(-f.position.z / 1800.0, 0.0, 1.0);
        f.distanceMiles = Math.round(f.progress * 2700);

        // Update Zone transitions
        if (f.position.z <= -1200 && f.zoneId !== 3) {
          f.zoneId = 3;
          f.zoneName = ZONE_DEFINITIONS[3].name;
          f.flightState = 'approaching_boston';
          this.setTimeOfDay('night');
        } else if (f.position.z <= -600 && f.position.z > -1200 && f.zoneId !== 2) {
          f.zoneId = 2;
          f.zoneName = ZONE_DEFINITIONS[2].name;
          this.setTimeOfDay('sunset');
        }

        if (f.progress >= 1.0) {
          this.completeFlightToBoston();
        }
      }

      this._syncAirplaneTransform();

      // Update Flight Chase Camera when in flight_simulator
      if (this.state.activeView === 'flight_simulator') {
        this.camera.position.set(
          f.position.x * 0.55,
          f.position.y + 3.2,
          f.position.z + 11.5
        );
        this.camera.lookAt(f.position.x, f.position.y + 0.6, f.position.z - 15.0);
      } else if (this.controls.enabled) {
        this.controls.update();
      }

      // Update 3D Character Animations
      updateCharacterAnimation(
        this.sunnyFox,
        this.sunnyFox.currentAnimation,
        t,
        dt,
        this.state.flight
      );
      updateCharacterAnimation(
        this.lunaBat,
        this.lunaBat.currentAnimation,
        t,
        dt,
        this.state.flight
      );

      // Update Particle Bursts, Contrails & Collectibles
      this.particleBursts.update(dt);
      this.contrailSystem.update(dt, this.airplaneGroup, f.boostActive);

      const magnetRadius = f.barrelRollActive ? 10.0 : 4.8;
      const planeVec = new THREE.Vector3(f.position.x, f.position.y, f.position.z);
      this.skyCourse.update(dt, t, planeVec, magnetRadius, (item) =>
        this._handleItemCollected(item)
      );
    }

    this._updateFlightHudDom();
    this.renderer.render(this.scene, this.camera);
  }

  // ==================== DOM & EVENT WIRING ====================

  _updateRoleLabelsInDom() {
    const pName =
      this.state.flight.pilotId === 'SunnyFox'
        ? '🦊 SunnyFox (LanternFox)'
        : '🦇 LunaBat (StarBat)';
    const cName =
      this.state.flight.coPilotId === 'SunnyFox'
        ? '🦊 SunnyFox (LanternFox)'
        : '🦇 LunaBat (StarBat)';

    const pEl = document.getElementById('hud-pilot-name');
    const cEl = document.getElementById('hud-copilot-name');
    if (pEl) pEl.textContent = pName;
    if (cEl) cEl.textContent = cName;
  }

  _updateFlightHudDom() {
    const f = this.state.flight;
    const setTxt = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };
    setTxt('hud-score-val', f.score);
    setTxt('hud-rings-val', f.ringsPassed);
    setTxt('hud-miles-val', `${f.distanceMiles} / 2700 mi`);
    setTxt('hud-zone-val', `Zone ${f.zoneId}: ${f.zoneName}`);

    const bar = document.getElementById('hud-route-progress-fill');
    if (bar) bar.style.width = `${Math.round(f.progress * 100)}%`;
  }

  _updateHangarActiveChips() {
    const h = this.state.hangar;
    document.querySelectorAll('[data-plane-model]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.planeModel === h.modelId);
    });
    document.querySelectorAll('[data-paint-palette]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.paintPalette === h.paintPaletteId);
    });
    document.querySelectorAll('[data-propeller-style]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.propellerStyle === h.propellerStyleId);
    });
    document.querySelectorAll('[data-contrail-style]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.contrailStyle === h.contrailStyleId);
    });
    document.querySelectorAll('[data-wing-emblem]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.wingEmblem === h.wingEmblemId);
    });
  }

  _updatePhotoBoothChips() {
    const pb = this.state.photoBooth;
    document.querySelectorAll('[data-backdrop-id]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.backdropId === pb.backdropId);
    });
    document.querySelectorAll('[data-pose-id]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.poseId === pb.poseId);
    });
  }

  _renderPostcardGalleryDom() {
    const downloadLink = document.getElementById('btn-download-postcard');
    if (downloadLink && this.state.photoBooth.lastCapturedDataUrl) {
      downloadLink.href = this.state.photoBooth.lastCapturedDataUrl;
    }
    const strip = document.getElementById('saved-postcards-strip');
    if (strip) {
      strip.innerHTML = '';
      this.state.photoBooth.savedPostcards.slice(-6).forEach((card) => {
        const thumb = document.createElement('div');
        thumb.style.width = '100%';
        thumb.style.aspectRatio = '16 / 9';
        thumb.style.backgroundImage = `url(${card.dataUrl})`;
        thumb.style.backgroundSize = 'cover';
        thumb.style.backgroundPosition = 'center';
        thumb.style.borderRadius = '6px';
        thumb.style.border = '1px solid rgba(255, 217, 102, 0.5)';
        thumb.style.cursor = 'pointer';
        thumb.title = card.captionText;
        thumb.addEventListener('click', () => {
          if (downloadLink) downloadLink.href = card.dataUrl;
        });
        strip.appendChild(thumb);
      });
    }
  }

  _bindDomEvents() {
    window.addEventListener('resize', () => {
      const w = window.innerWidth || 1280;
      const h = window.innerHeight || 720;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });

    // View Tabs
    document.querySelectorAll('.nav-tab-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        if (btn.dataset.view === 'flight_simulator' && !this.state.flight.active) {
          this.startFlight();
        }
        this.setView(btn.dataset.view);
      });
    });

    // Audio Mute Toggle
    const muteBtn = document.getElementById('btn-toggle-audio');
    if (muteBtn) {
      muteBtn.addEventListener('click', () => {
        this.state.audioMuted = soundSynth.setMuted(!this.state.audioMuted);
        muteBtn.textContent = this.state.audioMuted ? '🔇 Audio Muted' : '🔊 Plush Synth On';
      });
    }

    // Studio Animation Chips
    document.querySelectorAll('[data-anim-btn]').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.setCharacterAnimation(btn.dataset.animBtn);
        soundSynth.playPlushSqueak();
      });
    });

    // Accessory Toggles
    document.querySelectorAll('[data-accessory-toggle]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const [charId, accName] = btn.dataset.accessoryToggle.split(':');
        const vis = this.toggleAccessory(charId, accName);
        btn.classList.toggle('active', vis);
        soundSynth.playPlushSqueak();
      });
    });

    // Character Tap Reaction Buttons
    document.querySelectorAll('[data-tap-char]').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.triggerCharacterTapReaction(btn.dataset.tapChar);
      });
    });

    // Swap Roles Buttons
    document.querySelectorAll('[data-action="swap-roles"]').forEach((btn) => {
      btn.addEventListener('click', () => this.swapRoles());
    });

    const coPilotModeBtn = document.getElementById('btn-copilot-mode');
    if (coPilotModeBtn) {
      coPilotModeBtn.addEventListener('click', () => this.toggleCoPilotMode());
    }

    // Flight Stunt & Zone Controls
    const bindClick = (id, fn) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('click', fn);
    };
    bindClick('btn-flight-boost', () => this.triggerBoost());
    bindClick('btn-flight-barrel-roll', () => this.triggerBarrelRoll());
    bindClick('btn-flight-heart-drop', () => this.dropHeartPackage());
    bindClick('btn-flight-restart', () => {
      this.resetFlight();
      this.startFlight();
    });

    document.querySelectorAll('[data-zone-btn]').forEach((btn) => {
      btn.addEventListener('click', () => this.setZone(Number(btn.dataset.zoneBtn)));
    });
    document.querySelectorAll('[data-time-btn]').forEach((btn) => {
      btn.addEventListener('click', () => this.setTimeOfDay(btn.dataset.timeBtn));
    });

    // Hangar Customizer Buttons
    document.querySelectorAll('[data-plane-model]').forEach((btn) => {
      btn.addEventListener('click', () => this.setPlaneModel(btn.dataset.planeModel));
    });
    document.querySelectorAll('[data-paint-palette]').forEach((btn) => {
      btn.addEventListener('click', () => this.setPaintPalette(btn.dataset.paintPalette));
    });
    document.querySelectorAll('[data-propeller-style]').forEach((btn) => {
      btn.addEventListener('click', () => this.setPropellerStyle(btn.dataset.propellerStyle));
    });
    document.querySelectorAll('[data-contrail-style]').forEach((btn) => {
      btn.addEventListener('click', () => this.setContrailStyle(btn.dataset.contrailStyle));
    });
    document.querySelectorAll('[data-wing-emblem]').forEach((btn) => {
      btn.addEventListener('click', () => this.setWingEmblem(btn.dataset.wingEmblem));
    });

    // Photo Booth Controls
    document.querySelectorAll('[data-backdrop-id]').forEach((btn) => {
      btn.addEventListener('click', () => this.setPhotoBackdrop(btn.dataset.backdropId));
    });
    document.querySelectorAll('[data-pose-id]').forEach((btn) => {
      btn.addEventListener('click', () => this.setPhotoPose(btn.dataset.poseId));
    });
    const capInput = document.getElementById('photobooth-caption-input');
    if (capInput) {
      capInput.addEventListener('input', (e) => this.setPhotoCaption(e.target.value));
    }
    bindClick('btn-capture-postcard', () => this.capturePostcard());

    // Raycast Tap-to-React on 3D Canvas
    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    this.canvas.addEventListener('pointerdown', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, this.camera);
      const hits = raycaster.intersectObjects([this.sunnyFox, this.lunaBat], true);
      if (hits.length > 0) {
        let obj = hits[0].object;
        while (obj && obj !== this.sunnyFox && obj !== this.lunaBat) {
          obj = obj.parent;
        }
        if (obj === this.sunnyFox) {
          this.triggerCharacterTapReaction('SunnyFox');
        } else if (obj === this.lunaBat) {
          this.triggerCharacterTapReaction('LunaBat');
        }
      }
    });

    // Virtual Thumbstick for iPad Flight Steering
    const stickBox = document.getElementById('flight-thumbstick');
    const stickKnob = document.getElementById('flight-thumbstick-knob');
    if (stickBox && stickKnob) {
      let draggingStick = false;
      const updateStick = (clientX, clientY) => {
        const rect = stickBox.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const maxR = rect.width * 0.38;
        const dx = THREE.MathUtils.clamp(clientX - cx, -maxR, maxR);
        const dy = THREE.MathUtils.clamp(clientY - cy, -maxR, maxR);
        stickKnob.style.transform = `translate(${dx}px, ${dy}px)`;
        this.setSteering(dx / maxR, -dy / maxR);
      };
      stickBox.addEventListener('pointerdown', (e) => {
        draggingStick = true;
        stickBox.setPointerCapture(e.pointerId);
        updateStick(e.clientX, e.clientY);
      });
      stickBox.addEventListener('pointermove', (e) => {
        if (draggingStick) updateStick(e.clientX, e.clientY);
      });
      const releaseStick = () => {
        draggingStick = false;
        stickKnob.style.transform = 'translate(0px, 0px)';
        this.setSteering(0, 0);
      };
      stickBox.addEventListener('pointerup', releaseStick);
      stickBox.addEventListener('pointercancel', releaseStick);
    }

    // Desktop Keyboard Controls (WASD / Arrows / Space / R / F / C)
    const keys = {};
    const syncKeysToSteer = () => {
      const sx = (keys.ArrowRight || keys.KeyD ? 1 : 0) - (keys.ArrowLeft || keys.KeyA ? 1 : 0);
      const sy = (keys.ArrowUp || keys.KeyW ? 1 : 0) - (keys.ArrowDown || keys.KeyS ? 1 : 0);
      this.setSteering(sx, sy);
    };
    window.addEventListener('keydown', (e) => {
      if (document.activeElement && document.activeElement.tagName === 'INPUT') return;
      keys[e.code] = true;
      syncKeysToSteer();
      if (e.code === 'Space') this.triggerBoost();
      if (e.code === 'KeyR' || e.code === 'KeyE') this.triggerBarrelRoll();
      if (e.code === 'KeyF' || e.code === 'KeyH') this.dropHeartPackage();
      if (e.code === 'KeyC') this.swapRoles();
    });
    window.addEventListener('keyup', (e) => {
      keys[e.code] = false;
      syncKeysToSteer();
    });

    this._updateHangarActiveChips();
    this._updatePhotoBoothChips();
    this._renderPostcardGalleryDom();
  }

  _exposeAppStateContract() {
    const app = this;
    const stateObj = this.state;

    // Bind all required deterministic verification methods onto window.__APP_STATE__
    stateObj.setView = (v) => app.setView(v);
    stateObj.stepSimulation = (framesOrDt, maybeDt) => app.stepSimulation(framesOrDt, maybeDt);
    stateObj.setCharacterAnimation = (charIdOrAnim, maybeAnim) =>
      app.setCharacterAnimation(charIdOrAnim, maybeAnim);
    stateObj.triggerCharacterTapReaction = (charId) => app.triggerCharacterTapReaction(charId);
    stateObj.toggleAccessory = (charId, accName, forceVal) =>
      app.toggleAccessory(charId, accName, forceVal);
    stateObj.swapRoles = () => app.swapRoles();
    stateObj.setCoPilotMode = (mode) => app.setCoPilotMode(mode);
    stateObj.toggleCoPilotMode = () => app.toggleCoPilotMode();
    stateObj.startFlight = () => app.startFlight();
    stateObj.resetFlight = () => app.resetFlight();
    stateObj.setSteering = (sx, sy) => app.setSteering(sx, sy);
    stateObj.triggerBoost = () => app.triggerBoost();
    stateObj.triggerBarrelRoll = () => app.triggerBarrelRoll();
    stateObj.dropHeartPackage = () => app.dropHeartPackage();
    stateObj.collectNearestItem = (type) => app.collectNearestItem(type);
    stateObj.setZone = (z) => app.setZone(z);
    stateObj.setTimeOfDay = (mode) => app.setTimeOfDay(mode);
    stateObj.completeFlightToBoston = () => app.completeFlightToBoston();
    stateObj.setPlaneModel = (m) => app.setPlaneModel(m);
    stateObj.setPaintPalette = (p) => app.setPaintPalette(p);
    stateObj.setPropellerStyle = (s) => app.setPropellerStyle(s);
    stateObj.setContrailStyle = (c) => app.setContrailStyle(c);
    stateObj.setWingEmblem = (e) => app.setWingEmblem(e);
    stateObj.setPhotoBackdrop = (b) => app.setPhotoBackdrop(b);
    stateObj.setPhotoPose = (p) => app.setPhotoPose(p);
    stateObj.setPhotoCaption = (t) => app.setPhotoCaption(t);
    stateObj.capturePostcard = () => app.capturePostcard();
    stateObj.saveConfigToLocalStorage = () => app.saveConfigToLocalStorage();
    stateObj.loadConfigFromLocalStorage = () => app.loadConfigFromLocalStorage();

    window.__APP_STATE__ = stateObj;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  new CrittersAirplaneApp();
});
