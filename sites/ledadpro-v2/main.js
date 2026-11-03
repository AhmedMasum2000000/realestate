// LED AD PRO v2: hero slider, scroll effects, service image peek, dotted map with pins.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // Header: solid after scrolling, burger menu on phones
  const hdr = $('.hdr');
  const onScroll = () => hdr.classList.toggle('solid', scrollY > 40);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  $('.burger').addEventListener('click', () => hdr.classList.toggle('open'));
  $$('.nav a').forEach(a => a.addEventListener('click', () => hdr.classList.remove('open')));

  // Hero crossfade slider with dash progress
  const slides = $$('.slide'), dashes = $('.dashes'), DUR = 6000;
  let cur = 0, timer;
  slides.forEach((_, i) => {
    const b = document.createElement('button');
    b.className = 'dash'; b.setAttribute('aria-label', `Slide ${i + 1}`);
    b.style.setProperty('--dur', DUR + 'ms'); b.innerHTML = '<i></i>';
    b.addEventListener('click', () => go(i));
    dashes.appendChild(b);
  });
  const ds = $$('.dash');
  function go(i) {
    slides[cur].classList.remove('on'); ds[cur].classList.remove('on');
    cur = (i + slides.length) % slides.length;
    slides[cur].classList.add('on');
    void ds[cur].offsetWidth; ds[cur].classList.add('on');
    clearTimeout(timer); if (!reduce) timer = setTimeout(() => go(cur + 1), DUR);
  }
  go(0);

  // Reveal on scroll
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { threshold: .15 });
  $$('.rv').forEach(el => io.observe(el));

  // Statement fill and cyan-band word reveal, both driven by scroll position
  const st = $('.statement h2'), band = $('.band h2');
  band.innerHTML = band.textContent.trim().split(/\s+/).map(w => `<span class="w">${w}</span>`).join(' ');
  const words = $$('.w', band);
  const prog = el => { const r = el.getBoundingClientRect(); return Math.min(1, Math.max(0, (innerHeight - r.top) / (innerHeight + r.height * .2))); };
  function tick() {
    st.style.setProperty('--p', (reduce ? 100 : Math.round(prog(st) * 130 - 15)) + '%');
    const n = reduce ? words.length : Math.floor(prog(band) * 1.6 * words.length);
    words.forEach((w, i) => w.classList.toggle('on', i < n));
  }
  addEventListener('scroll', () => requestAnimationFrame(tick), { passive: true }); tick();

  // Service rows: image follows the pointer
  const peek = $('.svc-peek'), pimg = $('img', peek);
  $$('.svc-row').forEach(r => {
    r.addEventListener('mouseenter', () => { pimg.src = r.dataset.img; peek.classList.add('on'); });
    r.addEventListener('mouseleave', () => peek.classList.remove('on'));
  });
  addEventListener('mousemove', e => { peek.style.left = e.clientX + 'px'; peek.style.top = e.clientY + 'px'; });

  // Dotted map of Bangladesh with pulsing pins
  const cv = $('#map'), ctx = cv.getContext('2d');
  // Rough outline of Bangladesh as [lon, lat], enough for a dot-matrix silhouette.
  const SHAPE = [[88.03,24.66],[88.14,24.92],[88.45,25.17],[88.68,25.22],[88.95,25.18],[89.01,25.29],[88.83,25.48],[88.56,25.53],[88.44,25.85],[88.65,26.13],[88.95,26.29],[89.12,26.03],[89.33,26.02],[89.55,26.23],[89.84,25.97],[89.86,25.42],[90.12,25.26],[90.6,25.17],[91.1,25.2],[91.66,25.14],[92.04,25.18],[92.47,24.98],[92.22,24.5],[91.92,24.33],[91.73,24.15],[91.37,24.1],[91.16,23.62],[91.37,23.19],[91.6,22.95],[91.82,23.36],[92.15,23.73],[92.29,23.68],[92.36,22.95],[92.58,22.04],[92.66,21.32],[92.33,20.67],[92.08,21.19],[92.03,21.7],[91.82,22.18],[91.47,22.47],[91.03,22.68],[90.6,22.39],[90.27,21.84],[89.84,21.86],[89.6,22.14],[89.03,22.06],[88.89,22.88],[88.53,23.63],[88.7,24.23],[88.03,24.66]];
  const B = { x0: 86.1, x1: 92.9, y0: 20.4, y1: 26.7 };
  // Dhaka inset: a zoomed circle over the Bay of Bengal, so the city pins don't overlap.
  const DK = { x0: 90.33, x1: 90.47, y0: 23.70, y1: 23.88 }, DHAKA = [90.40, 23.78];
  let pins = [], W, H, dots = [], idots = [], active = 0, inset;
  const proj = (lon, lat) => [(lon - B.x0) / (B.x1 - B.x0) * W, (B.y1 - lat) / (B.y1 - B.y0) * H];
  function inside(x, y, poly) {
    let c = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const [xi, yi] = poly[i], [xj, yj] = poly[j];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c;
    }
    return c;
  }
  function layout() {
    const dpr = devicePixelRatio || 1, r = cv.getBoundingClientRect();
    W = r.width; H = r.height; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const poly = SHAPE.map(([a, b]) => proj(a, b)), step = Math.max(7, W / 62);
    dots = [];
    for (let y = step / 2; y < H; y += step) for (let x = step / 2; x < W; x += step) if (inside(x, y, poly)) dots.push([x, y]);
    inset = { x: W * .19, y: H * .8, r: W * .165 };
    const k = inset.r * 2 / (DK.x1 - DK.x0);
    const ip = (lon, lat) => [inset.x + (lon - (DK.x0 + DK.x1) / 2) * k, inset.y - (lat - (DK.y0 + DK.y1) / 2) * k];
    idots = []; const s2 = step * .8;
    for (let y = inset.y - inset.r; y < inset.y + inset.r; y += s2) for (let x = inset.x - inset.r; x < inset.x + inset.r; x += s2)
      if (Math.hypot(x - inset.x, y - inset.y) < inset.r - 6) idots.push([x, y]);
    pins = $$('.loc-list li').map(li => ({ li, p: ip(+li.dataset.lon, +li.dataset.lat) }));
  }
  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(143,163,196,.35)';
    for (const [x, y] of dots) { ctx.beginPath(); ctx.arc(x, y, 1.7, 0, 7); ctx.fill(); }
    // Dhaka on the country map, linked to the inset
    const [dx, dy] = proj(...DHAKA);
    ctx.strokeStyle = 'rgba(0,209,255,.5)'; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(dx, dy); ctx.lineTo(inset.x + inset.r * .7, inset.y - inset.r * .7); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = '#00d1ff'; ctx.beginPath(); ctx.arc(dx, dy, 6, 0, 7); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.font = '800 12px Inter, sans-serif'; ctx.fillText('DHAKA', dx + 12, dy + 4);
    // Inset
    ctx.fillStyle = 'rgba(7,18,43,.92)'; ctx.strokeStyle = 'rgba(0,209,255,.6)'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(inset.x, inset.y, inset.r, 0, 7); ctx.fill(); ctx.stroke();
    ctx.fillStyle = 'rgba(143,163,196,.18)';
    for (const [x, y] of idots) { ctx.beginPath(); ctx.arc(x, y, 1.2, 0, 7); ctx.fill(); }
    pins.forEach(({ p: [x, y], li }, i) => {
      const on = i === active, ph = ((t / 1600) + i * .37) % 1;
      if (!reduce) { ctx.strokeStyle = `rgba(0,209,255,${(1 - ph) * .8})`; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 5 + ph * (on ? 26 : 14), 0, 7); ctx.stroke(); }
      ctx.fillStyle = on ? '#00d1ff' : 'rgba(0,209,255,.7)'; ctx.beginPath(); ctx.arc(x, y, on ? 7 : 4.5, 0, 7); ctx.fill();
      if (on) {
        const label = li.firstChild.textContent.trim().toUpperCase();
        ctx.font = '800 12px Inter, sans-serif';
        const w = ctx.measureText(label).width, lx = Math.min(x + 12, inset.x + inset.r - w - 4);
        ctx.fillStyle = '#fff'; ctx.fillText(label, lx, y - 12);
      }
    });
    requestAnimationFrame(draw);
  }
  $$('.loc-list li').forEach((li, i) => {
    if (i === 0) li.classList.add('on');
    li.addEventListener('mouseenter', () => { active = i; $$('.loc-list li').forEach(l => l.classList.toggle('on', l === li)); });
    li.addEventListener('click', () => { active = i; $$('.loc-list li').forEach(l => l.classList.toggle('on', l === li)); });
  });
  addEventListener('resize', layout); layout(); requestAnimationFrame(draw);

  $('#yr').textContent = new Date().getFullYear();
})();
