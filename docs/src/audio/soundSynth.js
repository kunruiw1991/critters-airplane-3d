// Zero-Dependency Web Audio API Plush Sound & Flight Synthesizer

export class SoundSynth {
  constructor() {
    this.ctx = null;
    this.muted = false;
    this.lastTriggeredSound = null;
    this.triggerCount = 0;
  }

  _ensureContext() {
    if (this.muted) return null;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        try {
          this.ctx = new AudioCtx();
        } catch (e) {
          this.ctx = null;
        }
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  setMuted(muted) {
    this.muted = Boolean(muted);
    return this.muted;
  }

  playToneSequence(freqs, duration = 0.16, waveType = 'sine', gainPeak = 0.08) {
    this.triggerCount += 1;
    const ctx = this._ensureContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    freqs.forEach((f, idx) => {
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = waveType;
        osc.frequency.setValueAtTime(f, now + idx * 0.055);
        gain.gain.setValueAtTime(0.0001, now + idx * 0.055);
        gain.gain.exponentialRampToValueAtTime(gainPeak, now + idx * 0.055 + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.055 + duration);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + idx * 0.055);
        osc.stop(now + idx * 0.055 + duration + 0.02);
      } catch (e) {
        // Ignore audio scheduling errors in headless environments
      }
    });
  }

  playFoxLanternChime() {
    this.lastTriggeredSound = 'fox_lantern_chime';
    this.playToneSequence([523.25, 659.25, 783.99, 987.77, 1174.66], 0.28, 'triangle', 0.09);
  }

  playBatMoonStarSparkle() {
    this.lastTriggeredSound = 'bat_moonstar_sparkle';
    this.playToneSequence([440.0, 554.37, 659.25, 880.0, 1108.73], 0.26, 'sine', 0.09);
  }

  playPlushSqueak() {
    this.lastTriggeredSound = 'plush_squeak';
    this.playToneSequence([680, 1120, 860], 0.12, 'sine', 0.08);
  }

  playWingFlapWhoosh() {
    this.lastTriggeredSound = 'wing_flap_whoosh';
    this.playToneSequence([220, 293.66, 349.23], 0.15, 'triangle', 0.06);
  }

  playPropellerAndBoost() {
    this.lastTriggeredSound = 'propeller_boost';
    this.playToneSequence([329.63, 440.0, 659.25, 880.0], 0.22, 'sawtooth', 0.06);
  }

  playRingCollectChime() {
    this.lastTriggeredSound = 'ring_collect';
    this.playToneSequence([587.33, 783.99, 1046.5], 0.20, 'triangle', 0.08);
  }

  playHeartDropChime() {
    this.lastTriggeredSound = 'heart_drop';
    this.playToneSequence([523.25, 659.25, 1046.5], 0.24, 'sine', 0.08);
  }

  playRoleSwapDuoChime() {
    this.lastTriggeredSound = 'role_swap_duo';
    this.playToneSequence([440.0, 554.37, 659.25, 783.99, 1046.5], 0.22, 'triangle', 0.08);
  }
}

export const soundSynth = new SoundSynth();
