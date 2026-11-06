(function () {
  var d = document, b = d.body, reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // wordmarks fill the width
  var marks = [].slice.call(d.querySelectorAll('[data-fit]'));
  function fit() {
    marks.forEach(function (s) {
      var box = s.parentNode.clientWidth; if (!box) return;
      s.style.fontSize = '100px'; s.style.fontSize = (100 * box / s.offsetWidth * 0.995).toFixed(1) + 'px';
    });
  }
  fit(); addEventListener('resize', fit); if (d.fonts && d.fonts.ready) d.fonts.ready.then(fit);

  // top bar swaps the tagline for the small wordmark once the hero is gone
  var bar = d.getElementById('bar'), hero = d.querySelector('.hero');
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { bar.classList.toggle('scrolled', !es[0].isIntersecting); }, { threshold: 0.15 }).observe(hero);

  // menu overlay
  var btn = d.getElementById('menu-btn'), menu = d.getElementById('menu');
  [].forEach.call(menu.querySelectorAll('.menu-links a'), function (a, i) { a.style.setProperty('--i', i); });
  function toggle(open) {
    menu.hidden = !open; btn.setAttribute('aria-expanded', open); b.classList.toggle('menu-open', open);
  }
  btn.addEventListener('click', function () { toggle(menu.hidden); });
  menu.addEventListener('click', function (ev) { if (ev.target.closest('a')) toggle(false); });
  addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && !menu.hidden) toggle(false); });

  // reel: crossfade our own screen photos
  var slides = [].slice.call(d.querySelectorAll('.reel-frame img')), cur = 0;
  if (slides.length > 1 && !reduce) setInterval(function () {
    slides[cur].classList.remove('on'); cur = (cur + 1) % slides.length; slides[cur].classList.add('on');
  }, 4200);

  // reveal sections as they come in
  var rv = [].slice.call(d.querySelectorAll('.rv'));
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -10% 0px' });
    rv.forEach(function (x) { io.observe(x); });
  } else rv.forEach(function (x) { x.classList.add('in'); });
})();
