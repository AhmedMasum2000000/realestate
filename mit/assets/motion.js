/* Move In Thailand: scroll motion. GSAP + ScrollTrigger, only for visitors who allow motion.
   Every effect starts from content that is already readable, so a failed script leaves a normal page. */
(() => {
  'use strict';
  const root = document.documentElement;

  /* Glass header: hides while scrolling down, returns on the first scroll up. */
  const header = document.querySelector('.header');
  if (header) {
    let last = window.scrollY, down = 0, up = 0, queued = false;
    const update = () => {
      queued = false;
      const y = window.scrollY;
      if (y > last) { down += y - last; up = 0; } else { up += last - y; down = 0; }
      last = y;
      header.classList.toggle('is-scrolled', y > 8);
      const menuOpen = header.querySelector('.navigation.is-open');
      if (y < 160 || up > 10 || menuOpen) header.classList.remove('is-hidden');
      else if (down > 14) header.classList.add('is-hidden');
    };
    addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, {passive: true});
    header.addEventListener('focusin', () => header.classList.remove('is-hidden'));
  }

  /* Pattaya local time in the hero corner label. */
  const clock = document.querySelector('[data-local-time]');
  if (clock && window.Intl) {
    const format = new Intl.DateTimeFormat('en-GB', {timeZone: 'Asia/Bangkok', hour: '2-digit', minute: '2-digit'});
    const tick = () => { clock.textContent = format.format(new Date()) + ' GMT+7'; };
    tick();
    setInterval(tick, 30000);
  }

  /* Cards: a soft brand glow follows the pointer. */
  document.querySelectorAll('.route-spec, .visa-card, .related-card').forEach(card => {
    card.classList.add('glow-card');
    card.addEventListener('pointermove', event => {
      const box = card.getBoundingClientRect();
      card.style.setProperty('--mx', (event.clientX - box.left) + 'px');
      card.style.setProperty('--my', (event.clientY - box.top) + 'px');
    });
  });

  const gsap = window.gsap, ScrollTrigger = window.ScrollTrigger;
  if (!root.classList.contains('motion-ok') || !gsap || !ScrollTrigger) { root.classList.remove('motion-ok'); return; }
  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.config({ignoreMobileResize: true});

  const hero = document.querySelector('[data-story-hero]');
  if (hero) storyHero(hero);
  reveals();
  statement(document.querySelector('[data-scramble]'));
  counters();

  /* ---------- Home hero: a pinned frame sequence driven by one master timeline. ---------- */
  function storyHero(hero) {
    const phone = matchMedia('(max-width: 700px)').matches;
    const count = Number(phone ? hero.dataset.countMobile : hero.dataset.countDesktop) || 0;
    const canvas = hero.querySelector('.story-canvas');
    const context = canvas && canvas.getContext('2d');
    if (!count || !context) return;

    // Slow or data-saving connections get every fourth frame, phones every second; the player blends between them.
    const connection = navigator.connection || {};
    const lite = connection.saveData || /(^|-)(2g|3g)$/.test(connection.effectiveType || '');
    const step = lite ? 4 : phone ? 2 : 1;
    const base = hero.dataset.frames + (phone ? 'mobile/' : 'desktop/');
    const images = new Array(count);
    const ready = new Uint8Array(count);
    let current = 0, drawQueued = false;

    const fit = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(canvas.clientWidth * ratio);
      canvas.height = Math.round(canvas.clientHeight * ratio);
      draw();
    };
    const cover = (image, alpha) => {
      const scale = Math.max(canvas.width / image.naturalWidth, canvas.height / image.naturalHeight);
      const width = image.naturalWidth * scale, height = image.naturalHeight * scale;
      context.globalAlpha = alpha;
      context.drawImage(image, (canvas.width - width) / 2, (canvas.height - height) / 2, width, height);
    };
    const nearest = (index, direction) => {
      for (let i = index; i >= 0 && i < count; i += direction) if (ready[i]) return i;
      return -1;
    };
    function draw() {
      drawQueued = false;
      const frame = Math.max(0, Math.min(count - 1, current));
      let a = nearest(Math.floor(frame), -1), b = nearest(Math.ceil(frame), 1);
      if (a < 0) a = b;
      if (b < 0) b = a;
      if (a < 0) return;
      cover(images[a], 1);
      if (b !== a) {
        const t = (frame - a) / (b - a);
        if (t > 0.002) cover(images[b], t);
      }
      context.globalAlpha = 1;
      canvas.classList.add('is-ready');
    }
    const requestDraw = () => { if (!drawQueued) { drawQueued = true; requestAnimationFrame(draw); } };

    // Load frame 1 at once (it is the poster), then coarse to fine so scrubbing works early.
    const order = [], seen = new Set();
    const add = index => { if (index >= 0 && index < count && !seen.has(index)) { seen.add(index); order.push(index); } };
    add(0); add(count - 1);
    for (let gap = 16; gap >= step; gap /= 2) for (let i = 0; i < count; i += gap) add(i);
    const load = index => new Promise(done => {
      const image = new Image();
      image.decoding = 'async';
      image.onload = () => { images[index] = image; ready[index] = 1; if (Math.abs(index - current) <= step * 2 || index === 0) requestDraw(); done(); };
      image.onerror = done;
      image.src = base + String(index + 1).padStart(3, '0') + '.webp';
    });
    const queue = order.slice(1);
    const worker = async () => { while (queue.length) await load(queue.shift()); };
    load(order[0]).then(() => {
      const start = () => { for (let i = 0; i < 4; i++) worker(); };
      if (document.readyState === 'complete') setTimeout(start, 300);
      else addEventListener('load', () => setTimeout(start, 300), {once: true});
    });

    const scenes = ['The coast', 'The culture', 'The city', 'Your home'];
    const sceneNumber = hero.querySelector('[data-scene-number]');
    const sceneName = hero.querySelector('[data-scene-name]');
    const meter = hero.querySelector('[data-story-meter]');
    let scene = -1;
    const showScene = () => {
      const next = Math.min(scenes.length - 1, Math.floor((current / count) * scenes.length));
      if (next === scene) return;
      scene = next;
      sceneNumber.textContent = String(next + 1).padStart(2, '0');
      sceneName.textContent = scenes[next];
    };

    const lines = hero.querySelectorAll('.story-line');
    const taglines = hero.querySelectorAll('[data-tagline]');
    const state = {frame: 0};
    const timeline = gsap.timeline({
      defaults: {ease: 'none'},
      scrollTrigger: {
        trigger: hero,
        start: 'top top',
        end: () => '+=' + Math.round(innerHeight * (phone ? 2.6 : 3.2)),
        pin: true,
        scrub: 0.5,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: self => { meter.style.transform = 'scaleX(' + self.progress.toFixed(3) + ')'; }
      }
    });
    timeline
      .to(state, {frame: count - 1, duration: 10, onUpdate: () => { current = state.frame; requestDraw(); showScene(); }}, 0)
      // Intro exits: each headline line leaves in its own direction.
      // Explicit start values: the CSS load-in may still be running when the timeline is built.
      .fromTo(hero.querySelector('.story-brand'), {y: 0, autoAlpha: 1}, {y: -40, autoAlpha: 0, duration: 0.9, ease: 'power1.in', immediateRender: false}, 0.05)
      .fromTo(hero.querySelector('.story-intro-meta'), {y: 0, autoAlpha: 1}, {y: 50, autoAlpha: 0, duration: 0.9, ease: 'power1.in', immediateRender: false}, 0.05)
      .fromTo(lines[0], {x: 0, autoAlpha: 1}, {x: () => -innerWidth * 0.75, autoAlpha: 0, duration: 1.7, ease: 'power2.in', immediateRender: false}, 0.2)
      .fromTo(lines[1], {scale: 1, autoAlpha: 1}, {scale: 2.6, autoAlpha: 0, duration: 1.7, ease: 'power2.in', immediateRender: false}, 0.2)
      .fromTo(lines[2], {x: 0, autoAlpha: 1}, {x: () => innerWidth * 0.75, autoAlpha: 0, duration: 1.7, ease: 'power2.in', immediateRender: false}, 0.2)
      // Mid-story taglines over the culture and city scenes.
      .fromTo(taglines[0], {autoAlpha: 0, y: 40}, {autoAlpha: 1, y: 0, duration: 0.9, ease: 'power2.out'}, 2.3)
      .to(taglines[0], {autoAlpha: 0, y: -40, duration: 0.8, ease: 'power2.in'}, 4.0)
      .fromTo(taglines[1], {autoAlpha: 0, y: 40}, {autoAlpha: 1, y: 0, duration: 0.9, ease: 'power2.out'}, 4.9)
      .to(taglines[1], {autoAlpha: 0, y: -40, duration: 0.8, ease: 'power2.in'}, 6.6)
      // The final frame: details either side of the home, then hold before unpinning.
      .to(hero.querySelector('.story-dim'), {opacity: 0.3, duration: 1.2}, 7.6)
      .fromTo(hero.querySelector('.story-end-left'), {autoAlpha: 0, x: -80}, {autoAlpha: 1, x: 0, duration: 1.3, ease: 'power3.out'}, 8.0)
      .fromTo(hero.querySelector('.story-end-right'), {autoAlpha: 0, x: 80}, {autoAlpha: 1, x: 0, duration: 1.3, ease: 'power3.out'}, 8.25)
      .to({}, {duration: 1.4});

    fit();
    let resizeTimer;
    addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(fit, 120); });
  }

  /* ---------- Every section: staggered entrance as it scrolls into view. ---------- */
  function reveals() {
    const selector = ['.section-heading', '.promise-strip p', '.intent-card', '.route-spec', '.story-grid > *', '.service-card',
      '.finder-feature-grid > *', '.process-grid > li', '.tool-card', '.faq-layout > *', '.closing-inner > *', '.visa-card',
      '.related-card', '.article-body > section', '.sidebar-card', '.number-list > li', '.section-footnote', '.download-block',
      '.fee-table', '.page-hero > *', '.stat', '.editorial-photo'].join(',');
    // Content already on screen is left alone, so nothing visible ever blinks out.
    const targets = gsap.utils.toArray(selector).filter(el => !el.closest('[data-story-hero]') && el.getBoundingClientRect().top > innerHeight * 0.92);
    if (!targets.length) return;
    gsap.set(targets, {opacity: 0, y: 34});
    targets.forEach(el => { const bar = el.matches('.route-spec') && el.querySelector('.spec-bar i'); if (bar) gsap.set(bar, {scaleX: 0}); });
    ScrollTrigger.batch(targets, {
      start: 'top 90%',
      once: true,
      onEnter: batch => {
        gsap.to(batch, {opacity: 1, y: 0, duration: 0.9, ease: 'power3.out', stagger: 0.09, overwrite: true});
        batch.forEach((el, index) => {
          const bar = el.matches('.route-spec') && el.querySelector('.spec-bar i');
          if (bar) gsap.to(bar, {scaleX: 1, duration: 1.4, delay: 0.35 + index * 0.09, ease: 'power2.out'});
        });
      }
    });
  }

  /* ---------- Statement: letters resolve from scrambled glyphs, one after another. ---------- */
  function statement(el) {
    if (!el || el.getBoundingClientRect().top < innerHeight * 0.9) return;
    const spoken = document.createElement('span');
    spoken.className = 'visually-hidden';
    spoken.textContent = el.textContent.replace(/\s+/g, ' ').trim();
    const chars = [];
    el.querySelectorAll('.statement-a, .statement-b').forEach(part => {
      const words = part.textContent.trim().split(/\s+/);
      part.textContent = '';
      part.setAttribute('aria-hidden', 'true');
      words.forEach((word, index) => {
        const wrap = document.createElement('span');
        wrap.className = 'word';
        for (const letter of word) {
          const char = document.createElement('span');
          char.className = 'char';
          char.dataset.char = letter;
          char.textContent = letter;
          char.style.opacity = '0';
          wrap.appendChild(char);
          chars.push(char);
        }
        part.appendChild(wrap);
        if (index < words.length - 1) part.appendChild(document.createTextNode(' '));
      });
    });
    el.prepend(spoken);
    const glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789฿';
    ScrollTrigger.create({
      trigger: el,
      start: 'top 82%',
      once: true,
      onEnter: () => chars.forEach((char, index) => {
        setTimeout(() => {
          char.style.opacity = '1';
          let turns = 0;
          const timer = setInterval(() => {
            if (++turns > 6) { char.textContent = char.dataset.char; char.classList.add('is-set'); clearInterval(timer); }
            else char.textContent = glyphs[Math.floor(Math.random() * glyphs.length)];
          }, 42);
        }, index * 26);
      })
    });
  }

  /* ---------- Stats: count up from zero when the strip comes into view. ---------- */
  function counters() {
    document.querySelectorAll('[data-count]').forEach(el => {
      if (el.getBoundingClientRect().top < innerHeight * 0.95) return;
      const target = Number(el.dataset.count);
      const value = {n: 0};
      el.textContent = '0';
      ScrollTrigger.create({
        trigger: el,
        start: 'top 88%',
        once: true,
        onEnter: () => gsap.to(value, {n: target, duration: 1.6, ease: 'power2.out', onUpdate: () => { el.textContent = String(Math.round(value.n)); }})
      });
    });
  }
})();
