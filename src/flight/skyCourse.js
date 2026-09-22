// R2.3 & R2.4 3-Zone Sky Course (San Francisco Golden Gate Bridge -> Rainbow Cloud Archipelago -> Boston Zakim Bridge & Skyline)

const THREE = window.THREE;

export const ZONE_DEFINITIONS = {
  1: {
    id: 1,
    name: 'Golden Gate Sunrise Takeoff',
    zStart: 0,
    zEnd: -600,
    defaultTimeOfDay: 'day',
  },
  2: {
    id: 2,
    name: 'Rainbow Cloud Archipelago & Paper-Airplane Wind Tunnels',
    zStart: -600,
    zEnd: -1200,
    defaultTimeOfDay: 'sunset',
  },
  3: {
    id: 3,
    name: 'Starry Night Aurora Approach into Boston',
    zStart: -1200,
    zEnd: -1800,
    defaultTimeOfDay: 'night',
  },
};

export class SkyCourseManager {
  constructor(scene) {
    this.scene = scene;
    this.courseGroup = new THREE.Group();
    this.courseGroup.name = 'SkyCourseWorld';
    this.scene.add(this.courseGroup);

    this.collectibles = [];
    this.droppedPackages = [];
    this.hiddenStarlightRings = [];

    this._buildLandmarks();
    this._buildCollectibles();
  }

  _buildLandmarks() {
    // 1. Zone 1: San Francisco Golden Gate Bridge (International Orange #c0362c)
    const sfGroup = new THREE.Group();
    sfGroup.name = 'SanFranciscoGoldenGateBridge';
    sfGroup.position.set(0, 0, -50);

    const ggOrange = new THREE.MeshStandardMaterial({ color: 0xc0362c, roughness: 0.45, metalness: 0.35 });
    const deckMat = new THREE.MeshStandardMaterial({ color: 0x383c4a, roughness: 0.7 });

    // Twin International Orange Towers
    [-16, 16].forEach((tx) => {
      const tower = new THREE.Mesh(new THREE.BoxGeometry(2.6, 28, 2.2), ggOrange);
      tower.position.set(tx, 10, 0);
      sfGroup.add(tower);

      const crossBeam1 = new THREE.Mesh(new THREE.BoxGeometry(5.5, 1.4, 1.8), ggOrange);
      crossBeam1.position.set(tx, 20, 0);
      sfGroup.add(crossBeam1);
    });

    // Bridge Roadway Deck & Main Span Arch
    const bridgeDeck = new THREE.Mesh(new THREE.BoxGeometry(46, 1.1, 5.2), deckMat);
    bridgeDeck.position.set(0, 4.5, 0);
    sfGroup.add(bridgeDeck);

    const topSpan = new THREE.Mesh(new THREE.BoxGeometry(35, 1.5, 2.0), ggOrange);
    topSpan.position.set(0, 23.5, 0);
    sfGroup.add(topSpan);

    this.courseGroup.add(sfGroup);

    // 2. Zone 2: Rainbow Cloud Islands & Giant Rainbow Archways
    const zone2Group = new THREE.Group();
    zone2Group.name = 'RainbowCloudArchipelago';
    const cloudMat = new THREE.MeshStandardMaterial({ color: 0xfff8f2, roughness: 0.9 });
    const rainbowColors = [0xff5c8a, 0xff9e2c, 0xffd966, 0x56d8c0, 0x6bc5ff, 0xb88cff];

    for (let i = 0; i < 14; i++) {
      const cz = -120 - i * 115;
      const cx = (i % 2 === 0 ? -1 : 1) * (10 + (i % 3) * 4);
      const cy = 6 + (i % 4) * 3.5;

      const cloudCluster = new THREE.Group();
      cloudCluster.position.set(cx, cy, cz);
      for (let c = 0; c < 3; c++) {
        const puff = new THREE.Mesh(new THREE.SphereGeometry(2.4 - c * 0.4, 14, 12), cloudMat);
        puff.position.set((c - 1) * 1.9, (c % 2) * 0.5, 0);
        puff.scale.set(1.3, 0.75, 1.0);
        cloudCluster.add(puff);
      }
      zone2Group.add(cloudCluster);
    }

    [-700, -950, -1150].forEach((rz) => {
      const archGrp = new THREE.Group();
      archGrp.position.set(0, 8, rz);
      rainbowColors.forEach((col, idx) => {
        const band = new THREE.Mesh(
          new THREE.TorusGeometry(14 - idx * 0.65, 0.32, 10, 36, Math.PI),
          new THREE.MeshBasicMaterial({ color: col })
        );
        archGrp.add(band);
      });
      zone2Group.add(archGrp);
    });
    this.courseGroup.add(zone2Group);

    // 3. Zone 3: Boston Leonard P. Zakim Bridge & Boston Skyline + Starlight Runway
    const bostonGroup = new THREE.Group();
    bostonGroup.name = 'BostonZakimBridgeAndSkyline';
    bostonGroup.position.set(0, 0, -1760);

    const zakimWhite = new THREE.MeshStandardMaterial({
      color: 0xf4f6fc,
      emissive: 0x283566,
      emissiveIntensity: 0.5,
      roughness: 0.3,
    });
    [-14, 14].forEach((zx) => {
      const obelisk = new THREE.Mesh(new THREE.ConeGeometry(2.2, 26, 4), zakimWhite);
      obelisk.position.set(zx, 13, 0);
      bostonGroup.add(obelisk);
    });

    // Prudential Tower & Custom House Clock Tower silhouettes
    const towerMat = new THREE.MeshStandardMaterial({
      color: 0x1e2952,
      emissive: 0x3a2278,
      emissiveIntensity: 0.6,
      roughness: 0.35,
    });
    [-24, -19, 19, 25].forEach((bx, idx) => {
      const h = 20 + (idx % 2) * 8;
      const bldg = new THREE.Mesh(new THREE.BoxGeometry(4.2, h, 4.2), towerMat);
      bldg.position.set(bx, h / 2, -18);
      bostonGroup.add(bldg);
    });

    // Boston Starlight Welcome Runway
    const runway = new THREE.Mesh(
      new THREE.BoxGeometry(18, 0.5, 65),
      new THREE.MeshStandardMaterial({
        color: 0x1a1e3a,
        emissive: 0xffd966,
        emissiveIntensity: 0.35,
      })
    );
    runway.name = 'BostonWelcomeRunway';
    runway.position.set(0, 2.2, 15);
    bostonGroup.add(runway);

    this.courseGroup.add(bostonGroup);
  }

