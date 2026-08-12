/* ===========================================================
   HUD-GLITCH.JS — display type that corrupts like the terminal
   The CSS layers give the RGB split; this gives the character
   scramble that makes SEQUENCING feel alive. Both data-text and
   textContent are rewritten together so the ghost layers follow
   the corruption instead of drifting out of sync.
   =========================================================== */
(function () {
  'use strict';
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var NOISE = '█▓░▒#?X!@01%$/\\<>[]{}=+*ΞΔΩ';
  var els = [].slice.call(document.querySelectorAll('.glitch'));
  if (!els.length) return;

  function scramble(el) {
    if (el._busy) return;
    el._busy = true;

    var real = el.dataset.text || el.textContent;
    var mode = Math.random();
    // Short bursts mangle a couple of glyphs; rare long ones eat the word.
    var heavy = mode > .82;
    var ticks = heavy ? 9 + Math.floor(Math.random() * 6) : 3 + Math.floor(Math.random() * 4);
    var n = 0;

    var id = setInterval(function () {
      var ch = real.split('');
      var hits = heavy
        ? Math.ceil(ch.length * (.45 + Math.random() * .4))
        : 1 + Math.floor(Math.random() * 2);
      for (var i = 0; i < hits; i++) {
        var p = Math.floor(Math.random() * ch.length);
        ch[p] = NOISE[Math.floor(Math.random() * NOISE.length)];
      }
      var out = ch.join('');
      el.textContent = out;
      el.dataset.text = out;          // keep the RGB ghosts in step

      if (++n >= ticks) {
        clearInterval(id);
        el.textContent = real;
        el.dataset.text = real;
        el._busy = false;
      }
    }, heavy ? 46 : 38);
  }

  els.forEach(function (el) {
    // Stagger so stacked lines never corrupt in lockstep.
    (function loop() {
      setTimeout(function () { scramble(el); loop(); }, 2200 + Math.random() * 5200);
    })();
  });

  // Hovering the block provokes it.
  els.forEach(function (el) {
    var host = el.closest('.ident, .phead') || el;
    host.addEventListener('pointerenter', function () {
      els.forEach(function (e, i) { setTimeout(function () { scramble(e); }, i * 70); });
    });
  });
})();
