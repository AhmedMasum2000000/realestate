/* Second Home Thailand: restrained motion. Words rise, groups stagger, the process pins and the
   page keeps a quiet pulse (hero light and embers, clock, ticker). No libraries, no tracking. */
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
  const cine = document.querySelector('[data-cine]');
  let last = scrollY;
  const onScroll = () => {
    const y = scrollY;
    const max = document.documentElement.scrollHeight - innerHeight;
    if (progress) progress.style.setProperty('--p', max > 0 ? (y / max).toFixed(4) : 0);
    const menuOpen = document.querySelector('.menu-toggle[aria-expanded=true]');
    if (header && !menuOpen) header.classList.toggle('is-hidden', y > 240 && y > last + 2);
    if (header && y < last - 2) header.classList.remove('is-hidden');
    if (mobileCta) mobileCta.classList.toggle('is-shown', y > innerHeight * 0.6);
    if (header && cine) header.classList.toggle('is-solid', y > cine.offsetHeight - header.offsetHeight - 8);
    last = y;
    pin();
    if (full) frame();
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
    pinned.querySelectorAll('[data-pin-photo]').forEach((photo, index) => photo.classList.toggle('is-active', index === active));
    if (number) number.textContent = String(active + 1).padStart(2, '0');
  }
  if (pinned && !full) steps.forEach(step => step.classList.add('is-active'));

  // Photographs: masks open as they arrive, a horizontal story runs while its section is pinned,
  // and images drift a little against the scroll.
  const films = [...document.querySelectorAll('[data-film]')];
  const story = document.querySelector('[data-story]');
  const track = story && story.querySelector('[data-story-track]');
  const chapters = story ? story.querySelectorAll('[data-chapter]').length : 0;
  const storyNumber = story && story.querySelector('[data-story-number]');
  const storyBar = story && story.querySelector('[data-story-progress]');
  const drifting = [...document.querySelectorAll('[data-parallax]')];
  const clamp = value => Math.min(1, Math.max(0, value));
  const cineMedia = cine && cine.querySelector('[data-cine-media]');
  const cineCopy = cine && cine.querySelector('[data-cine-copy]');
  const pointer = {x: 0, y: 0, tx: 0, ty: 0};
  if (cine && full && matchMedia('(pointer: fine)').matches) {
    // A slow camera drift that follows the pointer.
    cine.addEventListener('pointermove', event => {
      pointer.tx = (event.clientX / innerWidth - 0.5) * -24;
      pointer.ty = (event.clientY / innerHeight - 0.5) * -16;
    });
    const ease = () => {
      pointer.x += (pointer.tx - pointer.x) * 0.06;
      pointer.y += (pointer.ty - pointer.y) * 0.06;
      if (Math.abs(pointer.tx - pointer.x) > 0.05 || Math.abs(pointer.ty - pointer.y) > 0.05) frame();
      requestAnimationFrame(ease);
    };
    requestAnimationFrame(ease);
  }
  const motes = cine && full && cine.querySelector('[data-motes]');
  if (motes) {
    // Warm embers rising through the evening light. Paused when the hero is off screen.
    const context = motes.getContext('2d');
    let width = 0, height = 0, visible = true, particles = [];
    const size = () => {
      const ratio = Math.min(2, devicePixelRatio || 1);
      width = motes.clientWidth; height = motes.clientHeight;
      motes.width = width * ratio; motes.height = height * ratio;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      const count = Math.round(Math.min(90, width * height / 16000));
      particles = Array.from({length: count}, () => spawn(true));
    };
    const spawn = anywhere => ({x: Math.random() * width, y: anywhere ? Math.random() * height : height + 10, r: 0.6 + Math.random() * 1.9,
      speed: 0.12 + Math.random() * 0.38, sway: Math.random() * Math.PI * 2, life: 0, max: 500 + Math.random() * 700});
    const draw = () => {
      if (visible && !document.hidden) {
        context.clearRect(0, 0, width, height);
        particles.forEach((dot, index) => {
          dot.life++; dot.y -= dot.speed; dot.sway += 0.01; dot.x += Math.sin(dot.sway) * 0.25;
          const fade = Math.min(1, dot.life / 90, (dot.max - dot.life) / 120);
          if (fade <= 0 || dot.y < -10) { particles[index] = spawn(false); return; }
          const glow = context.createRadialGradient(dot.x, dot.y, 0, dot.x, dot.y, dot.r * 4);
          glow.addColorStop(0, `rgba(255,214,160,${(0.85 * fade).toFixed(3)})`);
          glow.addColorStop(1, 'rgba(255,170,90,0)');
          context.fillStyle = glow;
          context.beginPath(); context.arc(dot.x, dot.y, dot.r * 4, 0, Math.PI * 2); context.fill();
        });
      }
      requestAnimationFrame(draw);
    };
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; }).observe(cine);
    addEventListener('resize', size);
    size();
    requestAnimationFrame(draw);
  }
  let queued = false;
  function frame() {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      const vh = innerHeight;
      films.forEach(film => {
        const top = film.getBoundingClientRect().top;
        film.style.setProperty('--f', clamp((top - vh * 0.08) / (vh * 0.75)).toFixed(3));
      });
      if (track) {
        const box = story.getBoundingClientRect();
        const p = clamp(-box.top / (box.height - vh));
        const distance = Math.max(0, track.scrollWidth - innerWidth);
        track.style.transform = `translate3d(${(-p * distance).toFixed(1)}px,0,0)`;
        if (storyBar) storyBar.style.width = (p * 100).toFixed(2) + '%';
        if (storyNumber) storyNumber.textContent = String(Math.min(chapters, 1 + Math.floor(p * chapters * 0.999))).padStart(2, '0');
      }
      if (cineMedia) {
        // The photograph sinks and slowly grows as you scroll away; the words lift and fade.
        const p = clamp(scrollY / cine.offsetHeight);
        cineMedia.style.transform = `translate3d(${pointer.x.toFixed(2)}px,${(p * 22 * vh / 100 + pointer.y).toFixed(2)}px,0) scale(${(1 + p * 0.08).toFixed(4)})`;
        if (p > 0) { cineCopy.style.opacity = String(Math.max(0, 1 - p * 1.6).toFixed(3)); cineCopy.style.transform = `translate3d(0,${(-p * 80).toFixed(1)}px,0)`; }
        else { cineCopy.style.opacity = ''; cineCopy.style.transform = ''; }
      }
      drifting.forEach(node => {
        const box = node.getBoundingClientRect();
        if (box.bottom < -200 || box.top > vh + 200) return;
        const offset = (box.top + box.height / 2 - vh / 2) / vh;
        node.style.setProperty('--py', (offset * -6).toFixed(2) + '%');
      });
    });
  }

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

})();