  _buildCollectibles() {
    this.collectibles.forEach((c) => this.courseGroup.remove(c.mesh));
    this.collectibles = [];
    this.hiddenStarlightRings = [];

    const typesCycle = [
      'sky_ring',
      'golden_lantern',
      'crescent_moon_star',
      'music_note_booster',
      'mom_heart_care_package',
      'paper_airplane_squadron',
      'starlight_ring',
    ];

    for (let i = 0; i < 42; i++) {
      const type = typesCycle[i % typesCycle.length];
      const z = -45 - i * 40;
      const x = Math.sin(i * 0.85) * 6.5;
      const y = 11.5 + Math.cos(i * 0.7) * 3.2;
      const isHiddenRing = type === 'starlight_ring' || z <= -1200;

      let mesh;
      if (type === 'sky_ring' || type === 'starlight_ring') {
        const ringMat = new THREE.MeshStandardMaterial({
          color: type === 'starlight_ring' ? 0xffe57f : 0xff9e2c,
          emissive: type === 'starlight_ring' ? 0xffe57f : 0xffd966,
          emissiveIntensity: isHiddenRing ? 0.35 : 1.6,
          transparent: true,
          opacity: isHiddenRing ? 0.35 : 0.95,
          roughness: 0.2,
        });
        mesh = new THREE.Mesh(new THREE.TorusGeometry(3.2, 0.24, 12, 32), ringMat);
      } else if (type === 'golden_lantern') {
        mesh = new THREE.Mesh(
          new THREE.CylinderGeometry(0.55, 0.65, 1.2, 14),
          new THREE.MeshStandardMaterial({
            color: 0xffd966,
            emissive: 0xffb732,
            emissiveIntensity: 2.0,
          })
        );
      } else if (type === 'crescent_moon_star') {
        mesh = new THREE.Mesh(
          new THREE.TorusGeometry(0.75, 0.22, 12, 24, Math.PI * 1.4),
          new THREE.MeshStandardMaterial({
            color: 0xffe57f,
            emissive: 0xc5a3f0,
            emissiveIntensity: 2.0,
          })
        );
      } else if (type === 'music_note_booster') {
        mesh = new THREE.Mesh(
          new THREE.OctahedronGeometry(0.78, 1),
          new THREE.MeshStandardMaterial({
            color: 0x00f0ff,
            emissive: 0x00f0ff,
            emissiveIntensity: 1.8,
          })
        );
      } else if (type === 'mom_heart_care_package') {
        mesh = new THREE.Mesh(
          new THREE.BoxGeometry(1.05, 1.05, 1.05),
          new THREE.MeshStandardMaterial({
            color: 0xff5c8a,
            emissive: 0xff5c8a,
            emissiveIntensity: 1.5,
          })
        );
      } else {
        // paper_airplane_squadron
        mesh = new THREE.Mesh(
          new THREE.ConeGeometry(0.85, 1.9, 4),
          new THREE.MeshStandardMaterial({
            color: 0xfaf5ea,
            emissive: 0xffd966,
            emissiveIntensity: 1.1,
          })
        );
        mesh.rotation.x = -Math.PI / 2;
      }

      mesh.position.set(x, y, z);
      mesh.name = `Collectible_${type}_${i}`;
      mesh.userData = {
        id: `item_${i}`,
        type,
        collected: false,
        isHiddenStarlightRing: Boolean(type === 'starlight_ring' || z <= -1200),
        revealedByPendantLight: false,
        scoreValue:
          type === 'starlight_ring'
            ? 300
            : type === 'mom_heart_care_package'
            ? 200
            : type === 'music_note_booster' || type === 'sky_ring'
            ? 150
            : 100,
      };

      this.courseGroup.add(mesh);
      const itemObj = {
        id: `item_${i}`,
        type,
        mesh,
        collected: false,
      };
      this.collectibles.push(itemObj);
      if (mesh.userData.isHiddenStarlightRing) {
        this.hiddenStarlightRings.push(itemObj);
      }
    }
  }

