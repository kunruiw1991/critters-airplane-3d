// R1.3 Dual 3D Particle Burst Emitters (Fox Warm Lantern Fireflies & Bat Starry Lavender Moon-Dust)

const THREE = window.THREE;

export class ParticleBurstSystem {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'CharacterParticleBursts';
    this.scene.add(this.group);
    this.particles = [];
    this.totalEmitted = 0;

    this.sphereGeom = new THREE.SphereGeometry(0.042, 8, 8);
    this.starGeom = new THREE.OctahedronGeometry(0.052, 0);
  }

  emitBurst(originVec, paletteHexes, isStar = false, count = 26) {
    for (let i = 0; i < count; i++) {
      const hex = paletteHexes[i % paletteHexes.length];
      const mat = new THREE.MeshBasicMaterial({
        color: new THREE.Color(hex),
        transparent: true,
        opacity: 1.0,
      });
      const mesh = new THREE.Mesh(isStar ? this.starGeom : this.sphereGeom, mat);
      mesh.position.copy(originVec);
      const theta = (i / count) * Math.PI * 2 + Math.random() * 0.4;
      const speed = 0.8 + Math.random() * 1.6;
      const vel = new THREE.Vector3(
        Math.cos(theta) * speed,
        0.5 + Math.random() * 1.4,
        Math.sin(theta) * speed
      );
      this.group.add(mesh);
      this.particles.push({
        mesh,
        vel,
        age: 0,
        maxAge: 0.9 + Math.random() * 0.6,
      });
      this.totalEmitted += 1;
    }
  }

  emitFoxFireflies(originVec) {
    this.emitBurst(originVec, ['#ffd966', '#ff9e2c', '#fff4b8', '#f26d6d'], false, 28);
  }

  emitBatMoonDust(originVec) {
    this.emitBurst(originVec, ['#ffe57f', '#c5a3f0', '#9f78d9', '#8ab4f8'], true, 28);
  }

  emitCelebrationBurst(originVec) {
    this.emitBurst(originVec, ['#ffd966', '#ff5c8a', '#c5a3f0', '#56d8c0', '#ffe57f'], true, 32);
  }

  update(dt) {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.age += dt;
      if (p.age >= p.maxAge) {
        this.group.remove(p.mesh);
        p.mesh.material.dispose();
        this.particles.splice(i, 1);
        continue;
      }
      p.mesh.position.addScaledVector(p.vel, dt);
      p.mesh.rotation.y += 4.0 * dt;
      p.mesh.rotation.x += 3.0 * dt;
      const lifeRatio = 1.0 - p.age / p.maxAge;
      p.mesh.scale.setScalar(0.4 + 0.8 * lifeRatio);
      p.mesh.material.opacity = lifeRatio;
    }
  }
}
