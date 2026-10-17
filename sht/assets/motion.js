/* Second Home Thailand: restrained motion. Words rise, groups stagger, the process pins and the
   page keeps a quiet pulse (echo drift, clock, ticker). No libraries, no tracking. */
(() => {
  'use strict';
  const root = document.documentElement;
  const full = root.classList.contains('motion-ok');
  const seen = (nodes, onIn, threshold = 0.12) => {
    if (!('IntersectionObserver' in window)) { nodes.forEach(onIn); return; }
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { onIn(entry.target); observer.unobserve(entry.target); }
    }), {threshold, rootMargin: '0px 0px -6% 0px'});
    nodes.forEach(node => observer.observe(node));
  };

  // Local time in Pattaya, to the second.
  const clocks = document.querySelectorAll('[data-local-time]');
  if (clocks.length) {
    const format = new Intl.DateTimeFormat('en-GB', {timeZone: 'Asia/Bangkok', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false});
    const tick = () => { const time = format.format(new Date()); clocks.forEach(node => { node.textContent = 'Pattaya ' + time + ' ICT'; }); };
    tick();
    setInterval(tick, 1000);
  }

  // Count the trust metrics up from zero when they come into view.
  const counters = [...document.querySelectorAll('[data-count]')];
  seen(counters, node => {
    const target = Number(node.dataset.count);
    if (!full || !Number.isFinite(target)) return;
    const start = performance.now();
    const step = now => {
      const t = Math.min(1, (now - start) / 1400);
      node.textContent = String(Math.round(target * (1 - Math.pow(1 - t, 3))));
      if (t < 1) requestAnimationFrame(step);
    };
    node.textContent = '0';
    requestAnimationFrame(step);
  }, 0.4);

  // Header hides on the way down, returns on the way up. Scroll progress runs along the top.
  const header = document.querySelector('.header');
  const progress = document.querySelector('[data-page-progress]');
  const mobileCta = document.querySelector('.mobile-cta');
  let last = scrollY;
  const onScroll = () => {
    const y = scrollY;
    const max = document.documentElement.scrollHeight - innerHeight;
    if (progress) progress.style.setProperty('--p', max > 0 ? (y / max).toFixed(4) : 0);
    const menuOpen = document.querySelector('.menu-toggle[aria-expanded=true]');
    if (header && !menuOpen) header.classList.toggle('is-hidden', y > 240 && y > last + 2);
    if (header && y < last - 2) header.classList.remove('is-hidden');
    if (mobileCta) mobileCta.classList.toggle('is-shown', y > innerHeight * 0.6);
    last = y;
    pin();
  };

  // Pinned process: four steps across a 400vh section.
  const pinned = document.querySelector('[data-pin]');
  const steps = pinned ? [...pinned.querySelectorAll('[data-pin-step]')] : [];
  const number = pinned && pinned.querySelector('[data-pin-number]');
  const bar = pinned && pinned.querySelector('[data-pin-progress]');
  let current = -1;
  function pin() {
    if (!pinned || !full) return;
    const box = pinned.getBoundingClientRect();
    const travel = box.height - innerHeight;
    const p = travel > 0 ? Math.min(1, Math.max(0, -box.top / travel)) : 0;
    if (bar) bar.style.width = (p * 100).toFixed(2) + '%';
    const active = Math.min(steps.length - 1, Math.floor(p * steps.length * 0.999));
    if (active === current) return;
    current = active;
    steps.forEach((step, index) => { step.classList.toggle('is-active', index === active); step.classList.toggle('is-done', index < active); });
    if (number) number.textContent = String(active + 1).padStart(2, '0');
  }
  if (pinned && !full) steps.forEach(step => step.classList.add('is-active'));

  addEventListener('scroll', onScroll, {passive: true});
  addEventListener('resize', onScroll);
  onScroll();

  if (!full) return;

  // Split headings into words, keeping <em> and <br> in place.
  const split = element => {
    let i = 0;
    const walk = node => {
      [...node.childNodes].forEach(child => {
        if (child.nodeType === 3) {
          const parts = child.textContent.split(/(\s+)/);
          const fragment = document.createDocumentFragment();
          parts.forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { fragment.appendChild(document.createTextNode(part)); return; }
            const word = document.createElement('span');
            word.className = 'w';
            word.style.setProperty('--i', i++);
            word.textContent = part;
            fragment.appendChild(word);
          });
          child.replaceWith(fragment);
        } else if (child.nodeType === 1 && child.tagName !== 'BR') {
          walk(child);
        }
      });
    };
    walk(element);
  };
  const headings = [...document.querySelectorAll('[data-reveal-words]')];
  headings.forEach(split);
  seen(headings, node => node.classList.add('is-in'));

  // Groups stagger in sequence; capped so long lists do not wait.
  const groups = new Map();
  document.querySelectorAll('[data-stagger]').forEach(node => {
    const parent = node.parentElement;
    const index = groups.get(parent) || 0;
    groups.set(parent, index + 1);
    node.style.setProperty('--d', Math.min(index * 80, 480) + 'ms');
  });
  seen([...document.querySelectorAll('[data-stagger]')], node => node.classList.add('is-in'), 0.08);

  // The echo stack fans out once, then drifts.
  const echo = document.querySelector('.echo');
  if (echo) {
    echo.querySelectorAll('.echo-row').forEach((row, index) => row.style.setProperty('--row', index));
    requestAnimationFrame(() => requestAnimationFrame(() => echo.classList.add('is-in')));
    setTimeout(() => echo.classList.add('is-settled'), 2800);
  }
})();
