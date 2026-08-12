/* ===========================================================
   HUD-NAV.JS — the bottom menu's tracking reticle
   Shared by the inner pages. The homepage runs its own copy
   inside its single rAF loop alongside the nucleus.
   =========================================================== */
(function () {
  'use strict';
  var menu = document.getElementById('menu');
  var scan = document.getElementById('scan');
  if (!menu || !scan) return;

  var RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = [].slice.call(document.querySelectorAll('.mi'));
  var x = 0, w = 0, tx = 0, tw = 0, a = 0, ta = 0, init = false, raf = null;
  var lerp = function (p, q, t) { return p + (q - p) * t; };

  function to(el) {
    if (!el) return;
    tx = el.offsetLeft; tw = el.offsetWidth; ta = 1;
    if (!init) { x = tx; w = tw; init = true; }
    if (!raf) raf = requestAnimationFrame(loop);
  }
  function rest() { to(document.querySelector('.mi.on')); }

  function loop() {
    x = lerp(x, tx, .16); w = lerp(w, tw, .16); a = lerp(a, ta, .12);
    scan.style.transform = 'translateX(' + x.toFixed(1) + 'px)';
    scan.style.width = w.toFixed(1) + 'px';
    scan.style.opacity = a.toFixed(3);
    if (Math.abs(tx - x) > .3 || Math.abs(tw - w) > .3 || Math.abs(ta - a) > .01) {
      raf = requestAnimationFrame(loop);
    } else { raf = null; }
  }

  items.forEach(function (el) {
    el.addEventListener('pointerenter', function () { to(el); });
    el.addEventListener('focus', function () { to(el); });
  });
  menu.addEventListener('pointerleave', rest);
  addEventListener('resize', function () { init = false; rest(); });

  if (RM) { scan.style.opacity = 0; } else { rest(); }

  // Returning via the back/forward cache must not restore a stale reticle.
  addEventListener('pageshow', function () { init = false; rest(); });
})();
