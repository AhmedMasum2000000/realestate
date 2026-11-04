#!/usr/bin/python3
"""LED AD PRO universal strategic plan (client proposal) -> HTML, then PDF via tools/render_pdf.js.

Usage: /usr/bin/python3 tools/ledadpro_plan.py [--client "Brand name"] [--out path.html]
Prices are taken from the October 2026 quotations (Metro Rail LED, static billboards). Update RATES
when quotations change. Needs Pillow (system python).
"""
import argparse, base64, html, io, re, sys
from datetime import date
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from ledadpro_extra import CLIENTS  # noqa: E402

V2 = ROOT / 'sites/ledadpro-v2'
PI = ROOT / 'brand/ledadpro/plan/img'
e = html.escape

SALES, OFFICE, EMAIL, WEB = '+880 1958-503753', '+880 1316-743003', 'info@ledadpro.com', 'ledadpro.com'
ADDRESS = 'Flat A1, House 99, Road 10/2, Block D, Niketon, Gulshan 1, Dhaka'

METRO = dict(screens=840, trains=14, coaches=84, hours=16, riders='5,50,000', per_min=35)
METRO['min_day'] = METRO['hours'] * METRO['trains']          # 1 min per hour on every train
METRO['min_month'] = METRO['min_day'] * 30
METRO['month'] = METRO['min_month'] * METRO['per_min']
SITES = [  # kept for the cover/tiles photos only
     # flagship static billboards, price per year (BDT)
    ('expressway-chairman-bari', 'Dhaka Elevated Expressway, Chairman Bari Crossing', 'Mohakhali & Airport', "125' × 40'", '5,000', 4200000, 'Lighting billboard'),
    ('jalshiri-300-feet', 'Jalshiri Bus Stand, Purbachal 300 Feet', 'Dhaka (both sides)', "100' × 30' × 2", '6,000', 3800000, 'Billboard, both sides'),
    ('banani-kakoli-dropwall', 'Elevated Expressway, near Banani–Kakoli', 'Mohakhali', "40' × 17' + 40' × 12'", '1,160', 3250000, 'Drop-wall billboard'),
    ('kuril-300-feet', 'Kuril Biswaroad, Purbachal 300 Feet', 'Kuril, Expressway & 300 Feet', "35' × 20'", '700', 1470000, 'Billboard'),
]


def bdt(n):  # Indian/Bangladeshi digit grouping: 1,08,22,400
    s = str(int(n)); head, tail = s[:-3], s[-3:]
    while len(head) > 2:
        tail = head[-2:] + ',' + tail; head = head[:-2]
    return (head + ',' + tail) if head else tail


