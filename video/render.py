#!/usr/bin/env python3
"""Render the Second Home Thailand launch film frame by frame.

    python video/render.py                     # 60s master, 16:9, 1920x1080, 60fps
    python video/render.py --cut 15 --vertical # 15s cut, 9:16, 1080x1920

The film is one HTML page (video/film.html.j2) with a render(t) function that places every element for
time t. Each frame is set, captured in Chromium and piped to ffmpeg, so every render is identical.
Silent by design: music and voice are laid in afterwards against the beat sheet this script prints.
"""
import argparse
import functools
import http.server
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'video'
BUILD = ROOT/'.cache'/'film'
OUT = HERE/'out'
CHROME = os.environ.get('CHROMIUM_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
FPS = 60

ICON = lambda d: f'<svg viewBox="0 0 48 48" fill="none" stroke="#171717" stroke-width="3" stroke-linecap="square">{d}<path d="M8 44h32" stroke="#4a90c2"/></svg>'
NODES = [
    ('route', 'Route', ICON('<circle cx="24" cy="20" r="14"/><path d="m30 14-4 9-9 4 4-9z"/>')),
    ('documents', 'Documents', ICON('<path d="M12 4h17l7 7v27H12z"/><path d="M18 18h12M18 25h12M18 32h8"/>')),
    ('home', 'Home', ICON('<path d="M6 20 24 6l18 14M11 17v21h26V17"/><path d="M20 38V27h8v11"/>')),
    ('arrival', 'Arrival', ICON('<path d="M24 4v10l16 10v4l-16-5v9l5 4v3l-5-2-5 2v-3l5-4v-9L8 28v-4l16-10"/>')),
    ('renewals', 'Renewals', ICON('<rect x="6" y="8" width="36" height="30"/><path d="M6 17h36M15 4v8M33 4v8"/><circle cx="30" cy="28" r="4" stroke="#4a90c2"/>')),
]
ROUTES = [(20, 'YRS', 'Thailand Privilege', 'Membership · up to 20 years'), (10, 'YRS', 'Long-Term Resident', 'BOI categories · up to 10 years'),
          (1, 'YR', 'Retirement', 'Age 50+ · renewed yearly'), (5, 'YRS', 'DTV', 'Remote work · 5-year visa')]
DOOR_PATH = 'M704 1489V872C682 872 658 859 650 837C786 869 924 690 1024 534C1124 690 1262 869 1398 837C1390 859 1366 872 1344 872V1489'
DOOR_FILL = 'M738 1489V880C760 868 900 720 1024 560C1148 720 1288 868 1310 880V1489Z'

# Cut lists: (scene, start, end, offset into the scene). The master is the full story; cuts reuse its scenes.
CUTS = {
    60: [('line', 0, 3.0, 0), ('flight', 3.0, 10.2, 0), ('door', 10.2, 14.0, 0), ('summit', 14.0, 18.8, 0), ('meet', 18.8, 21.8, 0),
         ('system', 21.8, 30.4, 0), ('routes', 30.4, 36.2, 0), ('homes', 36.2, 42.0, 0), ('writing', 42.0, 46.8, 0),
         ('montage', 46.8, 52.2, 0), ('logo-scene', 52.2, 60.0, 0)],
    30: [('line', 0, 3.0, 0), ('flight', 3.0, 8.4, 1.8), ('door', 8.4, 12.2, 0), ('summit', 12.2, 17.0, 0), ('system', 17.0, 22.6, 3.0),
         ('montage', 22.6, 25.0, 2.6), ('logo-scene', 25.0, 30.0, 2.8)],
    15: [('door', 0, 3.8, 0), ('summit', 3.8, 8.6, 0), ('system', 8.6, 11.4, 5.8), ('logo-scene', 11.4, 15.0, 3.4)],
    6: [('line', 0, .9, .6), ('door', .9, 3.4, .3), ('logo-scene', 3.4, 6.0, 4.4)],
}
BEATS = {60: [(0, 'Low warm tone: the blue line draws'), (3.0, 'Fly in over the Gulf: music starts'), (4.2, 'REMEMBER'), (4.85, 'the warm'), (5.5, 'AIR'),
              (9.3, 'Push: white flash'), (10.2, 'Cut to the door'), (10.75, 'Door opens: warm-air whoosh'), (14.0, 'Summit: music opens up'), (18.8, 'Khun Boon pops in: chime'),
              (22.8, 'Node 1 connects'), (25.0, 'Node 5 connects'), (26.2, 'Pulses flow to Boon'), (30.4, 'Routes: tiles flip'), (36.2, 'Homes: count to 386'),
              (44.75, 'Stamp: AGREED IN WRITING (hit)'), (46.8, 'Montage through the door: build'), (52.2, 'Logo draws: single chime'), (56.8, 'Logo settles, CTA'), (60, 'End')]}


def page_html(width, height, vertical):
    env = Environment(loader=FileSystemLoader([str(HERE), str(ROOT/'sht'/'templates')]), autoescape=True)
    return env.get_template('film.html.j2').render(W=width, H=height, V=vertical, nodes=NODES, routes=ROUTES, door_path=DOOR_PATH,
                                                    door_fill=DOOR_FILL, montage=['skyline', 'night-market', 'temple', 'summit'], scenes=[])


def prepare(width, height, vertical):
    BUILD.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT/'sht'/'assets'/'fonts', BUILD/'fonts', dirs_exist_ok=True)
    img = BUILD/'img'; img.mkdir(exist_ok=True)
    for name, src in (('temple', '1.jpg'), ('skyline', '2.jpg'), ('summit', '3.jpg'), ('night-market', '4.jpg')):
        shutil.copy(ROOT/'assets'/'properties'/src, img/f'{name}.jpg')
    shot = img/'properties.png'
    if not shot.is_file():
        capture_site(shot)
    (BUILD/'film.html').write_text(page_html(width, height, vertical), encoding='utf-8')


