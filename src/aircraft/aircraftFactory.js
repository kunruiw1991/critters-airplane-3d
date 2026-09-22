// R3.1 & R3.2 3D Airplane Factory (Critter Cloud Biplane, Starlight Supersonic Jet, Origami Dream Glider)

import { countGroupStats } from '../characters/materials.js';

const THREE = window.THREE;

export const PAINT_PALETTES = {
  sunset_fox_amber: {
    id: 'sunset_fox_amber',
    name: 'Sunset Fox Amber',
    primary: '#e89125',
    secondary: '#f26d6d',
    emissive: '#ffd966',
    accent: '#faefd4',
  },
  midnight_bat_indigo: {
    id: 'midnight_bat_indigo',
    name: 'Midnight Bat Indigo',
    primary: '#3a2278',
    secondary: '#9f78d9',
    emissive: '#ffe57f',
    accent: '#c5a3f0',
  },
  huntrx_golden_neon: {
    id: 'huntrx_golden_neon',
    name: 'HUNTR/X Golden Neon',
    primary: '#1a103c',
    secondary: '#ff2a85',
    emissive: '#ffd700',
    accent: '#00f0ff',
  },
  mint_cloud: {
    id: 'mint_cloud',
    name: 'Mint Cloud',
    primary: '#56d8c0',
    secondary: '#fff8eb',
    emissive: '#ff8da1',
    accent: '#7ec8ff',
  },
};

const _emblemTextureCache = {};

export function createWingEmblemTexture(emblemId = 'fox_lantern_crest') {
  if (_emblemTextureCache[emblemId]) return _emblemTextureCache[emblemId];
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');

  ctx.clearRect(0, 0, 256, 256);

  // Outer badge circle
  ctx.beginPath();
  ctx.arc(128, 128, 110, 0, Math.PI * 2);
  ctx.fillStyle = '#181438';
  ctx.fill();
  ctx.lineWidth = 10;
  ctx.strokeStyle = '#ffd966';
  ctx.stroke();

  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.font = 'bold 88px sans-serif';

  if (emblemId === 'fox_lantern_crest') {
    ctx.fillStyle = '#e89125';
    ctx.fillText('🏮', 128, 122);
  } else if (emblemId === 'bat_moonstar_crest') {
    ctx.fillStyle = '#c5a3f0';
    ctx.fillText('🌙', 128, 122);
  } else if (emblemId === 'sf_boston_heart_wings') {
    ctx.fillStyle = '#ff5c8a';
    ctx.fillText('💖', 128, 122);
  } else {
    ctx.fillStyle = '#ffd700';
    ctx.fillText('⭐', 128, 122);
  }

  ctx.font = 'bold 22px sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('SFO ✈️ BOS', 128, 202);

  const tex = new THREE.CanvasTexture(canvas);
  _emblemTextureCache[emblemId] = tex;
  return tex;
}

export function buildPropellerGroup(styleId = 'classic_wood_brass') {
  const propGroup = new THREE.Group();
  propGroup.name = 'propellerGroup';
  propGroup.position.set(0, 0, 2.48);

  const hubMat = new THREE.MeshStandardMaterial({
    color: styleId === 'starlight_crystal_turbine' ? 0x00f0ff : 0xd49b35,
    roughness: 0.25,
    metalness: 0.85,
  });
  const hub = new THREE.Mesh(new THREE.ConeGeometry(0.26, 0.42, 20), hubMat);
  hub.rotation.x = Math.PI / 2;
  propGroup.add(hub);

  const bladeCount = styleId === 'rainbow_flower_pinwheel' ? 6 : styleId === 'starlight_crystal_turbine' ? 5 : 3;
  const rainbowCols = [0xff6b8b, 0xffa36b, 0xffd966, 0x6be89b, 0x6bc5ff, 0xb88cff];

  for (let i = 0; i < bladeCount; i++) {
    const ang = (i * Math.PI * 2) / bladeCount;
    const bColor =
      styleId === 'rainbow_flower_pinwheel'
        ? rainbowCols[i % rainbowCols.length]
        : styleId === 'starlight_crystal_turbine'
        ? 0x7ec8ff
        : 0x6b3814;

    const bladeMat = new THREE.MeshStandardMaterial({
      color: bColor,
      emissive: styleId === 'starlight_crystal_turbine' ? 0x00a8cc : 0x000000,
      emissiveIntensity: 0.6,
      roughness: 0.35,
      metalness: 0.4,
    });
    const blade = new THREE.Mesh(new THREE.BoxGeometry(0.18, 1.45, 0.045), bladeMat);
    blade.position.set(Math.cos(ang) * 0.65, Math.sin(ang) * 0.65, 0);
    blade.rotation.z = ang + Math.PI / 2;
    blade.rotation.y = 0.25;
    propGroup.add(blade);
  }
  return propGroup;
}

