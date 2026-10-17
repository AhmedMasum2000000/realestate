/* Khun Boon, the concierge. A welcome note on the home page, a helper beside the consultation form and
   the Visa Finder, and a 90-day report date keeper. Remembered in local storage, never in a cookie. */
(() => {
  'use strict';
  const store = {
    get(key) { try { return localStorage.getItem(key); } catch (error) { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch (error) { /* private mode */ } },
    remove(key) { try { localStorage.removeItem(key); } catch (error) { /* private mode */ } }
  };
  const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Switch the visible pose inside a figure that holds several.
  const pose = (figure, name) => {
    if (!figure) return;
    figure.querySelectorAll('.boon-pose').forEach(svg => svg.classList.toggle('is-on', svg.classList.contains('boon-' + name)));
  };

  // Welcome note: once a month, a few seconds after the hero has settled.
  const note = document.getElementById('boon-note');
  if (note) {
    const KEY = 'sht-boon-note';
    const MONTH = 30 * 24 * 60 * 60 * 1000;
    if (Date.now() - (Number(store.get(KEY)) || 0) > MONTH) {
      const part = name => note.querySelector('[data-boon-' + name + ']');
      const figure = part('figure');
      let closed = false;
      const onKey = event => { if (event.key === 'Escape') close(); };
      const open = () => {
        if (closed) return;
        note.hidden = false;
        requestAnimationFrame(() => note.classList.add('is-in'));
        document.addEventListener('keydown', onKey);
      };
      function close() {
        if (closed) return;
        closed = true;
        store.set(KEY, String(Date.now()));
        document.removeEventListener('keydown', onKey);
        note.classList.remove('is-in');
        setTimeout(() => { note.hidden = true; }, reduce ? 0 : 500);
      }
      const say = (title, text) => { part('title').textContent = title; part('text').textContent = text; part('actions').hidden = true; };
      part('yes').addEventListener('click', () => {
        store.set(KEY, String(Date.now()));
        pose(figure, 'offering');
        say('Please, help yourself.', 'Khanom maphrao, a little coconut sweet. Now, shall we find the residency route that fits you?');
        setTimeout(() => pose(figure, 'success'), reduce ? 0 : 1600);
        const next = part('next');
        next.hidden = false;
        next.focus({preventScroll: true});
      });
      part('no').addEventListener('click', () => {
        store.set(KEY, String(Date.now()));
        pose(figure, 'goodbye');
        note.classList.add('is-waving');
        say('Of course.', 'I’ll be here if you need me.');
        note.querySelector('[data-boon-close]').focus({preventScroll: true});
        setTimeout(close, 3200);
      });
      part('next').addEventListener('click', () => store.set(KEY, String(Date.now())));
      part('close').addEventListener('click', close);
      setTimeout(open, 6000);
    }
  }

  // Consultation form helper: one calm sentence for the field in hand.
  const helper = document.querySelector('[data-boon-helper]');
  const form = document.getElementById('move-enquiry');
  if (helper && form) {
    const figure = helper.querySelector('[data-boon-figure]');
    const bubble = helper.querySelector('[data-boon-say]');
    const tips = {
      name: 'Just the name you would like us to use.',
      email: 'We reply by email first. It stays in our private enquiry desk.',
      phone: 'Optional. Include your country code if you would like a call or a message.',
      interest: 'Choose the closest. We will cover the rest when we talk.',
      timeline: 'An approximate time is perfectly fine.',
      budget: 'Optional. A rough monthly figure helps us suggest the right areas.',
      message: 'Who is moving, and what feels uncertain? Please leave out passport and bank details.',
      consent: 'This only allows us to answer you. Updates are a separate, optional choice.'
    };
    form.addEventListener('focusin', event => {
      const tip = tips[event.target.name];
      if (!tip) return;
      pose(figure, 'notes');
      bubble.textContent = tip;
    });
    const status = document.getElementById('enquiry-status');
    if (status) new MutationObserver(() => {
      if (status.classList.contains('success')) { pose(figure, 'success'); bubble.textContent = 'Noted, with thanks. We will be in touch to arrange a time that suits you.'; }
      else if (status.classList.contains('error')) { pose(figure, 'puzzled'); bubble.textContent = 'Something did not go through. Your details are still here, so please try once more.'; }
    }).observe(status, {attributes: true, attributeFilter: ['class']});
  }

  // Visa Finder guide: follows the questions and greets the shortlist.
  const finderHelper = document.querySelector('[data-boon-finder]');
  const quizStep = document.getElementById('quiz-step');
  if (finderHelper && quizStep) {
    const figure = finderHelper.querySelector('[data-boon-figure]');
    const bubble = finderHelper.querySelector('[data-boon-say]');
    const lines = ['Four questions, about two minutes. Shall we find your starting point?', 'Noted. Two more after this one.', 'Very good. Nearly there.', 'Last one. Then I will show you the routes worth a closer look.'];
    new MutationObserver(() => {
      const text = quizStep.textContent;
      if (/RESULTS/i.test(text)) { pose(figure, 'success'); bubble.textContent = 'Here is your starting shortlist. Bring it to a consultation and we will check the details together.'; return; }
      const step = parseInt(text, 10) || 1;
      pose(figure, step === 1 ? 'guide' : 'notes');
      bubble.textContent = lines[Math.min(lines.length - 1, step - 1)];
    }).observe(quizStep, {childList: true, characterData: true, subtree: true});
  }

  // 90-day report date keeper. The date entered counts as day one, so the result errs early.
  const DAY = 24 * 60 * 60 * 1000;
  const parse = value => { const [y, m, d] = String(value).split('-').map(Number); return y && m && d ? Date.UTC(y, m - 1, d) : NaN; };
  const iso = time => new Date(time).toISOString().slice(0, 10);
  const long = time => new Date(time).toLocaleDateString('en-GB', {weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'});
  const short = time => new Date(time).toLocaleDateString('en-GB', {day: 'numeric', month: 'long', timeZone: 'UTC'});
  const ics = (start, due, close) => {
    const stamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z';
    const event = (time, title, text) => ['BEGIN:VEVENT', 'UID:' + iso(time) + '-' + title.length + '@secondhomethailand.com', 'DTSTAMP:' + stamp,
      'DTSTART;VALUE=DATE:' + iso(time).replace(/-/g, ''), 'DTEND;VALUE=DATE:' + iso(time + DAY).replace(/-/g, ''), 'SUMMARY:' + title, 'DESCRIPTION:' + text,
      'BEGIN:VALARM', 'TRIGGER:-PT9H', 'ACTION:DISPLAY', 'DESCRIPTION:' + title, 'END:VALARM', 'END:VEVENT'];
    return ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Second Home Thailand//Date keeper//EN',
      ...event(start, 'Thai 90-day report: filing opens', 'Your 90-day report can be filed from today. Due ' + long(due) + '.'),
      ...event(due, 'Thai 90-day report due', 'Your 90-day report is due today. Check the date on your immigration receipt.'),
      'END:VCALENDAR'].join('\r\n');
  };
  document.querySelectorAll('[data-reminder]').forEach(tool => {
    const input = tool.elements.date;
    const result = tool.querySelector('[data-reminder-result]');
    const KEY = 'sht-90-day';
    const show = value => {
      const start = parse(value);
      if (!Number.isFinite(start)) { result.hidden = false; result.innerHTML = '<p class="reminder-error">Please choose a date.</p>'; return; }
      const due = start + 89 * DAY, opens = due - 15 * DAY, closes = due + 7 * DAY;
      const remembered = store.get(KEY) === value;
      result.hidden = false;
      result.innerHTML = '<p class="mono">Your next report</p><p class="reminder-date">' + long(due) + '</p>' +
        '<p>Filing window, as set out in our guide: ' + short(opens) + ' to ' + short(closes) + '.</p>' +
        '<div class="reminder-actions"><button type="button" class="text-arrow" data-reminder-ics>Add to my calendar</button>' +
        '<label class="check"><input type="checkbox" data-reminder-keep' + (remembered ? ' checked' : '') + '><span>Remember this date in this browser</span></label></div>';
      result.querySelector('[data-reminder-ics]').addEventListener('click', () => {
        const url = URL.createObjectURL(new Blob([ics(opens, due, closes)], {type: 'text/calendar;charset=utf-8'}));
        const anchor = document.createElement('a');
        anchor.href = url; anchor.download = 'thai-90-day-report.ics';
        document.body.append(anchor); anchor.click(); anchor.remove();
        setTimeout(() => URL.revokeObjectURL(url), 5000);
      });
      result.querySelector('[data-reminder-keep]').addEventListener('change', event => { if (event.target.checked) store.set(KEY, value); else store.remove(KEY); });
    };
    tool.addEventListener('submit', event => { event.preventDefault(); show(input.value); });
    const saved = store.get(KEY);
    if (saved) { input.value = saved; show(saved); }
  });
})();

/* Homes: a shortlist kept in this browser, and filters on the main listings page. */
(() => {
  'use strict';
  const KEY = 'sht-shortlist';
  const read = () => { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (error) { return []; } };
  const write = list => { try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (error) { /* private mode */ } };
  const bar = document.querySelector('[data-shortlist-bar]');
  const sync = () => {
    const list = read();
    document.querySelectorAll('[data-save]').forEach(button => {
      const saved = list.includes(button.dataset.save);
      button.setAttribute('aria-pressed', String(saved));
      if (!button.classList.contains('home-save')) button.textContent = saved ? 'Saved to shortlist' : 'Save to shortlist';
    });
    if (bar) {
      bar.hidden = !list.length;
      bar.querySelector('[data-shortlist-count]').textContent = list.length;
      const plan = 'My shortlist: ' + list.join(', ') + '. Please check availability and arrange viewings.';
      bar.querySelector('[data-shortlist-send]').href = '/contact/?interest=homes&plan=' + encodeURIComponent(plan);
    }
  };
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-save]');
    if (!button) return;
    const list = read();
    const ref = button.dataset.save;
    write(list.includes(ref) ? list.filter(item => item !== ref) : list.concat(ref).slice(-30));
    sync();
    if (filterForm) apply();
  });
  const filterForm = document.querySelector('[data-home-filter]');
  const grid = document.querySelector('[data-home-grid]');
  function apply() {
    if (!filterForm || !grid) return;
    const f = new FormData(filterForm);
    const list = read();
    const cards = [...grid.querySelectorAll('[data-home]')];
    let shown = 0;
    cards.forEach(card => {
      const d = card.dataset;
      const ok = (!f.get('deal') || d.deal === f.get('deal')) && (!f.get('type') || d.type === f.get('type')) && (!f.get('area') || d.area === f.get('area')) &&
        (!f.get('beds') || (d.beds !== '' && Number(d.beds) >= Number(f.get('beds')))) && (!f.get('saved') || list.includes(d.ref));
      card.hidden = !ok;
      if (ok) shown++;
    });
    const sort = f.get('sort');
    if (sort !== 'new' || grid.dataset.sorted) {
      const order = cards.slice().sort((a, b) => sort === 'low' ? a.dataset.price - b.dataset.price : sort === 'high' ? b.dataset.price - a.dataset.price : Number(a.dataset.index) - Number(b.dataset.index));
      order.forEach(card => grid.appendChild(card));
      grid.dataset.sorted = '1';
    }
    filterForm.querySelector('[data-home-count]').textContent = shown + (shown === 1 ? ' home' : ' homes');
    const params = new URLSearchParams();
    for (const [key, value] of f) if (value && !(key === 'sort' && value === 'new')) params.set(key, value);
    history.replaceState(null, '', params.toString() ? '?' + params : location.pathname);
  }
  if (filterForm && grid) {
    grid.querySelectorAll('[data-home]').forEach((card, index) => { card.dataset.index = index; });
    const params = new URLSearchParams(location.search);
    for (const [key, value] of params) { const field = filterForm.elements[key]; if (field) { if (field.type === 'checkbox') field.checked = true; else field.value = value; } }
    filterForm.addEventListener('change', apply);
    filterForm.addEventListener('submit', event => event.preventDefault());
    apply();
  }
  sync();
})();