def capture_site(target):
    """The /properties page from the site build, captured at 2x as the 'website on screen' shot."""
    site = ROOT/'.cache'/'sht-preview'
    if not (site/'properties'/'index.html').is_file():
        subprocess.run([sys.executable, str(ROOT/'sht'/'build.py'), '--preview', '--output', str(site)], check=True)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(site))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME)
        page = browser.new_page(viewport={'width': 1280, 'height': 900}, device_scale_factor=2)
        page.add_init_script("try{sessionStorage.setItem('sht-intro','1');localStorage.setItem('sht-boon-note',String(Date.now()))}catch(e){}")
        page.goto(f'http://127.0.0.1:{server.server_port}/properties/', wait_until='networkidle')
        page.add_style_tag(content='.header,.progress,.mobile-cta{display:none!important}')
        page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
        page.evaluate("Promise.all([...document.images].slice(0, 60).map(i => i.decode().catch(() => {})))")
        page.evaluate("document.querySelector('.hub-list').scrollIntoView()")
        page.wait_for_timeout(1500)
        top = page.evaluate("document.querySelector('.hub-list').getBoundingClientRect().top + scrollY")
        page.screenshot(path=str(target), clip={'x': 0, 'y': top, 'width': 1280, 'height': 3000}, full_page=True)
        browser.close()
    server.shutdown()


def render_chunk(args):
    index, first, last, width, height, cut, part = args
    from playwright.sync_api import sync_playwright
    scenes = CUTS[cut]
    encoder = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
                                '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS), str(part)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=['--force-color-profile=srgb', '--disable-gpu'])
        page = browser.new_page(viewport={'width': width, 'height': height})
        page.goto((BUILD/'film.html').as_uri())
        page.evaluate(f'SCENES.splice(0, SCENES.length, ...{json.dumps(scenes)})')
        page.evaluate('ready()')
        for frame in range(first, last):
            page.evaluate(f'render({frame / FPS})')
            encoder.stdin.write(page.screenshot(type='png'))
        browser.close()
    encoder.stdin.close()
    encoder.wait()
    return index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cut', type=int, choices=sorted(CUTS), default=60)
    ap.add_argument('--vertical', action='store_true')
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--frames', help='render only a range, e.g. 600:900, for checks')
    ap.add_argument('--still', type=float, nargs='*', help='save PNG stills at these seconds instead of a video')
    args = ap.parse_args()
    width, height = (1080, 1920) if args.vertical else (1920, 1080)
    prepare(width, height, args.vertical)
    name = f"second-home-thailand-{args.cut}s-{'9x16' if args.vertical else '16x9'}"
    OUT.mkdir(parents=True, exist_ok=True)
    if args.still is not None:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=CHROME)
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.goto((BUILD/'film.html').as_uri())
            page.evaluate(f'SCENES.splice(0, SCENES.length, ...{json.dumps(CUTS[args.cut])})')
            page.evaluate('ready()')
            for s in args.still:
                page.evaluate(f'render({s})')
                page.screenshot(path=str(BUILD/f'still-{name}-{s:05.2f}.png'))
            browser.close()
        print('stills in', BUILD)
        return
    total = round(CUTS[args.cut][-1][2] * FPS)
    first, last = (map(int, args.frames.split(':')) if args.frames else (0, total))
    span = last - first
    chunks = [(i, first + span * i // args.workers, first + span * (i + 1) // args.workers, width, height, args.cut, BUILD/f'{name}-part{i}.mp4') for i in range(args.workers)]
    started = time.time()
    with ProcessPoolExecutor(args.workers) as pool:
        list(pool.map(render_chunk, chunks))
    listing = BUILD/f'{name}-parts.txt'
    listing.write_text(''.join(f"file '{c[6]}'\n" for c in chunks))
    final = OUT/f'{name}.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', '-movflags', '+faststart', str(final)], check=True)
    print(f'{final} · {span} frames in {time.time() - started:.0f}s')
    if args.cut in BEATS:
        (OUT/f'beat-sheet-{args.cut}s.txt').write_text('\n'.join(f'{t:06.2f}s  {label}' for t, label in BEATS[args.cut]) + '\n')


if __name__ == '__main__':
    main()
