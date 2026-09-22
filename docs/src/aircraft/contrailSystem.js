// R3.2 Sky-Writing Contrail Particle System (Rainbow Ribbon, Lantern Fireflies, Starlight Moon Dust, Heart Bubbles)

const THREE = window.THREE;

export const CONTRAIL_PALETTES = {
  rainbow_ribbon: ['#ff6b8b', '#ffa36b', '#ffd966', '#6be89b', '#6bc5ff', '#b88cff'],
  lantern_fireflies: ['#ffd966', '#ff9e2c', '#fff4b8', '#f26d6d'],
  starlight_moon_dust: ['#ffe57f', '#c5a3f0', '#9f78d9', '#8ab4f8'],
  heart_bubbles: ['#ff5c8a', '#ff9ebb', '#fff0f5', '#ffd966'],
};

export class ContrailSystem {
  constructor(styleId = 'rainbow_ribbon') {
    this.styleId = styleId;
    this.group = new THREE.Group();
    this.group.name = 'contrailSystem';
    this.particles = [];
    this.maxParticles = 96;
    this.spawnTimer = 0;

    const geom = new THREE.SphereGeometry(0.11, 8, 8);
    for (let i = 0; i < this.maxParticles; i++) {
      const mat = new THREE.MeshBasicMaterial({
        color: 0xffd966,
        transparent: true,
        opacity: 0.0,
      });
      const mesh = new THREE.Mesh(geom, mat);
      mesh.visible = false;
      this.group.add(mesh);
      this.particles.push({
        mesh,
        active: false,
        age: 0,
        maxAge: 1.1,
        vel: new THREE.Vector3(),
      });
    }
    this.cursor = 0;
    this.setStyle(styleId);
  }

  setStyle(styleId) {
    this.styleId = CONTRAIL_PALETTES[styleId] ? styleId : 'rainbow_ribbon';
    const colors = CONTRAIL_PALETTES[this.styleId];
    this.particles.forEach((p, idx) => {
      p.mesh.material.color.set(colors[idx % colors.length]);
    });
  }

  spawnPair(airplaneGroup, boostActive = false) {
    if (!airplaneGroup) return;
    const colors = CONTRAIL_PALETTES[this.styleId] || CONTRAIL_PALETTES.rainbow_ribbon;
    [-3.4, 3.4].forEach((wingX) => {
      const p = this.particles[this.cursor];
      this.cursor = (this.cursor + 1) % this.maxParticles;
      const worldPos = new THREE.Vector3(wingX, 0.1, -1.6).applyMatrix4(airplaneGroup.matrixWorld);
      p.mesh.position.copy(worldPos);
      p.mesh.material.color.set(colors[this.cursor % colors.length]);
      p.mesh.visible = true;
      p.mesh.material.opacity = 0.9;
      p.mesh.scale.setScalar(boostActive ? 1.55 : 1.0);
      p.active = true;
      p.age = 0;
      p.maxAge = boostActive ? 1.35 : 0.95;
      p.vel.set((Math.random() - 0.5) * 0.8, (Math.random() - 0.5) * 0.8, 6.0);
    });
  }

  update(dt, airplaneGroup, boostActive = false) {
    this.spawnTimer += dt;
    const interval = boostActive ? 0.018 : 0.035;
    if (this.spawnTimer >= interval) {
      this.spawnTimer = 0;
      this.spawnPair(airplaneGroup, boostActive);
    }

    for (let i = 0; i < this.maxParticles; i++) {
      const p = this.particles[i];
      if (!p.active) continue;
      p.age += dt;
      if (p.age >= p.maxAge) {
        p.active = false;
        p.mesh.visible = false;
        continue;
      }
      p.mesh.position.addScaledVector(p.vel, dt);
      const ratio = 1.0 - p.age / p.maxAge;
      p.mesh.material.opacity = ratio * 0.85;
      p.mesh.scale.setScalar(0.35 + ratio * (boostActive ? 1.3 : 0.9));
    }
  }
}
