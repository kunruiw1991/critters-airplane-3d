// R1.3 Mathematical Procedural 3D Animations for SunnyFox & LunaBat

const THREE = window.THREE;

export const ANIMATION_ALIASES = {
  idle: 'idle',
  wave: 'wave',
  joyful_wave: 'wave',
  wingflaptailwag: 'wingFlapTailWag',
  wing_flap_tail_wag: 'wingFlapTailWag',
  wingFlapTailWag: 'wingFlapTailWag',
  wing_flap: 'wingFlapTailWag',
  bouncedance: 'bounceDance',
  happy_bounce_dance: 'bounceDance',
  bounceDance: 'bounceDance',
  barrelrollcheer: 'barrelRollCheer',
  barrel_roll_cheer: 'barrelRollCheer',
  barrelRollCheer: 'barrelRollCheer',
  cockpitpilotsteer: 'cockpitPilotSteer',
  cockpit_pilot_steer: 'cockpitPilotSteer',
  cockpitPilotSteer: 'cockpitPilotSteer',
};

export function normalizeAnimationName(rawName) {
  if (!rawName || typeof rawName !== 'string') return 'idle';
  const trimmed = rawName.trim();
  if (ANIMATION_ALIASES[trimmed]) return ANIMATION_ALIASES[trimmed];
  const lower = trimmed.toLowerCase();
  return ANIMATION_ALIASES[lower] || trimmed;
}

