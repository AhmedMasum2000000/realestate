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

  const gsap = window.gsap, ScrollTrigger = window.ScrollTrigger, SplitText = window.SplitText;
  if (!root.classList.contains('motion-ok') || !gsap || !ScrollTrigger) { root.classList.remove('motion-ok'); return; }
  gsap.registerPlugin(ScrollTrigger);
  if (SplitText) gsap.registerPlugin(SplitText);
  ScrollTrigger.config({ignoreMobileResize: true});
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const desktop = matchMedia('(min-width: 901px)').matches;

  /* Smooth scrolling for mouse and trackpad, driven by GSAP's ticker so ScrollTrigger stays in step.
     Touch screens keep their native scrolling. */
  let lenis = null;
  if (finePointer && window.Lenis) {
    lenis = new window.Lenis({lerp: 0.11, anchors: {offset: -100}});
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(time => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  const hero = document.querySelector('[data-story-hero]');
  if (hero) storyHero(hero);
  headings();
  const processDrawn = desktop && processLine();
  reveals();
  images();
  statement(document.querySelector('[data-scramble]'));
  counters();
  marquee();
  wordmark();
  readingProgress();
  if (finePointer) { cursor(); magnetic(); tilt(); }

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
        scrub: lenis ? true : 0.5,
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

    // Depth: the headline drifts with the pointer while the scene shifts the other way.
    if (finePointer) {
      const intro = hero.querySelector('.story-intro');
      const ease = {duration: 1.1, ease: 'power3'};
      const introX = gsap.quickTo(intro, 'x', ease), introY = gsap.quickTo(intro, 'y', ease);
      const sceneX = gsap.quickTo(canvas, 'x', ease), sceneY = gsap.quickTo(canvas, 'y', ease);
      gsap.set(canvas, {scale: 1.05});
      hero.addEventListener('pointermove', event => {
        const nx = event.clientX / innerWidth - 0.5, ny = event.clientY / innerHeight - 0.5;
        introX(nx * 22); introY(ny * 14); sceneX(nx * -16); sceneY(ny * -10);
      });
      hero.addEventListener('pointerleave', () => { introX(0); introY(0); sceneX(0); sceneY(0); });
    }

    fit();
    let resizeTimer;
    addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(fit, 120); });
  }

  /* ---------- Every section: staggered entrance as it scrolls into view. ---------- */
  function reveals() {
    // Headings, photos and the process steps have their own entrances; these are the blocks around them.
    const selector = ['.section-heading .eyebrow', '.section-heading > p', '.section-heading > .text-link', '.promise-strip p',
      '.intent-card', '.route-spec', '.story-copy > :not(h2)', '.service-card', '.finder-preview',
      '.finder-feature-grid > div > :not(h2)', processDrawn ? '' : '.process-grid > li', '.tool-card', '.faq-layout > :last-child',
      '.faq-layout > :first-child > :not(h2)', '.closing-inner > *', '.visa-card', '.related-card', '.article-body > section > :not(h2)',
      '.sidebar-card', '.section-footnote', '.download-block > :not(h2)', '.page-hero > *', '.stat', '.marquee'].filter(Boolean).join(',');
    // Content already on screen is left alone, so nothing visible ever blinks out.
    const targets = gsap.utils.toArray(selector).filter(el => !el.closest('[data-story-hero]') && el.getBoundingClientRect().top > innerHeight * 0.92);
    if (!targets.length) return;
    gsap.set(targets, {opacity: 0, y: 30});
    targets.forEach(el => { const bar = el.matches('.route-spec') && el.querySelector('.spec-bar i'); if (bar) gsap.set(bar, {scaleX: 0}); });
    ScrollTrigger.batch(targets, {
      start: 'top 90%',
      once: true,
      onEnter: batch => {
        gsap.to(batch, {opacity: 1, y: 0, duration: 1, ease: 'expo.out', stagger: 0.08, overwrite: 'auto'});
        batch.forEach((el, index) => {
          const bar = el.matches('.route-spec') && el.querySelector('.spec-bar i');
          if (bar) gsap.to(bar, {scaleX: 1, duration: 1.4, delay: 0.35 + index * 0.09, ease: 'power2.out'});
        });
      }
    });
  }

  /* ---------- Headlines: each line rises from behind its own mask. ---------- */
  function headings() {
    const selector = ['.section-heading h2', '.story-copy h2', '.finder-feature-grid h2', '.faq-layout h2', '.page-hero h1',
      '.page-hero-note h2', '.tool-intro h1', '.article-body > section > h2', '.download-block h2', '.contact-note h2'].join(',');
    document.querySelectorAll(selector).forEach(el => {
      if (el.closest('[data-story-hero]')) return;
      const onScreen = el.getBoundingClientRect().top < innerHeight * 0.92;
      if (!SplitText) { gsap.set(el, {visibility: 'visible'}); return; }
      SplitText.create(el, {
        type: 'lines', mask: 'lines', linesClass: 'split-line', autoSplit: true,
        onSplit: self => {
          gsap.set(el, {visibility: 'visible'});
          return gsap.from(self.lines, {
            yPercent: 110, duration: 1.15, ease: 'expo.out', stagger: 0.09, delay: onScreen ? 0.1 : 0,
            ...(onScreen ? {} : {scrollTrigger: {trigger: el, start: 'top 88%', once: true}})
          });
        }
      });
    });
  }

  /* ---------- Photos: a wipe from below, the image settling inside it, then a slow parallax. ---------- */
  function images() {
    gsap.utils.toArray('.story-image, .editorial-photo, .contact-photo').forEach(frame => {
      const img = frame.querySelector('img');
      if (!img) return;
      const onScreen = frame.getBoundingClientRect().top < innerHeight * 0.92;
      const when = onScreen ? {delay: 0.05} : {scrollTrigger: {trigger: frame, start: 'top 85%', once: true}};
      gsap.set(img, {scale: 1.12});
      gsap.fromTo(frame, {clipPath: 'inset(100% 0% 0% 0%)'}, {clipPath: 'inset(0% 0% 0% 0%)', duration: onScreen ? 1.1 : 1.4, ease: onScreen ? 'expo.out' : 'expo.inOut', ...when});
      gsap.from(img, {scale: 1.45, duration: 2, ease: 'expo.out', ...when});
      gsap.fromTo(img, {yPercent: -5}, {yPercent: 5, ease: 'none', scrollTrigger: {trigger: frame, start: 'top bottom', end: 'bottom top', scrub: true}});
    });
  }

  /* ---------- Process: a line draws through the four steps and lights each one as it passes. ---------- */
  function processLine() {
    const grid = document.querySelector('.process-grid');
    if (!grid) return false;
    const steps = grid.querySelectorAll(':scope > li');
    grid.classList.add('is-drawn');
    gsap.set(steps, {opacity: 0.22, y: 26});
    const timeline = gsap.timeline({scrollTrigger: {trigger: grid, start: 'top 85%', end: 'top 35%', scrub: 0.6}});
    timeline.fromTo(grid, {'--p': 0}, {'--p': 1, ease: 'none', duration: steps.length}, 0);
    steps.forEach((step, index) => timeline.to(step, {opacity: 1, y: 0, duration: 0.7, ease: 'power2.out'}, index + 0.1));
    return true;
  }

  /* ---------- Marquee: a steady drift that speeds up, reverses and leans with the scroll. ---------- */
  function marquee() {
    document.querySelectorAll('[data-marquee]').forEach(band => {
      const track = band.querySelector('.marquee-track');
      const loop = gsap.to(track, {xPercent: -50, duration: 40, ease: 'none', repeat: -1});
      loop.totalTime(loop.duration() * 500);   // room to run backwards when the visitor scrolls up
      let boost = 0, direction = 1, lean = 0;
      const trigger = ScrollTrigger.create({
        trigger: band, start: 'top bottom', end: 'bottom top',
        onUpdate: self => {
          const velocity = self.getVelocity();
          direction = self.direction;
          boost = Math.min(Math.abs(velocity) / 260, 7);
          lean = gsap.utils.clamp(-6, 6, -velocity / 380);
        }
      });
      gsap.ticker.add(() => {
        if (!trigger.isActive && boost < 0.01) return;
        boost *= 0.92; lean *= 0.88;
        loop.timeScale(direction * (1 + boost));
        gsap.set(track, {skewX: lean});
      });
    });
  }

  /* ---------- Footer wordmark: letters rise in, and lift as the pointer passes over them. ---------- */
  function wordmark() {
    const mark = document.querySelector('.footer-wordmark');
    if (!mark || !SplitText) return;
    const split = SplitText.create(mark, {type: 'chars', charsClass: 'wm-char', aria: 'none'});
    gsap.from(split.chars, {yPercent: 105, duration: 1.2, ease: 'expo.out', stagger: 0.035, scrollTrigger: {trigger: mark, start: 'top 98%', once: true}});
    if (!finePointer) return;
    const lifts = split.chars.map(char => gsap.quickTo(char, 'y', {duration: 0.6, ease: 'power3'}));
    mark.addEventListener('pointermove', event => {
      split.chars.forEach((char, index) => {
        const box = char.getBoundingClientRect();
        const distance = Math.abs(event.clientX - (box.left + box.width / 2));
        lifts[index](-Math.max(0, 1 - distance / 240) * box.height * 0.16);
      });
    });
    mark.addEventListener('pointerleave', () => lifts.forEach(lift => lift(0)));
  }

  /* ---------- Guides: a thin progress line along the top of the window. ---------- */
  function readingProgress() {
    const article = document.querySelector('.article-body');
    if (!article) return;
    const bar = document.createElement('div');
    bar.className = 'read-progress';
    bar.setAttribute('aria-hidden', 'true');
    bar.appendChild(document.createElement('i'));
    document.body.appendChild(bar);
    gsap.fromTo(bar.firstChild, {scaleX: 0}, {scaleX: 1, ease: 'none', scrollTrigger: {trigger: article, start: 'top 25%', end: 'bottom 75%', scrub: true}});
  }

  /* ---------- Cursor: a trailing ring that grows over links and becomes a labelled disc over cards.
     The system cursor stays visible, so nothing about pointing changes. ---------- */
  function cursor() {
    const labels = [['.route-spec, .visa-card', 'Explore'], ['.related-card', 'Read'], ['.tool-card', 'Try it'], ['.intent-card', 'Start']];
    labels.forEach(([selector, text]) => document.querySelectorAll(selector).forEach(card => { card.dataset.cursor = text; }));
    const ring = document.createElement('div');
    const label = document.createElement('div');
    ring.className = 'cursor-ring';
    label.className = 'cursor-label';
    label.appendChild(document.createElement('span'));
    [ring, label].forEach(el => { el.setAttribute('aria-hidden', 'true'); document.body.appendChild(el); gsap.set(el, {xPercent: -50, yPercent: -50}); });
    const follow = (el, duration) => [gsap.quickTo(el, 'x', {duration, ease: 'power3'}), gsap.quickTo(el, 'y', {duration, ease: 'power3'})];
    const [ringX, ringY] = follow(ring, 0.45), [labelX, labelY] = follow(label, 0.6);
    const state = (name, on) => { ring.classList.toggle(name, on); label.classList.toggle(name, on); };
    addEventListener('pointermove', event => {
      if (event.pointerType !== 'mouse') return;
      ringX(event.clientX); ringY(event.clientY); labelX(event.clientX); labelY(event.clientY);
      root.classList.add('cursor-on');
    }, {passive: true});
    document.addEventListener('mouseleave', () => root.classList.remove('cursor-on'));
    addEventListener('pointerdown', () => state('is-down', true));
    addEventListener('pointerup', () => state('is-down', false));
    document.addEventListener('pointerover', event => {
      const card = event.target.closest('[data-cursor]');
      const typing = event.target.closest('input, textarea, select, [contenteditable]');
      const link = event.target.closest('a, button, summary, label');
      if (card) label.firstChild.textContent = card.dataset.cursor;
      state('is-card', !!card);
      state('is-text', !!typing);
      state('is-link', !card && !typing && !!link);
    });
  }

  /* ---------- Buttons lean toward the pointer and spring back when it leaves. ---------- */
  function magnetic() {
    document.querySelectorAll('.button').forEach(button => {
      const ease = {duration: 0.6, ease: 'power3'};
      const moveX = gsap.quickTo(button, 'x', ease), moveY = gsap.quickTo(button, 'y', ease);
      button.addEventListener('pointermove', event => {
        const box = button.getBoundingClientRect();
        if (box.width > 320) return;            // full-width buttons stay still
        moveX((event.clientX - box.left - box.width / 2) * 0.28);
        moveY((event.clientY - box.top - box.height / 2) * 0.4);
      });
      button.addEventListener('pointerleave', () => {
        gsap.to(button, {x: 0, y: 0, duration: 0.9, ease: 'elastic.out(1, 0.45)', overwrite: 'auto'});
      });
    });
  }

  /* ---------- Cards tilt a few degrees toward the pointer. ---------- */
  function tilt() {
    document.querySelectorAll('.route-spec, .tool-card, .visa-card').forEach(card => {
      gsap.set(card, {transformPerspective: 900});
      const ease = {duration: 0.7, ease: 'power3'};
      const turnX = gsap.quickTo(card, 'rotationX', ease), turnY = gsap.quickTo(card, 'rotationY', ease);
      card.addEventListener('pointermove', event => {
        const box = card.getBoundingClientRect();
        turnY(((event.clientX - box.left) / box.width - 0.5) * 7);
        turnX(-((event.clientY - box.top) / box.height - 0.5) * 7);
      });
      card.addEventListener('pointerleave', () => { turnX(0); turnY(0); });
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