  resetCollectibles() {
    this.collectibles.forEach((item) => {
      item.collected = false;
      item.mesh.visible = true;
      item.mesh.userData.collected = false;
    });
  }

  updatePendantRingIllumination(pendantLightsActive) {
    let revealedCount = 0;
    this.hiddenStarlightRings.forEach((item) => {
      if (pendantLightsActive) {
        item.mesh.userData.revealedByPendantLight = true;
        if (item.mesh.material) {
          item.mesh.material.opacity = 1.0;
          item.mesh.material.emissiveIntensity = 2.6;
        }
        revealedCount += 1;
      } else {
        item.mesh.userData.revealedByPendantLight = false;
        if (item.mesh.material) {
          item.mesh.material.opacity = 0.38;
          item.mesh.material.emissiveIntensity = 0.4;
        }
      }
    });
    return revealedCount;
  }

  spawnHeartCarePackageDrop(originPos) {
    const pkgGroup = new THREE.Group();
    pkgGroup.name = 'HeartParachutePackage';
    pkgGroup.position.copy(originPos);

    const box = new THREE.Mesh(
      new THREE.BoxGeometry(0.65, 0.65, 0.65),
      new THREE.MeshStandardMaterial({
        color: 0xff5c8a,
        emissive: 0xff5c8a,
        emissiveIntensity: 0.9,
      })
    );
    pkgGroup.add(box);

    const chute = new THREE.Mesh(
      new THREE.SphereGeometry(0.85, 16, 12, 0, Math.PI * 2, 0, Math.PI / 2),
      new THREE.MeshStandardMaterial({
        color: 0xfff5f8,
        side: THREE.DoubleSide,
      })
    );
    chute.position.set(0, 0.85, 0);
    pkgGroup.add(chute);

    this.courseGroup.add(pkgGroup);
    this.droppedPackages.push({
      group: pkgGroup,
      age: 0,
    });
    return pkgGroup;
  }

  update(dt, t, airplanePos, magnetRadius, onCollectCallback) {
    // Rotate & bob collectibles + check proximity collection
    for (let i = 0; i < this.collectibles.length; i++) {
      const item = this.collectibles[i];
      if (item.collected) continue;
      item.mesh.rotation.y += 1.8 * dt;

      if (airplanePos) {
        const dist = item.mesh.position.distanceTo(airplanePos);
        if (dist <= magnetRadius) {
          item.collected = true;
          item.mesh.userData.collected = true;
          item.mesh.visible = false;
          if (onCollectCallback) onCollectCallback(item);
        }
      }
    }

    // Update falling heart care packages
    for (let i = this.droppedPackages.length - 1; i >= 0; i--) {
      const pkg = this.droppedPackages[i];
      pkg.age += dt;
      pkg.group.position.y -= 3.2 * dt;
      pkg.group.rotation.z = 0.22 * Math.sin(pkg.age * 5.0);
      if (pkg.age > 5.0) {
        this.courseGroup.remove(pkg.group);
        this.droppedPackages.splice(i, 1);
      }
    }
  }
}