export function updateCharacterAnimation(charGroup, rawAnimName, t, dt = 1 / 60, flightInputs = {}) {
  if (!charGroup || !charGroup.parts) return;
  const canonical = normalizeAnimationName(rawAnimName || charGroup.currentAnimation);
  const preserveRaw = rawAnimName || charGroup.currentAnimation || 'idle';
  charGroup.currentAnimation = preserveRaw;
  charGroup.userData.animState = preserveRaw;
  charGroup.userData.canonicalAnimState = canonical;
  charGroup.animationTime = t;

  const isFox =
    charGroup.characterId === 'SunnyFox' ||
    charGroup.name === 'SunnyFox' ||
    charGroup.id === 'SunnyFox';
  const phase = isFox ? 0.0 : 0.85;
  const parts = charGroup.parts;
  const head = parts.head;
  const leftEar = parts.leftEar;
  const rightEar = parts.rightEar;
  const torso = parts.torso;
  const pendant = isFox ? parts.lanternPendant : parts.moonStarPendant;
  const leftLeg = parts.leftLeg;
  const rightLeg = parts.rightLeg;

  const steerX = flightInputs.steerX || 0;
  const steerY = flightInputs.steerY || 0;
  const role = charGroup.userData.role || (isFox ? 'pilot' : 'copilot');
  const baseY = flightInputs.baseY ?? 0.0;

  // Reset baseline transforms before applying harmonic overlay
  let rootY = baseY;
  let rootRotZ = 0;
  let headRotX = 0;
  let headRotY = 0;
  let headRotZ = 0;
  let leftEarZ = -0.33;
  let rightEarZ = 0.33;
  let leftLegX = 0;
  let rightLegX = 0;
  let pendantZ = 0.12 * Math.sin(2.4 * t + phase);
  let pendantX = 0.05 * Math.cos(4.2 * t);

  if (canonical === 'idle') {
    rootY = baseY + 0.03 * Math.sin(2.4 * t + phase);
    headRotZ = 0.05 * Math.sin(1.2 * t + phase);
    headRotY = 0.08 * Math.sin(0.9 * t + phase);
    const twitch = Math.pow(Math.max(0, Math.sin(1.8 * t + phase)), 8);
    leftEarZ = -0.34 - 0.24 * twitch * Math.sin(16 * t);
    rightEarZ = 0.34 + 0.18 * Math.pow(Math.max(0, Math.sin(1.4 * t + 1.5)), 8);

    if (isFox && parts.tail) {
      parts.tail.rotation.y = 0.42 + 0.22 * Math.sin(2.0 * t);
      parts.tail.rotation.z = 0.08 * Math.cos(2.0 * t);
      parts.leftArm.rotation.z = -0.48 - 0.06 * Math.sin(2.4 * t);
      parts.rightArm.rotation.z = 0.48 + 0.06 * Math.sin(2.4 * t);
      parts.leftArm.rotation.x = 0;
      parts.rightArm.rotation.x = 0;
    } else if (!isFox && parts.leftWingArm) {
      parts.leftWingArm.rotation.z = 0.12 * Math.sin(2.4 * t);
      parts.rightWingArm.rotation.z = -0.12 * Math.sin(2.4 * t);
      const lSpan = parts.leftWingArm.getObjectByName('outerWingSpan');
      const rSpan = parts.rightWingArm.getObjectByName('outerWingSpan');
      if (lSpan) lSpan.rotation.z = 0.08 * Math.sin(2.4 * t - 0.5);
      if (rSpan) rSpan.rotation.z = -0.08 * Math.sin(2.4 * t - 0.5);
    }
  } else if (canonical === 'wave') {
    rootY = baseY + Math.abs(Math.sin(4.8 * t)) * 0.07;
    headRotZ = -0.14 + 0.07 * Math.sin(4.8 * t);
    headRotX = -0.08 + 0.05 * Math.sin(9.6 * t);

    if (isFox) {
      parts.rightArm.rotation.z = 2.35 + 0.42 * Math.sin(9.6 * t);
      parts.rightArm.rotation.x = -0.35 + 0.16 * Math.cos(9.6 * t);
      parts.leftArm.rotation.z = -0.55 - 0.08 * Math.sin(4.8 * t);
      parts.tail.rotation.y = 0.42 + 0.35 * Math.sin(6.0 * t);
    } else {
      parts.rightWingArm.rotation.z = 0.88 + 0.45 * Math.sin(9.2 * t);
      parts.leftWingArm.rotation.z = 0.15 * Math.sin(4.6 * t);
      const rSpan = parts.rightWingArm.getObjectByName('outerWingSpan');
      if (rSpan) rSpan.rotation.z = 0.38 * Math.sin(9.2 * t - 0.4);
    }
  } else if (canonical === 'wingFlapTailWag') {
    if (isFox) {
      rootY = baseY + 0.05 * Math.abs(Math.sin(11.0 * t));
      parts.tail.rotation.y = 0.42 + 0.72 * Math.sin(11.5 * t);
      parts.tail.rotation.z = 0.28 * Math.cos(11.5 * t);
      torso.rotation.y = -0.16 * Math.sin(11.5 * t);
      pendantZ = 0.38 * Math.sin(11.5 * t);
      parts.leftArm.rotation.z = -0.75 - 0.22 * Math.sin(11.5 * t);
      parts.rightArm.rotation.z = 0.75 + 0.22 * Math.sin(11.5 * t);
    } else {
      rootY = baseY + 0.18 + 0.14 * Math.sin(10.5 * t - 0.4);
      parts.leftWingArm.rotation.z = 0.62 * Math.sin(10.5 * t);
      parts.leftWingArm.rotation.y = 0.26 * Math.cos(10.5 * t);
      parts.rightWingArm.rotation.z = -0.62 * Math.sin(10.5 * t);
      parts.rightWingArm.rotation.y = -0.26 * Math.cos(10.5 * t);
      const lSpan = parts.leftWingArm.getObjectByName('outerWingSpan');
      const rSpan = parts.rightWingArm.getObjectByName('outerWingSpan');
      if (lSpan) lSpan.rotation.z = 0.48 * Math.sin(10.5 * t - 0.6);
      if (rSpan) rSpan.rotation.z = -0.48 * Math.sin(10.5 * t - 0.6);
    }
  } else if (canonical === 'bounceDance') {
    const beat = 6.8 * t;
    rootY = baseY + 0.24 * Math.abs(Math.sin(beat));
    rootRotZ = 0.16 * Math.sin(beat);
    headRotZ = -0.22 * Math.sin(beat);
    leftLegX = 0.48 * Math.max(0, Math.sin(beat));
    rightLegX = 0.48 * Math.max(0, -Math.sin(beat));

    if (isFox) {
      parts.leftArm.rotation.x = -0.85 * Math.sin(beat);
      parts.rightArm.rotation.x = 0.85 * Math.sin(beat);
      parts.tail.rotation.y = 0.42 + 0.45 * Math.cos(beat);
    } else {
      parts.leftWingArm.rotation.z = 0.45 + 0.35 * Math.sin(beat);
      parts.rightWingArm.rotation.z = -0.45 + 0.35 * Math.sin(beat);
    }
  } else if (canonical === 'barrelRollCheer') {
    const T = 1.8;
    const u = ((t % T) + T) % T / T;
    if (u <= 0.7) {
      const s = u / 0.7;
      const smooth = s * s * s * (s * (s * 6 - 15) + 10);
      rootRotZ = Math.PI * 2 * smooth;
      rootY = baseY + 0.42 * Math.sin(Math.PI * s);
    } else {
      rootRotZ = 0;
      rootY = baseY + 0.12 * Math.sin(12 * t);
    }
    if (isFox) {
      parts.leftArm.rotation.z = -2.35;
      parts.rightArm.rotation.z = 2.35;
    } else {
      parts.leftWingArm.rotation.z = 0.85;
      parts.rightWingArm.rotation.z = -0.85;
    }
  } else if (canonical === 'cockpitPilotSteer') {
    leftLegX = -1.32;
    rightLegX = -1.32;
    headRotY = -0.34 * steerX;
    headRotX = 0.22 * steerY;
    headRotZ = -0.24 * steerX + 0.04 * Math.sin(3.2 * t);

    if (role === 'pilot') {
      if (isFox) {
        parts.leftArm.rotation.x = -1.15 + 0.28 * steerX;
        parts.rightArm.rotation.x = -1.15 - 0.28 * steerX;
        parts.leftArm.rotation.z = -0.32;
        parts.rightArm.rotation.z = 0.32;
      } else {
        parts.leftWingArm.rotation.y = 0.45 + 0.25 * steerX;
        parts.rightWingArm.rotation.y = -0.45 + 0.25 * steerX;
        parts.leftWingArm.rotation.z = 0.22 * Math.sin(4.0 * t);
        parts.rightWingArm.rotation.z = -0.22 * Math.sin(4.0 * t);
      }
    } else {
      // Co-pilot waving & cheering
      if (isFox) {
        parts.rightArm.rotation.z = 2.15 + 0.38 * Math.sin(8.5 * t);
        parts.leftArm.rotation.z = -0.5;
      } else {
        parts.rightWingArm.rotation.z = 0.78 + 0.40 * Math.sin(8.5 * t);
        parts.leftWingArm.rotation.z = -0.38 * Math.sin(8.5 * t);
      }
    }
  }

  // Apply computed joint poses
  charGroup.position.y = rootY;
  charGroup.rotation.z = rootRotZ;

  if (head) {
    head.rotation.set(headRotX, headRotY, headRotZ);
  }
  if (leftEar) leftEar.rotation.z = leftEarZ;
  if (rightEar) rightEar.rotation.z = rightEarZ;
  if (leftLeg) leftLeg.rotation.x = leftLegX;
  if (rightLeg) rightLeg.rotation.x = rightLegX;
  if (pendant) {
    pendant.rotation.z = pendantZ;
    pendant.rotation.x = pendantX;
  }

  // Scarf flutter in wind
  if (parts.pilotGear) {
    const scarf = parts.pilotGear.getObjectByName('pilotScarf');
    if (scarf && scarf.visible) {
      const tL = scarf.getObjectByName('scarfTailLeft');
      const tR = scarf.getObjectByName('scarfTailRight');
      if (tL) tL.rotation.x = 0.25 * Math.sin(14.0 * t);
      if (tR) tR.rotation.x = 0.25 * Math.cos(14.0 * t + 1.0);
    }
  }
}
