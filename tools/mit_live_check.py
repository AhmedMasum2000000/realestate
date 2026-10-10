#!/usr/bin/env python3
"""Open the live Move In Thailand home page in a real browser and check the scroll story works.

    python tools/mit_live_check.py https://moveinthailand.com/

For desktop and phone sizes it reports: script errors, whether motion started, whether
the hero pinned, how many story frames loaded, whether the closing panels appear at the
end of the story, whether the header hides and returns, and any sideways overflow.
Screenshots go to .cache/live-check/. Exits non-zero if a check fails.
"""
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path('.cache/live-check')


def check(page, url, tag, problems):
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda message: message.type == 'error' and errors.append(message.text))
    page.goto(url, wait_until='load', timeout=90000)
    page.add_style_tag(content='html{scroll-behavior:auto!important}')
    time.sleep(3)
    page.screenshot(path=str(OUT / f'{tag}-intro.png'))
    motion = page.evaluate("document.documentElement.classList.contains('motion-ok')")
    pin = page.evaluate("(() => { const t = window.ScrollTrigger && ScrollTrigger.getAll().find(s => s.pin); return t ? [t.start, t.end] : null })()")
    print(f'{tag}: motion={motion} pin={pin}')
    if not motion or not pin:
        problems.append(f'{tag}: the story hero did not start')
        return
    start, end = pin
    for fraction in (0.3, 0.6, 0.97):
        page.evaluate(f'window.scrollTo(0, {int(start + (end - start) * fraction)})')
        time.sleep(1.8)
        page.screenshot(path=str(OUT / f'{tag}-{int(fraction * 100)}.png'))
    panels = page.evaluate("['.story-end-left', '.story-end-right'].map(s => getComputedStyle(document.querySelector(s)).opacity)")
    frames = page.evaluate("performance.getEntriesByType('resource').filter(r => r.name.includes('/frames/')).length")
    ready = page.evaluate("!!document.querySelector('.story-canvas.is-ready')")
    page.evaluate('window.scrollBy(0, 900)')
    time.sleep(0.8)
    hidden_down = page.evaluate("document.querySelector('.header').classList.contains('is-hidden')")
    page.evaluate('window.scrollBy(0, -250)')
    time.sleep(0.8)
    hidden_up = page.evaluate("document.querySelector('.header').classList.contains('is-hidden')")
    overflow = page.evaluate('document.documentElement.scrollWidth - innerWidth')
    print(f'{tag}: canvas={ready} frames_loaded={frames} end_panels={panels} header_hides={hidden_down} header_returns={not hidden_up} overflow={overflow}px errors={errors}')
    if not ready or frames < 10:
        problems.append(f'{tag}: story frames did not load ({frames})')
    if panels != ['1', '1']:
        problems.append(f'{tag}: closing panels not shown at the end of the story ({panels})')
    if not hidden_down or hidden_up:
        problems.append(f'{tag}: header did not hide and return')
    if overflow > 1:
        problems.append(f'{tag}: page scrolls sideways by {overflow}px')
    if errors:
        problems.append(f'{tag}: script errors {errors}')


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://moveinthailand.com/'
    OUT.mkdir(parents=True, exist_ok=True)
    problems = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        for width, height, tag in ((1440, 900, 'desktop'), (390, 844, 'phone')):
            page = browser.new_page(viewport={'width': width, 'height': height})
            check(page, url, tag, problems)
            page.close()
        browser.close()
    if problems:
        print('PROBLEMS:\n- ' + '\n- '.join(problems))
        sys.exit(1)
    print('All live checks passed.')


if __name__ == '__main__':
    main()
