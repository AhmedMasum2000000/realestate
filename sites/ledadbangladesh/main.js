(function () {
  var d = document, reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- Dhaka clock (UTC+6)
  var clocks = [].slice.call(d.querySelectorAll('#clock, [data-clock]'));
  function tick() {
    var n = new Date(), t = new Date(n.getTime() + (n.getTimezoneOffset() + 360) * 60000);
    var s = [t.getHours(), t.getMinutes(), t.getSeconds()].map(function (x) { return (x < 10 ? '0' : '') + x; }).join(':');
    clocks.forEach(function (c) { c.textContent = s; c.setAttribute('datetime', s); });
  }
  tick(); setInterval(tick, 1000);

  // ---- fit the wordmark to the width
  var fit = d.querySelector('[data-fit]'), mark = fit && fit.parentNode;
  function fitMark() {
    if (!fit) return;
    var box = mark.clientWidth; if (!box) return;
    if (innerWidth <= 760) { // two lines on phones: fit the longer word
      fit.innerHTML = 'LED AD<br>Bangladesh';
      fit.style.fontSize = '100px';
      var probe = d.createElement('span'); probe.textContent = 'Bangladesh'; probe.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font-size:100px';
      mark.appendChild(probe); var w = probe.offsetWidth; mark.removeChild(probe);
      fit.style.fontSize = Math.floor(100 * (box - 24) / w) + 'px';
    } else {
      fit.textContent = 'LED AD Bangladesh';
      fit.style.fontSize = '100px';
      fit.style.fontSize = Math.floor(100 * box / fit.offsetWidth * 0.995) + 'px';
    }
  }
  fitMark(); addEventListener('resize', fitMark);
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(fitMark);

  // ---- letter pattern: nested diamonds of our letters spreading out from two points, like a
  // signal going out; each letter has its own brightness; the pointer lights letters up
  var c = d.getElementById('pattern'), hero = c && c.parentNode;
  if (c && c.getContext) {
    var X = c.getContext('2d'), WORD = 'LED AD ', dpr = Math.min(2, devicePixelRatio || 1);
    var cw, ch, cols, rows, W, H, mx = -1e4, my = -1e4, visible = true, last = 0, t0 = performance.now();
    function size() {
      W = hero.clientWidth; H = hero.clientHeight; c.width = W * dpr; c.height = H * dpr;
      var base = W < 760 ? 12 : 13; cw = base * dpr; ch = (base - 2) * dpr; cols = Math.ceil(c.width / cw); rows = Math.ceil(c.height / ch);
      X.font = '500 ' + (base - 3.5) * dpr + 'px Inter, Helvetica, Arial, sans-serif'; X.textBaseline = 'middle'; X.textAlign = 'center';
      draw(performance.now());
    }
    function tri(v, p, w) { v = ((v % p) + p) % p; var dd = Math.min(v, p - v); return dd < w ? 1 - dd / w : 0; }
    function hash(x, y) { var s = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453; return s - Math.floor(s); }
    function draw(now) {
      var t = reduce ? 0 : (now - t0) / 1000;
      X.clearRect(0, 0, c.width, c.height);
      var P = 15, Wd = 3.4, r = 9, k = cw / ch, cy = rows * 0.5;
      var cx1 = cols * (W < 760 ? 0.5 : 0.27), cx2 = cols * 0.73;
      for (var y = 0; y < rows; y++) {
        var dy = Math.abs(y - cy) * k;
        for (var x = 0; x < cols; x++) {
          var rad = Math.abs(x - cx1) + dy; if (W >= 760) rad = Math.min(rad, Math.abs(x - cx2) + dy);
          var a = tri(rad - t * 1.6, P, Wd);
          var px = x - mx, py = y - my, dist = Math.sqrt(px * px + py * py);
          if (dist < r) a += (1 - dist / r) * 0.9;
          if (a < 0.08) continue;
          var ch1 = WORD[(x + (y >> 1)) % 7]; if (ch1 === ' ') continue;
          X.fillStyle = 'rgba(17,17,17,' + Math.min(0.85, a * (0.45 + 0.55 * hash(x, y))).toFixed(3) + ')';
          X.fillText(ch1, (x + 0.5) * cw, (y + 0.5) * ch);
        }
      }
    }
    function loop(now) {
      if (visible && now - last > 40) { last = now; draw(now); }
      if (!reduce) requestAnimationFrame(loop);
    }
    size(); addEventListener('resize', size);
    if (!reduce) requestAnimationFrame(loop);
    hero.addEventListener('pointermove', function (ev) { var b = c.getBoundingClientRect(); mx = (ev.clientX - b.left) * dpr / cw; my = (ev.clientY - b.top) * dpr / ch; }, { passive: true });
    hero.addEventListener('pointerleave', function () { mx = my = -1e4; });
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(hero);
  }

  // ---- show / hide lists
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-toggle]'); if (!b) return;
    var list = d.getElementById(b.dataset.toggle), hide = b.hasAttribute('data-hide');
    list.hidden = hide;
    var box = b.parentNode; [].forEach.call(box.querySelectorAll('button'), function (x) { x.classList.toggle('on', x.hasAttribute('data-hide') === hide); x.setAttribute('aria-expanded', !hide); });
  });

  // ---- reveal images as they arrive
  var imgs = [].slice.call(d.querySelectorAll('.it img'));
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    imgs.forEach(function (i) { io.observe(i); });
  } else imgs.forEach(function (i) { i.classList.add('in'); });
})();