def uri(p, w=1300):
    p = Path(p)
    if p.suffix == '.svg':
        return 'data:image/svg+xml;base64,' + base64.b64encode(p.read_bytes()).decode()
    im = Image.open(p)
    if im.mode in ('RGBA', 'LA', 'P') and p.suffix == '.png':
        return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()
    im = im.convert('RGB'); im.thumbnail((w, w)); b = io.BytesIO(); im.save(b, 'JPEG', quality=74, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def logo(c):
    slug = re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')
    for ext in ('svg', 'png'):
        f = V2 / 'img/clients' / f'{slug}.{ext}'
        if f.exists():
            return uri(f)


CSS = (ROOT / 'tools/ledadpro_doc.css').read_text()
CREDITS = (PI / 'CREDITS.txt').read_text().strip() if (PI / 'CREDITS.txt').exists() else ''


def build(client):
    LOGO_W = uri(ROOT / 'brand/ledadpro/logo/logo-horizontal-reverse.svg')
    MARK = uri(ROOT / 'brand/ledadpro/logo/mark.svg')
    hr = {k: uri(PI / f'hr-{k}.jpg', 2400) for k in ('cover', 'metro', 'formats')}   # high-res only (>= 2400 px source)
    work = {k: uri(V2 / 'img/work' / f'{k}.jpg', 1600) for k in ['royal-enfield-gulshan-2', 'haier-gulshan-2', 'aarong-noakhali']}
    today = date.today().strftime('%B %Y')
    who = e(client) if client else '________________________'
    pages = []
    P = pages.append
    n = iter(range(1, 50))
    eb = lambda t: f'<p class="eb">{next(n):02d} · {t}</p>'

    # 1 cover
    P(f'''<section class="pg cover"><div class="cov-l"><img class="lg" src="{LOGO_W}">
<p class="kick" style="margin-top:auto">360° Visibility Plan</p>
<h1>Own the<br>city’s<br><em>attention.</em></h1>
<div class="for"><span>Prepared for</span><b>{who}</b><span>{today} · Official LED partner to AD Pro</span></div></div>
<div class="cov-r" style="background-image:linear-gradient(90deg,#0B1B3F 0%,rgba(11,27,63,.35) 28%,rgba(11,27,63,0) 60%),url({hr['cover']})"></div></section>''')

    # 2 proof
    wall = ''.join(f'<span><img alt="{e(c)}" src="{logo(c)}"></span>' for c in CLIENTS if logo(c)) + '<span class="more"><b>400+</b>brands served</span>'
    P(f'''<section class="pg">{eb('Proof first')}<h2>Brands that can choose anyone<br>chose our team.</h2>
<div class="stats"><div><b>400+</b><span>brands served by our team</span></div><div><b>56</b><span>LED screens in our network</span></div><div><b>840</b><span>Metro Rail LED screens</span></div><div><b>10</b><span>cities covered</span></div></div>
<div class="wall">{wall}</div><p class="foot">Campaigns delivered by the LED AD PRO team, including as official LED partner to AD Pro.</p></section>''')

    # 3 real work
    cases = [('royal-enfield-gulshan-2', 'Royal Enfield', 'Bullet 350 launch, 7 LED boards · Gulshan-2'), ('haier-gulshan-2', 'Haier', 'LED billboard campaign · Gulshan-2'),
             ('aarong-noakhali', 'Aarong', 'Store launch & illuminated signage · Noakhali')]
    P(f'''<section class="pg">{eb('Real work')}<h2>Real campaigns. Real streets.</h2><div class="cases c3">''' +
      ''.join(f'<figure><img src="{work[k]}"><figcaption><b>{b}</b><span>{s}</span></figcaption></figure>' for k, b, s in cases) + '</div></section>')

    # 5 the stack
    stack = [('See', 'Be impossible to miss', 'var(--p)', ['Static mega billboards', 'LED billboards', 'Building & airport branding']),
             ('Remember', 'Repeat until it sticks', 'var(--c)', ['Metro Rail LED, 1 min every hour', 'LED loops all day', 'Bus branding']),
             ('Visit', 'Bring them to you', 'var(--y)', ['LED caravan roadshows', 'Outlet opening', 'Events & activations']),
             ('Buy', 'Close at the shelf', '#7c5cff', ['Printing & packaging', 'Newspaper ads', 'Digital marketing'])]
    P(f'''<section class="pg">{eb('The plan on one page')}<h2>Nobody can scroll past a billboard.<br>We take you from <em>seen</em> to <em>sold.</em></h2><div class="stack">''' +
      ''.join(f'<div class="st"><i style="background:{c}"></i><small>0{i + 1}</small><h3>{h}</h3><p>{s}</p><ul>' + ''.join(f'<li>{x}</li>' for x in xs) + '</ul></div>'
              for i, (h, s, c, xs) in enumerate(stack)) + '</div><div class="band"><div><b>No skip button.</b>No ad-blockers, no feed, no scrolling past.</div><div><b>Size = trust.</b>Big physical presence says “big, safe brand”.</div><div><b>Daily repetition.</b>Same route, same screen, until you are the one they remember.</div><div><b>Fuels digital.</b>People search what they saw on the street.</div></div></section>')

    # 6 formats, nationwide
    fm = ['LED billboards', 'Static billboards', 'Metro Rail LED', 'LED caravan', 'Airport branding', 'Building branding',
          'Bus branding', 'Outlet opening', 'Events & activations', 'Printing & packaging', 'Newspaper ads', 'Digital marketing']
    P(f'''<section class="pg split fm">{''}<div>{eb('Anywhere in Bangladesh')}<h2>Any format. Any district.<br><em>One contract.</em></h2>
<ol class="fmt">''' + ''.join(f'<li><small>{i + 1:02d}</small>{t}</li>' for i, t in enumerate(fm)) + f'''</ol>
<p class="cta-line">We cover all over Bangladesh. <b>Send us your areas and dates, we send back the sites.</b></p></div>
<div class="ph" style="background-image:url({hr['formats']})"></div></section>''')

    # 7 plays
    plays = [('Launch', '4–6 weeks', 'New product, store or brand', ['LED billboards in 3–5 key areas', 'Metro Rail LED for 1 month', 'LED caravan roadshow', 'Opening event or activation', 'Digital boost on launch week']),
             ('Dominate', '3–12 months', 'Category leadership', ['A flagship Expressway or 300 Feet billboard', 'LED network rotation across Dhaka', 'Metro Rail LED, 3+ months', 'Bus or airport branding', 'Monthly review and refresh']),
             ('Season surge', '2–6 weeks', 'Eid, Puja, Boishakh, winter sales', ['Metro Rail LED in festive weeks', 'LED billboards near shopping hubs', 'LED caravan in markets', 'In-store and outlet branding', 'Offer-led creative updates'])]
    P(f'''<section class="pg">{eb('Pick your play')}<h2>Three proven plays. Pick the one<br>that matches your goal.</h2><div class="plays">''' +
      ''.join(f'<div class="play{" hot" if i == 1 else ""}"><small>{d}</small><h3>{t}</h3><p>{b}</p><ul class="ticks">' + ''.join(f'<li>{x}</li>' for x in xs) + '</ul></div>'
              for i, (t, d, b, xs) in enumerate(plays)) + '</div><p class="foot">Always-on option: keep one LED or Metro presence every month so your brand never disappears between campaigns.</p></section>')

    # 8 metro spotlight
    m = METRO
    P(f'''<section class="pg split">{''}<div>{eb('Spotlight · Metro Rail LED')}<h2>Ride with <em>5.5 lakh</em><br>commuters a day.</h2>
<div class="nums"><div><b>{m['screens']}</b><span>screens</span></div><div><b>{m['trains']}</b><span>trains</span></div><div><b>{m['hours']} h</b><span>daily</span></div><div><b>{m['riders']}</b><span>riders / day</span></div></div>
<div class="calc"><p><span>1 min every hour × {m['hours']} h × {m['trains']} trains</span><b>{m['min_day']} min / day</b></p>
<p><span>× 30 days</span><b>{bdt(m['min_month'])} min / month</b></p>
<p><span>× from BDT {m['per_min']} per minute</span><b>BDT {bdt(m['month'])} / month</b></p></div>
<p class="note">Approx. rider figure from the operator. Content due 5 days before airing · 100% advance · monthly exposure report included · excl. VAT, Tax &amp; AIT.</p></div>
<div class="ph" style="background-image:url({hr['metro']})"></div></section>''')

    # 14 end
    P(f'''<section class="pg end"><img class="mk" src="{MARK}"><h2>Let’s light up<br><em>your brand.</em></h2>
<div class="next"><div><b>1</b><h3>Send your requirement</h3><p>Goal, areas, dates, budget. One call or WhatsApp.</p></div><div><b>2</b><h3>Get your plan</h3><p>Shortlisted sites and a written quote, fast.</p></div><div><b>3</b><h3>Go live</h3><p>We install, run and send you photo proof.</p></div></div>
<div class="ct"><div><span>Sales &amp; marketing</span><b>{SALES}</b></div><div><span>Office</span><b>{OFFICE}</b></div><div><span>Email</span><b>{EMAIL}</b></div><div><span>Web</span><b>{WEB}</b></div><div><span>Address</span><b>{ADDRESS}</b></div></div>
<p class="fine">{CREDITS}<br>Quotes valid 10 days · rates exclude VAT, Tax &amp; AIT · prime sites and festive slots are limited</p><img class="lg" src="{LOGO_W}"></section>''')

    return f'<!doctype html><html><head><meta charset="utf-8"><title>LED AD PRO · 360° Visibility Plan</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--client', default=''); ap.add_argument('--out', default=str(ROOT / 'brand/ledadpro/plan/plan.html'))
    a = ap.parse_args()
    Path(a.out).write_text(build(a.client)); print(a.out)