export function createAirplane(config = {}) {
  const modelId = config.modelId || 'biplane';
  const paletteId = config.paintPaletteId || 'sunset_fox_amber';
  const propellerStyleId = config.propellerStyleId || 'classic_wood_brass';
  const wingEmblemId = config.wingEmblemId || 'fox_lantern_crest';
  const coPilotMode = config.coPilotMode || 'rear_cockpit';

  const pal = PAINT_PALETTES[paletteId] || PAINT_PALETTES.sunset_fox_amber;

  const matPrimary = new THREE.MeshStandardMaterial({
    color: new THREE.Color(pal.primary),
    roughness: 0.38,
    metalness: 0.28,
  });
  const matSecondary = new THREE.MeshStandardMaterial({
    color: new THREE.Color(pal.secondary),
    roughness: 0.42,
    metalness: 0.25,
  });
  const matEmissive = new THREE.MeshStandardMaterial({
    color: new THREE.Color(pal.emissive),
    emissive: new THREE.Color(pal.emissive),
    emissiveIntensity: 1.6,
    roughness: 0.2,
    metalness: 0.4,
  });
  const matAccent = new THREE.MeshStandardMaterial({
    color: new THREE.Color(pal.accent),
    roughness: 0.5,
    metalness: 0.15,
  });
  const matDarkRim = new THREE.MeshStandardMaterial({
    color: 0x24193c,
    roughness: 0.5,
    metalness: 0.5,
  });

  const airplaneGroup = new THREE.Group();
  airplaneGroup.name = `Airplane_${modelId}`;
  airplaneGroup.userData = {
    modelId,
    paintPaletteId: paletteId,
    propellerStyleId,
    wingEmblemId,
  };

  // Shared Cockpit Seat Anchors
  const pilotSeatAnchor = new THREE.Group();
  pilotSeatAnchor.name = 'pilotSeatAnchor';
  pilotSeatAnchor.position.set(0, 0.48, 0.78);
  pilotSeatAnchor.scale.setScalar(0.56);
  airplaneGroup.add(pilotSeatAnchor);

  const coPilotSeatAnchor = new THREE.Group();
  coPilotSeatAnchor.name = 'coPilotSeatAnchor';
  if (coPilotMode === 'wing_walker') {
    coPilotSeatAnchor.position.set(1.85, 0.62, -0.05);
  } else {
    coPilotSeatAnchor.position.set(0, 0.56, -0.68);
  }
  coPilotSeatAnchor.scale.setScalar(0.56);
  airplaneGroup.add(coPilotSeatAnchor);

  if (modelId === 'biplane') {
    // 1. Critter Cloud Biplane (>1,500 vertices)
    const fuselage = new THREE.Mesh(new THREE.CylinderGeometry(0.68, 0.52, 4.5, 32, 8), matPrimary);
    fuselage.name = 'fuselageMesh';
    fuselage.rotation.x = Math.PI / 2;
    airplaneGroup.add(fuselage);

    const noseCowling = new THREE.Mesh(new THREE.SphereGeometry(0.68, 28, 20), matSecondary);
    noseCowling.position.set(0, 0, 2.18);
    noseCowling.scale.set(1.0, 1.0, 0.55);
    airplaneGroup.add(noseCowling);

    const tailCone = new THREE.Mesh(new THREE.ConeGeometry(0.52, 1.35, 28), matPrimary);
    tailCone.rotation.x = -Math.PI / 2;
    tailCone.position.set(0, 0.05, -2.85);
    airplaneGroup.add(tailCone);

    // Upper & Lower Wings
    const upperWing = new THREE.Mesh(new THREE.BoxGeometry(7.8, 0.16, 1.55, 12, 2, 4), matSecondary);
    upperWing.name = 'upperWing';
    upperWing.position.set(0, 1.18, 0.25);
    airplaneGroup.add(upperWing);

    const lowerWing = new THREE.Mesh(new THREE.BoxGeometry(7.2, 0.16, 1.48, 12, 2, 4), matPrimary);
    lowerWing.name = 'lowerWing';
    lowerWing.position.set(0, -0.35, 0.15);
    airplaneGroup.add(lowerWing);

    // 4 Interplane Struts
    [-2.4, -0.9, 0.9, 2.4].forEach((sx) => {
      const strut = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.55, 12), matAccent);
      strut.position.set(sx, 0.42, 0.2);
      airplaneGroup.add(strut);
    });

    // Tail Fin & Stabilizers
    const vTail = new THREE.Mesh(new THREE.BoxGeometry(0.14, 1.15, 0.95), matSecondary);
    vTail.position.set(0, 0.62, -2.95);
    airplaneGroup.add(vTail);

    const hTail = new THREE.Mesh(new THREE.BoxGeometry(2.65, 0.12, 0.82), matAccent);
    hTail.position.set(0, 0.22, -2.95);
    airplaneGroup.add(hTail);

    // Landing Gear Wheels
    [-0.95, 0.95].forEach((wx) => {
      const wheelStrut = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.85, 12), matDarkRim);
      wheelStrut.position.set(wx, -0.78, 0.85);
      airplaneGroup.add(wheelStrut);

      const tire = new THREE.Mesh(new THREE.TorusGeometry(0.26, 0.095, 14, 24), matDarkRim);
      tire.rotation.y = Math.PI / 2;
      tire.position.set(wx, -1.18, 0.85);
      airplaneGroup.add(tire);
    });
  } else if (modelId === 'supersonic_jet') {
    // 2. Starlight Supersonic Jet (>1,500 vertices)
    const fuselage = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.68, 4.8, 32, 8), matPrimary);
    fuselage.name = 'fuselageMesh';
    fuselage.rotation.x = Math.PI / 2;
    airplaneGroup.add(fuselage);

    const needleNose = new THREE.Mesh(new THREE.ConeGeometry(0.42, 1.95, 28), matSecondary);
    needleNose.rotation.x = Math.PI / 2;
    needleNose.position.set(0, 0, 3.35);
    airplaneGroup.add(needleNose);

    // Swept Delta Wings
    const deltaWing = new THREE.Mesh(new THREE.BoxGeometry(8.4, 0.14, 2.35, 16, 2, 6), matSecondary);
    deltaWing.name = 'deltaWing';
    deltaWing.position.set(0, -0.05, -0.25);
    airplaneGroup.add(deltaWing);

    // Twin Canted V-Tail Fins
    [-0.75, 0.75].forEach((tx) => {
      const fin = new THREE.Mesh(new THREE.BoxGeometry(0.14, 1.25, 1.15), matPrimary);
      fin.position.set(tx, 0.62, -2.35);
      fin.rotation.z = tx < 0 ? 0.32 : -0.32;
      airplaneGroup.add(fin);
    });

    // Twin Glowing Neon Afterburners
    [-0.38, 0.38].forEach((bx, idx) => {
      const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.30, 0.65, 20), matDarkRim);
      nozzle.rotation.x = Math.PI / 2;
      nozzle.position.set(bx, 0, -2.55);
      airplaneGroup.add(nozzle);

      const plume = new THREE.Mesh(new THREE.ConeGeometry(0.22, 1.25, 20), matEmissive);
      plume.name = idx === 0 ? 'afterburnerLeft' : 'afterburnerRight';
      plume.rotation.x = -Math.PI / 2;
      plume.position.set(bx, 0, -3.35);
      airplaneGroup.add(plume);
    });
  } else {
    // 3. Origami Dream Glider (>1,500 vertices)
    const keelBody = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.62, 5.2, 24, 8), matPrimary);
    keelBody.name = 'fuselageMesh';
    keelBody.rotation.x = Math.PI / 2;
    keelBody.scale.set(0.85, 1.15, 1.0);
    airplaneGroup.add(keelBody);

    // Folded Left & Right Origami Main Wings
    [-1, 1].forEach((side) => {
      const wingPanel = new THREE.Mesh(new THREE.BoxGeometry(3.9, 0.08, 3.2, 14, 2, 8), matSecondary);
      wingPanel.position.set(side * 2.05, 0.22, -0.15);
      wingPanel.rotation.z = side * -0.14;
      airplaneGroup.add(wingPanel);

      const winglet = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.08, 2.6, 8, 2, 6), matAccent);
      winglet.position.set(side * 4.15, 0.48, -0.25);
      winglet.rotation.z = side * 0.65;
      airplaneGroup.add(winglet);

      const runeStrip = new THREE.Mesh(new THREE.BoxGeometry(3.7, 0.04, 0.14), matEmissive);
      runeStrip.position.set(side * 2.05, 0.28, 0.45);
      runeStrip.rotation.z = side * -0.14;
      airplaneGroup.add(runeStrip);
    });
  }

  // Tandem Cockpit Rim Rings
  [0.78, -0.68].forEach((cz) => {
    const rim = new THREE.Mesh(new THREE.TorusGeometry(0.46, 0.065, 12, 24), matDarkRim);
    rim.rotation.x = Math.PI / 2;
    rim.position.set(0, 0.55, cz);
    airplaneGroup.add(rim);
  });

  // Propeller / Nose Spinner Group
  const propellerGroup = buildPropellerGroup(propellerStyleId);
  airplaneGroup.add(propellerGroup);

  // Left & Right Wing Emblems
  const emblemTex = createWingEmblemTexture(wingEmblemId);
  const emblemMat = new THREE.MeshBasicMaterial({
    map: emblemTex,
    transparent: true,
    side: THREE.DoubleSide,
  });
  const emblemY = modelId === 'biplane' ? 1.27 : 0.12;
  const leftWingEmblemMesh = new THREE.Mesh(new THREE.CircleGeometry(0.58, 24), emblemMat);
  leftWingEmblemMesh.name = 'leftWingEmblemMesh';
  leftWingEmblemMesh.rotation.x = -Math.PI / 2;
  leftWingEmblemMesh.position.set(2.45, emblemY, 0.15);
  airplaneGroup.add(leftWingEmblemMesh);

  const rightWingEmblemMesh = new THREE.Mesh(new THREE.CircleGeometry(0.58, 24), emblemMat);
  rightWingEmblemMesh.name = 'rightWingEmblemMesh';
  rightWingEmblemMesh.rotation.x = -Math.PI / 2;
  rightWingEmblemMesh.position.set(-2.45, emblemY, 0.15);
  airplaneGroup.add(rightWingEmblemMesh);

  const stats = countGroupStats(airplaneGroup);
  airplaneGroup.vertexCount = stats.vertexCount;
  airplaneGroup.meshCount = stats.meshCount;
  airplaneGroup.primaryColorHex = pal.primary;
  airplaneGroup.secondaryColorHex = pal.secondary;
  airplaneGroup.pilotSeatAnchor = pilotSeatAnchor;
  airplaneGroup.coPilotSeatAnchor = coPilotSeatAnchor;
  airplaneGroup.propellerGroup = propellerGroup;

  return airplaneGroup;
}
