/* =========================================================
   audio.js — WebAudio 로 만드는 배경음과 효과음
   외부 음원 파일 없이 코드로만 합성합니다.
   ========================================================= */
(function (global) {
  'use strict';

  var ctx = null;
  var master = null;
  var bgmBus = null;
  var sfxBus = null;
  var delay = null;
  var filter = null;
  var timer = null;
  var moodName = 'silent';
  var enabled = true;
  var bgmOn = true;
  var started = false;
  var nextTime = 0;
  var step = 0;
  var current = null;

  /* 음계: 각 무드의 코드 진행과 멜로디 패턴 (판타지 무드 · 9th/sus 화음) */
  var MOODS = {
    title: {
      bpm: 64, wave: 'sine', pad: 0.052, pluck: 0.05, bass: 0.045, shimmer: 0.5,
      chords: [[50, 57, 62, 66], [45, 52, 57, 62], [47, 54, 59, 64], [43, 50, 55, 59]],
      bells: [[74, 81, 83, 81], [71, 78, 81, 78], [73, 80, 83, 80], [74, 78, 81, 79]],
      every: 8
    },
    day: {
      bpm: 88, wave: 'triangle', pad: 0.04, pluck: 0.052, bass: 0.038, shimmer: 0.22,
      chords: [[53, 60, 65, 69], [50, 57, 62, 66], [55, 62, 67, 71], [48, 55, 60, 64]],
      bells: [[77, 81, 84, 86], [74, 78, 81, 84], [79, 83, 86, 88], [72, 76, 79, 81]],
      every: 8
    },
    night: {
      bpm: 58, wave: 'sine', pad: 0.05, pluck: 0.04, bass: 0.05, shimmer: 0.7,
      chords: [[45, 52, 57, 62], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 55]],
      bells: [[69, 76, 81, 72], [65, 72, 76, 69], [67, 74, 79, 71], [64, 71, 74, 67]],
      every: 10
    },
    warm: {
      bpm: 76, wave: 'triangle', pad: 0.046, pluck: 0.055, bass: 0.044, shimmer: 0.35,
      chords: [[50, 57, 62, 65], [48, 55, 60, 64], [45, 52, 57, 60], [47, 54, 59, 64]],
      bells: [[74, 77, 81, 84], [72, 76, 79, 84], [69, 72, 76, 81], [71, 74, 78, 83]],
      every: 8
    },
    tense: {
      bpm: 100, wave: 'sawtooth', pad: 0.026, pluck: 0.026, bass: 0.048, shimmer: 0,
      chords: [[38, 45, 50, 51], [38, 44, 51, 52], [36, 43, 48, 49], [38, 45, 50, 51]],
      bells: [[62, 63], [63, 64], [60, 61], [62, 63]],
      every: 16
    }
  };

  function freq(m) { return 440 * Math.pow(2, (m - 69) / 12); }

  function init() {
    if (ctx) return ctx;
    var C = global.AudioContext || global.webkitAudioContext;
    if (!C) return null;
    ctx = new C();

    master = ctx.createGain();
    master.gain.value = 0.9;
    master.connect(ctx.destination);

    filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 2600;
    filter.Q.value = 0.55;
    filter.connect(master);

    delay = ctx.createDelay(1.4);
    delay.delayTime.value = 0.4;
    var fb = ctx.createGain();
    fb.gain.value = 0.28;
    var wet = ctx.createGain();
    wet.gain.value = 0.32;
    delay.connect(fb); fb.connect(delay);
    delay.connect(wet); wet.connect(filter);

    bgmBus = ctx.createGain();
    bgmBus.gain.value = 0;
    bgmBus.connect(filter);
    bgmBus.connect(delay);

    sfxBus = ctx.createGain();
    sfxBus.gain.value = 0.9;
    sfxBus.connect(master);
    return ctx;
  }

  /* 첫 사용자 조작에서 호출 — 브라우저 정책상 이때 열어야 합니다. */
  function unlock() {
    var c = init();
    if (!c) return;
    if (c.state === 'suspended') c.resume();
    started = true;
    if (bgmOn && moodName !== 'silent') startLoop();
  }

  function startLoop() {
    if (timer || !ctx) return;
    nextTime = ctx.currentTime + 0.06;
    step = 0;
    timer = setInterval(schedule, 140);
  }

  function stopLoop() {
    if (timer) { clearInterval(timer); timer = null; }
  }

  function schedule() {
    if (!ctx || !current) return;
    var m = current;
    var beat = 60 / m.bpm;
    while (nextTime < ctx.currentTime + 0.9) {
      playStep(m, step, nextTime, beat);
      nextTime += beat;
      step++;
    }
  }

  function playStep(m, i, t, beat) {
    var bar = Math.floor(i / 4) % m.chords.length;
    if (i % 4 === 0) {
      var chord = m.chords[bar];
      for (var k = 0; k < chord.length; k++) {
        pad(freq(chord[k]), beat * 3.9, m.pad * (k === 0 ? 1.15 : 0.78), t + k * 0.014);
      }
      bass(freq(chord[0] - 12), beat * 3.6, m.bass, t);
    }
    // 멜로디: 2박마다 한 음, every 주기마다 쉼
    if (i % 2 === 0) {
      var scale = m.bells[bar];
      var n = scale[(Math.floor(i / 2)) % scale.length];
      if ((i / 2) % m.every !== 0 || m.every < 8) {
        pluck(freq(n), beat * 2.4, m.pluck, t + 0.02);
      }
    }
    // 은은한 반짝임: 무드별 확률로 아주 높은 음
    if (m.shimmer && m.shimmer > 0 && (i % 8 === 3 || i % 8 === 6)) {
      if (Math.random() < m.shimmer * 0.5) {
        pluck(freq(88 + Math.floor(Math.random() * 5)), beat * 1.6, m.pluck * 0.32, t + 0.06);
      }
    }
    if (m === MOODS.tense && i % 4 === 2) {
      thump(t, 0.9);
    }
  }

  function pad(f, dur, vol, t) {
    var o = ctx.createOscillator();
    var o2 = ctx.createOscillator();
    var g = ctx.createGain();
    o.type = current.wave;
    o2.type = 'sine';
    o.frequency.value = f;
    o2.frequency.value = f * 1.004;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + Math.min(1.2, dur * 0.4));
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); o2.connect(g); g.connect(bgmBus);
    o.start(t); o2.start(t);
    o.stop(t + dur + 0.05); o2.stop(t + dur + 0.05);
  }

  function pluck(f, dur, vol, t) {
    var o = ctx.createOscillator();
    var o2 = ctx.createOscillator();
    var g = ctx.createGain();
    o.type = 'triangle';
    o2.type = 'sine';
    o.frequency.setValueAtTime(f, t);
    o2.frequency.setValueAtTime(f * 2.002, t);
    var g2 = ctx.createGain();
    g2.gain.value = 0.32;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); o2.connect(g2); g2.connect(g); g.connect(bgmBus);
    o.start(t); o2.start(t);
    o.stop(t + dur + 0.03); o2.stop(t + dur + 0.03);
  }

  function bass(f, dur, vol, t) {
    var o = ctx.createOscillator();
    var g = ctx.createGain();
    o.type = 'sine';
    o.frequency.setValueAtTime(f, t);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + 0.12);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(bgmBus);
    o.start(t); o.stop(t + dur + 0.05);
  }

  function thump(t, vol) {
    var o = ctx.createOscillator();
    var g = ctx.createGain();
    o.type = 'sine';
    o.frequency.setValueAtTime(72, t);
    o.frequency.exponentialRampToValueAtTime(40, t + 0.24);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol * 0.09, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.34);
    o.connect(g); g.connect(bgmBus);
    o.start(t); o.stop(t + 0.38);
  }

  /* ---------------- public ---------------- */
  function setMood(name) {
    if (name === moodName) return;
    moodName = name;
    if (!ctx) { if (name !== 'silent') init(); }
    if (!ctx) return;
    var target = MOODS[name];
    if (!target) {
      bgmBus.gain.cancelScheduledValues(ctx.currentTime);
      bgmBus.gain.setTargetAtTime(0, ctx.currentTime, 0.4);
      current = null;
      stopLoop();
      return;
    }
    current = target;
    step = 0;
    nextTime = ctx.currentTime + 0.1;
    if (started && bgmOn) {
      bgmBus.gain.cancelScheduledValues(ctx.currentTime);
      bgmBus.gain.setTargetAtTime(0.9, ctx.currentTime, 0.8);
      startLoop();
    }
  }

  function setBgm(on) {
    bgmOn = on;
    if (!ctx) return;
    if (!on) {
      bgmBus.gain.setTargetAtTime(0, ctx.currentTime, 0.3);
      stopLoop();
    } else if (started && moodName !== 'silent') {
      bgmBus.gain.setTargetAtTime(0.9, ctx.currentTime, 0.6);
      startLoop();
    }
  }

  function sfx(kind) {
    if (!enabled) return;
    var c = init();
    if (!c || c.state === 'suspended') return;
    var t = c.currentTime;
    if (kind === 'blip') {
      tone(1180 + Math.random() * 130, 0.016, 'sine', 0.01, t);
    } else if (kind === 'advance') {
      tone(520, 0.06, 'triangle', 0.026, t);
    } else if (kind === 'select') {
      tone(659, 0.07, 'triangle', 0.042, t);
      tone(988, 0.1, 'sine', 0.032, t + 0.06);
    } else if (kind === 'open') {
      tone(880, 0.06, 'sine', 0.028, t);
      tone(1175, 0.09, 'sine', 0.022, t + 0.05);
    } else if (kind === 'chime') {
      [523.25, 659.25, 783.99, 1046.5].forEach(function (f, i) {
        tone(f, 0.7, 'sine', 0.048, t + i * 0.14);
      });
    } else if (kind === 'heart') {
      tone(740, 0.09, 'sine', 0.033, t);
      tone(988, 0.12, 'sine', 0.028, t + 0.07);
    }
  }

  function tone(f, dur, type, vol, t) {
    var o = ctx.createOscillator();
    var g = ctx.createGain();
    o.type = type || 'sine';
    o.frequency.setValueAtTime(f, t);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol || 0.04, t + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(sfxBus);
    o.start(t); o.stop(t + dur + 0.02);
  }

  global.VNAudio = {
    unlock: unlock,
    setMood: setMood,
    setBgm: setBgm,
    sfx: sfx,
    setSfx: function (on) { enabled = on; },
    isReady: function () { return !!ctx; },
    debug: function () {
      return { state: ctx ? ctx.state : 'none', mood: moodName, bgmGain: bgmBus ? bgmBus.gain.value : 0 };
    }
  };
})(window);
