#!/usr/bin/env python3
"""Open the live Second Home Thailand site in a real browser and check it works.

    python tools/sht_live_check.py https://secondhomethailand.com/

For desktop, an iPhone profile and a reduced-motion visitor it reports the release served,
whether the page keeps a quiet pulse while idle, the pinned process steps, script errors,
cookies, sideways overflow, a few inner pages, and that the old template's pages are gone.
Screenshots go to .cache/live-check/. Exits non-zero if a check fails.
"""
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path('.cache/live-check')
INNER = ['visas/', 'visas/ltr/', 'stay-legal/90-day-report/', 'concierge/', 'contact/', 'library/', 'tools/visa-finder/']
GONE = ['author/bw9jc/']


def check(context, url, tag, problems):
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(url, wait_until='load', timeout=90000)
    time.sleep(3)
    page.screenshot(path=str(OUT / f'sht-{tag}-intro.png'))
    release = page.evaluate("(document.querySelector('link[href*=\"site.css\"]') || {}).href || ''").split('v=')[-1]
    snap = "(() => ({clock: (document.querySelector('[data-local-time]') || {}).textContent, running: document.getAnimations().filter(a => a.playState === 'running').length}))()"
    before = page.evaluate(snap)
    time.sleep(2.5)
    after = page.evaluate(snap)
    boon = page.evaluate("(() => { const n = document.getElementById('boon-note'); return n ? {shown: !n.hidden, poses: n.querySelectorAll('svg.boon').length} : null })()")
    print(f'{tag}: khun_boon_note={boon}')
    if not boon or boon['poses'] != 4:
        problems.append(f'{tag}: Khun Boon welcome note missing ({boon})')
    hero = page.evaluate("(() => { const h = document.querySelector('.cine h1'); const c = document.querySelector('.cine-copy'); return {title: h ? h.textContent.replace(/\\s+/g, ' ').trim() : '', links: c ? c.querySelectorAll('a').length : 0, paragraphs: c ? c.querySelectorAll('p').length : 0} })()")
    print(f'{tag}: hero={hero}')
    if not hero['title'].startswith('Stay in Thailand as long as it feels like home') or hero['links'] != 1:
        problems.append(f'{tag}: cinematic hero missing or changed ({hero})')
    print(f'{tag}: release={release} clock_moves={before["clock"] != after["clock"]} running_animations={after["running"]}')
    if before['clock'] == after['clock']:
        problems.append(f'{tag}: the clock did not tick')
    if tag != 'reduced-motion' and after['running'] < 3:
        problems.append(f'{tag}: only {after["running"]} animations running while idle')
    # Walk the pinned process and read which step is active.
    top = page.evaluate("(() => { const p = document.querySelector('[data-pin]'); return p ? [p.getBoundingClientRect().top + scrollY, p.offsetHeight - innerHeight] : null })()")
    if top:
        seen = []
        for fraction in (0.1, 0.4, 0.65, 0.95):
            page.evaluate(f'scrollTo(0, {int(top[0] + top[1] * fraction)})')
            time.sleep(0.9)
            seen.append(page.evaluate("[...document.querySelectorAll('[data-pin-step]')].findIndex(s => s.classList.contains('is-active'))"))
        page.screenshot(path=str(OUT / f'sht-{tag}-process.png'))
        print(f'{tag}: process steps seen={seen}')
        if tag != 'reduced-motion' and seen != [0, 1, 2, 3]:
            problems.append(f'{tag}: pinned process did not step through ({seen})')
    else:
        problems.append(f'{tag}: pinned process missing')
    overflow = page.evaluate('document.documentElement.scrollWidth - innerWidth')
    cookies = sorted(cookie['name'] for cookie in context.cookies())
    print(f'{tag}: overflow={overflow}px cookies={cookies} errors={errors}')
    if overflow > 1:
        problems.append(f'{tag}: page scrolls sideways by {overflow}px')
    if errors:
        problems.append(f'{tag}: script errors {errors}')
    if tag == 'desktop':
        for path in INNER:
            response = page.goto(url + path, wait_until='load', timeout=60000)
            canonical = page.evaluate("document.querySelector('link[rel=canonical]').href")
            ok = response.status == 200 and page.evaluate("!!document.getElementById('sht-config')")
            print(f'{tag}: /{path} status={response.status} canonical={canonical}')
            if not ok:
                problems.append(f'/{path} was not served by the new site ({response.status})')
        # Khun Boon: welcome note on the home page and a working 90-day date keeper.
        page.goto(url + 'stay-legal/90-day-report/', wait_until='load', timeout=60000)
        page.fill('#reminder-date', '2026-10-01')
        page.click('.reminder button[type=submit]')
        due = page.evaluate("(document.querySelector('.reminder-date') || {}).textContent || ''")
        print(f'{tag}: date keeper 2026-10-01 -> {due}')
        if due != 'Tuesday 29 December 2026':
            problems.append(f'90-day date keeper gave {due!r}')
        for path in GONE:
            response = page.goto(url + path, wait_until='load', timeout=60000)
            print(f'{tag}: old /{path} status={response.status}')
            if response.status not in (404, 410):
                problems.append(f'old page /{path} still answers {response.status}')
    page.close()


def main():
    url = (sys.argv[1] if len(sys.argv) > 1 else 'https://secondhomethailand.com/').rstrip('/') + '/'
    OUT.mkdir(parents=True, exist_ok=True)
    problems = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        profiles = (('desktop', {'viewport': {'width': 1440, 'height': 900}}),
                    ('phone', {k: v for k, v in playwright.devices['iPhone 13'].items() if k != 'default_browser_type'}),
                    ('reduced-motion', {'viewport': {'width': 1440, 'height': 900}, 'reduced_motion': 'reduce'}))
        for tag, options in profiles:
            context = browser.new_context(**options)
            check(context, url, tag, problems)
            context.close()
        browser.close()
    if problems:
        print('PROBLEMS:\n- ' + '\n- '.join(problems))
        sys.exit(1)
    print('All live checks passed.')


if __name__ == '__main__':
    main()
