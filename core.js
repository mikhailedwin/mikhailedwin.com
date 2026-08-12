/* ===========================================================
   CORE.SYS — shared runtime for all pages
   SIG bus · quantum pool · spotlight · reveal · fx registry
   =========================================================== */
(function () {
  'use strict';

  // ── SIG: tiny pub/sub + shared flags ──────────────────────
  var listeners = {};
  var SIG = {
    rm: window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    fine: window.matchMedia && window.matchMedia('(pointer: fine)').matches,
    on: function (ev, fn) { (listeners[ev] = listeners[ev] || []).push(fn); },
    emit: function (ev, data) {
      (listeners[ev] || []).forEach(function (fn) { try { fn(data); } catch (e) {} });
    }
  };
  window.SIG = SIG;

  // ── Quantum RNG pool (weekly circuit results) ─────────────
  window._qrn = window._qrn || [];
  window._qrnIdx = window._qrnIdx || 0;
  window.qrand = window.qrand || function () {
    return window._qrn.length ? window._qrn[window._qrnIdx++ % window._qrn.length] : Math.random();
  };
  fetch('quantum_rng.json?w=' + Math.floor(Date.now() / 604800000))
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (d.values && d.values.length) { window._qrn = d.values; SIG.emit('qrng:loaded', d); }
    })
    .catch(function () {});

  // ── Spotlight follow ───────────────────────────────────────
  var spot = document.getElementById('spotlight');
  if (spot) {
    document.addEventListener('mousemove', function (e) {
      spot.style.setProperty('--mx', e.clientX + 'px');
      spot.style.setProperty('--my', e.clientY + 'px');
    });
  }

  // ── Reveal on scroll ───────────────────────────────────────
  var revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) en.target.classList.add('in'); });
    }, { threshold: 0.15 });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  // ── Text corruption burst (.sys-flicker / data-fx="flicker") ──
  var NOISE = '█▓░▒#?X!@01%$';
  function runBurst(el, orig) {
    if (SIG.rm) return;
    var ticks = 0;
    var total = 5 + Math.floor(window.qrand() * 7);
    var id = setInterval(function () {
      var chars = orig.split('');
      var corrupt = 1 + Math.floor(Math.random() * 3);
      for (var n = 0; n < corrupt; n++) {
        var pos = Math.floor(Math.random() * chars.length);
        chars[pos] = NOISE[Math.floor(Math.random() * NOISE.length)];
      }
      el.textContent = chars.join('');
      el.style.opacity = Math.random() > 0.25 ? '1' : '0.05';
      if (++ticks >= total) {
        clearInterval(id);
        el.textContent = orig;
        el.style.opacity = '';
        setTimeout(function () { runBurst(el, orig); }, 600 + window.qrand() * 2800);
      }
    }, 35 + window.qrand() * 55);
  }
  window.runBurst = runBurst;
  document.querySelectorAll('.sys-flicker, [data-fx~="flicker"]').forEach(function (el) {
    el._orig = el.textContent;
    setTimeout(function () { runBurst(el, el._orig); }, window.qrand() * 1200);
  });

  // ── Decode-in: headings scramble-resolve when they appear ──
  function decodeEl(el) {
    if (el._decoded) return;
    el._decoded = true;
    if (SIG.rm) return;
    // Collect text nodes so child spans (.acc/.mag colours) survive
    var nodes = [];
    (function walk(n) {
      n.childNodes.forEach(function (c) {
        if (c.nodeType === 3 && c.textContent.trim()) nodes.push({ node: c, orig: c.textContent });
        else if (c.nodeType === 1) walk(c);
      });
    })(el);
    if (!nodes.length) return;
    var totalLen = nodes.reduce(function (s, n) { return s + n.orig.length; }, 0);
    var start = null, DUR = 560;
    function frame(ts) {
      if (!start) start = ts;
      var p = Math.min(1, (ts - start) / DUR);
      var resolved = Math.floor(p * totalLen);
      var seen = 0;
      nodes.forEach(function (n) {
        var out = '';
        for (var i = 0; i < n.orig.length; i++) {
          var ch = n.orig[i];
          if (ch === ' ' || seen + i < resolved) out += ch;
          else out += NOISE[Math.floor(Math.random() * NOISE.length)];
        }
        n.node.textContent = out;
        seen += n.orig.length;
      });
      if (p < 1) requestAnimationFrame(frame);
      else nodes.forEach(function (n) { n.node.textContent = n.orig; });
    }
    requestAnimationFrame(frame);
  }
  var decodeTargets = document.querySelectorAll('.section-title, .page-title, [data-fx~="decode"]');
  if (decodeTargets.length) {
    var dio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { decodeEl(en.target); dio.unobserve(en.target); }
      });
    }, { threshold: 0.3 });
    decodeTargets.forEach(function (el) { dio.observe(el); });
  }

  // ── 3D tilt + specular sheen (data-fx="tilt") ──────────────
  if (SIG.fine && !SIG.rm) {
    document.querySelectorAll('[data-fx~="tilt"]').forEach(function (el) {
      var rx = 0, ry = 0, tx = 0, ty = 0, raf = null;
      var sheen = document.createElement('div');
      sheen.className = 'fx-sheen';
      el.appendChild(sheen);
      function loop() {
        rx += (tx - rx) * 0.12;
        ry += (ty - ry) * 0.12;
        el.style.transform = 'perspective(900px) rotateX(' + rx.toFixed(3) + 'deg) rotateY(' + ry.toFixed(3) + 'deg)';
        if (Math.abs(tx - rx) > 0.01 || Math.abs(ty - ry) > 0.01) raf = requestAnimationFrame(loop);
        else { raf = null; if (tx === 0 && ty === 0) el.style.transform = ''; }
      }
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width;
        var py = (e.clientY - r.top) / r.height;
        tx = (py - 0.5) * -6;
        ty = (px - 0.5) * 6;
        el.style.setProperty('--px', (px * 100).toFixed(1) + '%');
        el.style.setProperty('--py', (py * 100).toFixed(1) + '%');
        if (!raf) raf = requestAnimationFrame(loop);
      });
      el.addEventListener('pointerleave', function () {
        tx = 0; ty = 0;
        if (!raf) raf = requestAnimationFrame(loop);
      });
    });
  }

  // ── Parallax depth: expose scroll position as a CSS var ────
  if (!SIG.rm) {
    var syTick = false;
    window.addEventListener('scroll', function () {
      if (syTick) return;
      syTick = true;
      requestAnimationFrame(function () {
        document.documentElement.style.setProperty('--scroll-y', window.scrollY);
        syTick = false;
      });
    }, { passive: true });
  }

  // ── rAF hygiene: reset timing baselines when tab regains focus ──
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) SIG.emit('visible');
  });
})();
