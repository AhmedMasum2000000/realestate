#!/usr/bin/python3
"""LED AD PRO visiting card (89 x 51 mm + 3 mm bleed). Writes card.html; render with tools/render_card.js.
Usage: /usr/bin/python3 tools/ledadpro_card.py [--name "Full Name"] [--title "Designation"] [--phone "+880 ..."] [--email x@ledadpro.com]
"""
import argparse, base64, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
B = ROOT / 'brand/ledadpro/classic/assets'
OUT = ROOT / 'brand/ledadpro/stationery'
import re
def svg(f):  # reverse logos ship with a navy backing rect; drop it so they sit on the card's own background
    t = re.sub(r'<rect[^>]*fill="#0B1B3F"[^>]*/>', '', (B / f).read_text(), count=1)
    return 'data:image/svg+xml;base64,' + base64.b64encode(t.encode()).decode()

ap = argparse.ArgumentParser()
ap.add_argument('--name', default='Your Name'); ap.add_argument('--title', default='Designation')
ap.add_argument('--phone', default='+880 1XXX-XXXXXX'); ap.add_argument('--email', default='name@ledadpro.com')
a = ap.parse_args(); e = html.escape

CSS = '''
@page{size:95mm 57mm;margin:0}*{margin:0;padding:0;box-sizing:border-box}
:root{--n:#0B1B3F;--p:#0674BB;--s:#8AD5F2;--c:#3FC1F0;--g:#5BBF6A;--m:#5b6782}
body{font-family:Inter,sans-serif;-webkit-print-color-adjust:exact}
.card{width:95mm;height:57mm;position:relative;overflow:hidden;page-break-after:always}
/* trim box = 3mm inset; keep content inside the 4mm safe area */
.front{background:radial-gradient(120% 140% at 85% 20%,#13285a 0%,var(--n) 55%,#060f26 100%)}
.front .grid{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.07) .35mm,transparent .4mm);background-size:2.2mm 2.2mm;
  -webkit-mask-image:linear-gradient(115deg,transparent 30%,#000 75%);mask-image:linear-gradient(115deg,transparent 30%,#000 75%)}
.front .mk{position:absolute;right:-7mm;top:-6mm;height:40mm;border-radius:4mm;opacity:.95;filter:drop-shadow(0 0 3.5mm rgba(63,193,240,.45))}
.front .lg{position:absolute;left:8mm;bottom:10mm;height:13mm}
.front .tag{position:absolute;left:8mm;bottom:6.4mm;font:700 4.6pt Inter;letter-spacing:.32em;text-transform:uppercase;color:#8fa3cc}
.strip{position:absolute;left:0;right:0;bottom:0;height:3mm;background:linear-gradient(90deg,var(--p),var(--c),var(--g))}
.front .strip{height:4.2mm}
.back{background:#fff;color:var(--n)}
.back .mk{position:absolute;right:8mm;top:7.5mm;height:10mm}
.back .nm{position:absolute;left:8mm;top:8.5mm;font:900 12.5pt/1 "Inter Display",Inter;letter-spacing:-.2px}
.back .tt{position:absolute;left:8mm;top:14.4mm;font:700 5.6pt Inter;letter-spacing:.24em;text-transform:uppercase;color:var(--p)}
.back .rows{position:absolute;left:8mm;right:8mm;top:23mm;display:grid;grid-template-columns:1fr 1fr;gap:2.6mm 4mm;line-height:1}
.back .rows div span{display:block;font:800 3.9pt Inter;letter-spacing:.24em;text-transform:uppercase;color:#8a96b0;margin-bottom:.5mm}
.back .rows div b{display:block;font:600 6.4pt/1.25 Inter;color:var(--n)}
.back .rows .w{grid-column:1 / -1}
.back .strip{height:3.6mm}
'''

front = f'''<section class="card front"><div class="grid"></div><img class="mk" src="{svg('favicon-classic.svg')}"><img class="lg" src="{svg('logo-classic-dark.svg')}">
<p class="tag">LED · Metro · Outdoor · Bangladesh</p><div class="strip"></div></section>'''
back = f'''<section class="card back"><img class="mk" src="{svg('logo-classic.svg')}"><h1 class="nm">{e(a.name)}</h1><p class="tt">{e(a.title)}</p>
<div class="rows"><div><span>Mobile</span><b>{e(a.phone)}</b></div><div><span>Sales &amp; marketing</span><b>+880 1958-503753</b></div>
<div><span>Email</span><b>{e(a.email)}</b></div><div><span>Web</span><b>ledadpro.com</b></div>
<div class="w"><span>Office</span><b>House 99, Road 10/2, Block D, Niketon, Gulshan 1, Dhaka</b></div></div><div class="strip"></div></section>'''
(OUT / 'card.html').write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{front}{back}</body></html>')
print(OUT / 'card.html')
