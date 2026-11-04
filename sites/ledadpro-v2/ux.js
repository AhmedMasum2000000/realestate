/* LED AD PRO: shared UX layer for every page (loaded with defer).
   - logo/globe pops in front on internal link clicks while the next page loads
   - hover/touch prefetch of internal pages (speculation rules do prerender where supported)
   - WhatsApp button to the sales line, scroll progress bar, count-up stats
   - homepage goal planner (#planner): pick a goal, get the right service mix, send it on WhatsApp */
(function () {
  var WA = '8801958503753', d = document, reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var intro = d.getElementById('intro');

  // ---- page transition on internal links
  function internal(a) {
    if (!a || a.target || a.hasAttribute('download')) return false;
    var u; try { u = new URL(a.href, location.href); } catch (e) { return false; }
    if (u.origin !== location.origin || !/^https?:$/.test(u.protocol)) return false;
    if (u.pathname === location.pathname && u.search === location.search) return false; // same page / hash
    return !/\.(pdf|jpe?g|png|webp|svg|mp4|zip)$/i.test(u.pathname);
  }
  d.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest('a[href]');
    if (!internal(a) || !intro || reduce) return;
    e.preventDefault();
    intro.classList.remove('out'); intro.classList.add('q', 'show');
    setTimeout(function () { location.href = a.href; }, 140);
  });

  // ---- prefetch on hover / touch (fallback where speculation rules are not supported)
  var done = {};
  function pre(e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!internal(a) || done[a.href]) return; done[a.href] = 1;
    var l = d.createElement('link'); l.rel = 'prefetch'; l.href = a.href; d.head.appendChild(l);
  }
  d.addEventListener('mouseover', pre, { passive: true }); d.addEventListener('touchstart', pre, { passive: true });

  // ---- scroll progress bar (blue -> cyan -> green)
  var bar = d.createElement('div'); bar.className = 'ux-progress'; d.body.appendChild(bar);
  var tick = 0;
  addEventListener('scroll', function () {
    if (tick) return; tick = 1;
    requestAnimationFrame(function () { var h = d.documentElement; bar.style.transform = 'scaleX(' + (h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)) + ')'; tick = 0; });
  }, { passive: true });

  // ---- WhatsApp button
  var w = d.createElement('a'); w.className = 'ux-wa'; w.target = '_blank'; w.rel = 'noopener';
  w.href = 'https://wa.me/' + WA + '?text=' + encodeURIComponent('Hi LED AD PRO, I want to advertise. (' + location.href + ')');
  w.setAttribute('aria-label', 'Chat with sales on WhatsApp');
  w.innerHTML = '<svg viewBox="0 0 32 32" width="26" height="26" aria-hidden="true"><path fill="#fff" d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.7a10.7 10.7 0 0 1-5.5-1.5l-.4-.2-3.9 1 1-3.8-.3-.4A10.7 10.7 0 1 1 16 26.7zm5.9-8c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1a8.8 8.8 0 0 1-4.4-3.8c-.3-.6.3-.5.9-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.5c.2.2 2.4 3.6 5.7 5 2.1.9 2.9 1 4 .8.6-.1 1.9-.8 2.2-1.5.3-.7.3-1.3.2-1.5-.1-.1-.3-.2-.6-.3z"/></svg><span>Chat with sales</span>';
  d.body.appendChild(w);
  // on pages whose hero already has call/WhatsApp buttons, bring the floating button in after the hero
  var heroCta = d.querySelector('.hero-cta');
  if (heroCta && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { es.forEach(function (en) { w.classList.toggle('in', !en.isIntersecting); }); }).observe(heroCta);
  } else setTimeout(function () { w.classList.add('in'); }, 2200);

  // ---- count-up numbers (".stats b", "[data-count]")
  var nums = [].slice.call(d.querySelectorAll('.stats b, [data-count]'));
  if (nums.length && 'IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return; io.unobserve(en.target);
        var el = en.target, m = el.textContent.match(/^([^\d]*)([\d,]+)(.*)$/); if (!m) return;
        var to = +m[2].replace(/,/g, ''), t0 = performance.now(), dur = 1100;
        (function f(t) { var k = Math.min(1, (t - t0) / dur), v = Math.round(to * (1 - Math.pow(1 - k, 3)));
          el.textContent = m[1] + v.toLocaleString('en-IN') + m[3]; if (k < 1) requestAnimationFrame(f); })(t0);
      });
    }, { threshold: .6 });
    nums.forEach(function (n) { io.observe(n); });
  }

  // ---- hero booking cut-off: content is due by the 10th (airs the 15th) or the 25th (airs the 1st), Dhaka time
  var U = d.getElementById('hero-urgent');
  if (U) {
    var MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var dhaka = function () { var n = new Date(); return new Date(n.getTime() + (n.getTimezoneOffset() + 360) * 60000); };
    var next = function (t) {
      var y = t.getFullYear(), m = t.getMonth(), c = [];
      for (var k = 0; k < 3; k++) { var mm = m + k; c.push([new Date(y, mm, 10, 23, 59, 59), new Date(y, mm, 15)]); c.push([new Date(y, mm, 25, 23, 59, 59), new Date(y, mm + 1, 1)]); }
      for (var i = 0; i < c.length; i++) if (c[i][0] > t) return c[i];
    };
    var t0 = dhaka(), n = next(t0), fmt = function (x) { return x.getDate() + ' ' + MON[x.getMonth()]; };
    U.querySelector('[data-dl-date]').textContent = fmt(n[0]);
    U.querySelector('[data-dl-live]').textContent = fmt(n[1]);
    var cd = U.querySelector('[data-dl-cd]');
    var upd = function () { var ms = n[0] - dhaka(); if (ms < 0) return;
      var dd = Math.floor(ms / 864e5), h = Math.floor(ms / 36e5) % 24, mi = Math.floor(ms / 6e4) % 60, s = Math.floor(ms / 1e3) % 60;
      cd.textContent = (dd ? dd + 'd ' : '') + h + 'h ' + (mi < 10 ? '0' : '') + mi + 'm ' + (s < 10 ? '0' : '') + s + 's left'; };
    upd(); setInterval(upd, 1000);
  }

  // ---- goal planner (homepage)
  var P = d.getElementById('planner');
  if (P) {
    var GOALS = {
      launch: ['Launch a new product', ['LED billboards', 'Metro Rail LED', 'LED caravan', 'Digital marketing']],
      store: ['Open a store or branch', ['Outlet opening', 'Building branding', 'LED caravan', 'Printing']],
      festive: ['Win festive sales', ['LED billboards', 'Metro Rail LED', 'Newspaper ads', 'In-store branding']],
      trust: ['Build trust and authority', ['Static billboards', 'Airport branding', 'Building branding', 'Newspaper ads']],
      city: ['Reach a new city or district', ['Static billboards', 'LED caravan', 'Bus branding', 'Events']],
      try: ['Get people to try it', ['Events & activations', 'LED caravan', 'Printing & packaging', 'Digital marketing']]
    };
    var out = P.querySelector('.pl-out'), mix = P.querySelector('.pl-mix'), cta = P.querySelector('.pl-wa');
    P.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-goal]'); if (!b) return;
      [].forEach.call(P.querySelectorAll('button[data-goal]'), function (x) { x.setAttribute('aria-pressed', x === b); });
      var g = GOALS[b.dataset.goal];
      mix.innerHTML = g[1].map(function (s, i) { return '<li style="--d:' + i * 70 + 'ms">' + s + '</li>'; }).join('');
      cta.href = 'https://wa.me/' + WA + '?text=' + encodeURIComponent('Hi LED AD PRO, my goal: ' + g[0] + '. Suggested mix: ' + g[1].join(', ') + '. Please send me a plan and quote.');
      out.hidden = false; out.classList.remove('on'); void out.offsetWidth; out.classList.add('on');
    });
  }
})();
