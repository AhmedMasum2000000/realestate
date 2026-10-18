/* The Second Home Plan proposal: an email or phone number opens the plan. Remembered in local storage only. */
(() => {
  'use strict';
  const root = document.querySelector('[data-proposal]');
  if (!root) return;
  const KEY = 'sht-proposal';
  const store = {
    get() { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (error) { return null; } },
    set(value) { try { localStorage.setItem(KEY, JSON.stringify(value)); } catch (error) { /* private mode */ } }
  };
  const config = (() => { try { return JSON.parse(document.getElementById('sht-config').textContent); } catch (error) { return {}; } })();
  const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const body = root.querySelector('[data-proposal-body]');
  const gate = root.querySelector('[data-proposal-gate]');
  const form = document.getElementById('proposal-form');
  const status = document.getElementById('pp-status');

  const name = text => {
    const clean = (text || '').trim().split(/\s+/)[0];
    if (clean) root.querySelectorAll('[data-name]').forEach(el => { el.textContent = clean; });
  };
  let opened = false;
  const open = (target, fromSubmit) => {
    if (!opened) {
      opened = true;
      body.hidden = false;
      root.classList.add('is-open');
      animate();
    }
    const to = document.querySelector(target || '#dream');
    if (to && fromSubmit !== false) to.scrollIntoView({behavior: reduce ? 'auto' : 'smooth', block: 'start'});
  };

  // Links to chapters open the gate first while the plan is closed.
  root.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || opened) return;
    event.preventDefault();
    gate.scrollIntoView({behavior: reduce ? 'auto' : 'smooth', block: 'center'});
    document.getElementById('pp-contact').focus({preventScroll: true});
  });

  const saved = store.get();
  if (saved) { name(saved.name); open(null, false); }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    status.className = 'pp-status'; status.textContent = '';
    const contact = form.elements.contact.value.trim();
    const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(contact);
    const isPhone = /^\+?[0-9][0-9 ().-]{6,24}$/.test(contact) && contact.replace(/\D/g, '').length >= 7;
    if (!isEmail && !isPhone) { status.className = 'pp-status error'; status.textContent = 'Please add an email address, or a phone number starting with your country code.'; form.elements.contact.focus(); return; }
    if (!form.elements.consent.checked) { status.className = 'pp-status error'; status.textContent = 'Please tick the box so we may contact you about this plan.'; form.elements.consent.focus(); return; }
    const reader = {name: form.elements.name.value.trim().slice(0, 120)};
    if (config.preview) { store.set(reader); name(reader.name); open(); return; }
    const button = form.querySelector('[type=submit]'); button.disabled = true;
    status.textContent = 'Opening your plan…';
    try {
      const api = (config.apiBase || '/wp-json/sht/v1/').replace(/\/?$/, '/');
      const boot = await fetch(api + 'bootstrap', {credentials: 'same-origin', cache: 'no-store', headers: {Accept: 'application/json'}});
      const auth = await boot.json();
      if (!boot.ok || !auth.token) throw new Error('We could not start the secure form. Please reload the page and try again.');
      const requestId = window.crypto && crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
      const response = await fetch(api + 'proposal-leads', {method: 'POST', credentials: 'same-origin', headers: {'Content-Type': 'application/json', Accept: 'application/json'},
        body: JSON.stringify({token: auth.token, request_id: requestId, name: reader.name, contact, consent: true, website: form.elements.website.value})});
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.saved) throw new Error(result.message || 'Your details could not be saved. Please try again.');
      store.set(reader); name(reader.name);
      status.textContent = '';
      open();
    } catch (error) {
      status.className = 'pp-status error';
      status.textContent = error.message === 'Failed to fetch' ? 'We could not connect. Please check your connection and try again.' : error.message;
    } finally { button.disabled = false; }
  });

  // Gentle reveals and the ticking offer list, once the plan is open.
  function animate() {
    const ticks = root.querySelectorAll('[data-ticks] li');
    if (reduce || !('IntersectionObserver' in window)) { ticks.forEach(li => li.classList.add('on')); return; }
    root.classList.add('motion');
    const io = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); } }), {rootMargin: '0px 0px -8% 0px'});
    root.querySelectorAll('.rv').forEach(el => io.observe(el));
    setTimeout(() => root.querySelectorAll('.rv').forEach(el => el.classList.add('in')), 4000);
    const t = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const i = [].indexOf.call(ticks, entry.target);
      setTimeout(() => entry.target.classList.add('on'), 120 + i * 40);
      t.unobserve(entry.target);
    }), {rootMargin: '0px 0px -15% 0px'});
    ticks.forEach(li => t.observe(li));
  }
})();
