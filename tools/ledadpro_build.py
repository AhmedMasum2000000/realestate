"""Build the live LED AD PRO site (ledadpro.com) from the v2 design and the locations data.

Output: sites/ledadpro-live/
  index.html                         homepage (from sites/ledadpro-v2/index.html)
  assets/                            css, js, data and photos
  locations/index.html               all locations
  locations/<area>/index.html        area page
  locations/<area>/<topic>/index.html  5 topic pages per area
  sitemap-ledadpro.xml, llms.txt

Run: python3 tools/ledadpro_build.py
"""
import html, json, math, re, shutil, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'sites/ledadpro-v2'
OUT = ROOT / 'sites/ledadpro-live'
sys.path.insert(0, str(ROOT / 'tools'))
from ledadpro_areas import AREA, STATIC_AREA  # noqa: E402
from ledadpro_extra import CLIENTS, CASES, SERVICES  # noqa: E402

SITE = 'https://ledadpro.com'
PHONE, PHONE_TXT = '+8801958503753', '+880 1958-503753'  # Sales and Marketing (main line for leads)
OFFICE, OFFICE_TXT = '+8801316743003', '+880 1316-743003'  # office / general
EMAIL = 'info@ledadpro.com'
ADDRESS = 'Flat A1, House 99 (1st floor), Road 10/2, Block D, Niketon, Gulshan 1, Dhaka'
TODAY = date.today().isoformat()
e = html.escape

data = (SRC / 'locations.js').read_text()
LOCS = json.loads(re.search(r'window\.LOCS=(.*?);\nwindow\.STATIC', data, re.S).group(1))
STATIC = json.loads(re.search(r'window\.STATIC=(.*?);\s*$', data, re.S).group(1))
for a in LOCS:
    a['short'] = a['name'].split(' & ')[0].replace(' Railway Station', '').replace(' Launch Terminal', '')
    a['static'] = [s for s in STATIC if STATIC_AREA.get(s['n']) == a['id']]
BYID = {a['id']: a for a in LOCS}

TOPICS = [  # slug, nav label, title pattern, h1 pattern
    ('led-screens', 'LED screens', 'LED Screens in {n}: All {c} Locations & Facing | LED AD PRO', 'Every LED screen in {n}'),
    ('advertising-cost', 'Cost', 'LED Billboard Advertising Cost in {n} (2026 Guide) | LED AD PRO', 'LED billboard advertising cost in {n}'),
    ('audience-and-routes', 'Audience & routes', 'Who Sees LED Billboards in {n}: Audience & Routes | LED AD PRO', 'Who your {n} LED ad reaches'),
    ('campaign-planning', 'Planning', 'How to Plan an LED Billboard Campaign in {n} | LED AD PRO', 'Plan an LED billboard campaign in {n}'),
    ('faq', 'FAQ', 'LED Billboard Advertising in {n}: Questions Answered | LED AD PRO', '{n} LED advertising: questions answered'),
]


def km(a, b):
    p1, p2 = math.radians(a['lat']), math.radians(b['lat'])
    d = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b['lon'] - a['lon']) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(d))


def nearby(a, n=4):
    return sorted((x for x in LOCS if x is not a), key=lambda x: km(a, x))[:n]


def img(p):  # data paths are relative to the v2 folder
    return '/assets/' + p if p and not p.startswith('/') else p


def screens(a, n):
    return f"{n} LED {'screen' if n == 1 else 'screens'}"


def org():
    return {'@type': 'LocalBusiness', '@id': SITE + '/#business', 'name': 'LED AD PRO', 'url': SITE + '/',
            'telephone': PHONE, 'email': EMAIL,
            'contactPoint': [{'@type': 'ContactPoint', 'telephone': PHONE, 'contactType': 'sales', 'areaServed': 'BD', 'availableLanguage': ['en', 'bn']},
                             {'@type': 'ContactPoint', 'telephone': OFFICE, 'contactType': 'customer service', 'areaServed': 'BD', 'availableLanguage': ['en', 'bn']}], 'image': SITE + '/assets/brand/og-image.png', 'logo': SITE + '/assets/brand/logo-horizontal-1600.png',
            'address': {'@type': 'PostalAddress', 'streetAddress': 'Flat A1, House 99, Road 10/2, Block D, Niketon',
                        'addressLocality': 'Dhaka', 'addressRegion': 'Gulshan 1', 'addressCountry': 'BD'},
            'geo': {'@type': 'GeoCoordinates', 'latitude': 23.774, 'longitude': 90.417},
            'openingHoursSpecification': [
                {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'], 'opens': '09:00', 'closes': '20:00'},
                {'@type': 'OpeningHoursSpecification', 'dayOfWeek': 'Friday', 'opens': '10:00', 'closes': '12:00'}],
            'areaServed': {'@type': 'Country', 'name': 'Bangladesh'}}


def ld(*objs):
    return ''.join(f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", **o}, ensure_ascii=False)}</script>' for o in objs)


def crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(items)]}


def faq_ld(qas):
    return {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub('<[^>]+>', '', ans)}} for q, ans in qas]}


OG_DEFAULT = ['/assets/brand/og-image.png']  # build_area swaps in the area photo


def page(path, title, desc, h1, body, crumb, schema=(), og_img=None, lead=''):
    og_img = og_img or OG_DEFAULT[0]
    url = SITE + path
    bc = ''.join(f'<a href="{u}">{e(n)}</a><span>/</span>' for n, u in crumb[:-1]) + f'<span aria-current="page">{e(crumb[-1][0])}</span>'
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="website"><meta property="og:site_name" content="LED AD PRO"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}{og_img}">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#0B1B3F">
<link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml"><link rel="icon" href="/assets/brand/favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="/assets/brand/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@800;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/pages.css?v=2">
{ld(*schema, crumbs(crumb))}
</head>
<body>
<header class="ph"><a class="logo" href="/" aria-label="LED AD PRO home"><img src="/assets/brand/logo-header-animated.svg" alt="LED AD PRO" width="300" height="70" data-replay></a>
<nav aria-label="Main"><a href="/#services">Services</a><a href="/locations/">Locations</a><a href="/pricing/">Pricing</a><a href="/services/metro-rail-led-advertising/">Metro LED</a><a href="/services/led-caravan/">LED Caravan</a><a href="/clients/">Clients</a><a href="/#contact">Contact</a></nav>
<a class="btn" href="tel:{PHONE}">Call {PHONE_TXT}</a></header>
<main>
<div class="wrap"><nav class="bc" aria-label="Breadcrumb">{bc}</nav>
<h1 class="display">{e(h1)}</h1>{f'<p class="lead">{lead}</p>' if lead else ''}</div>
{body}
<section class="cta"><div class="wrap"><h2 class="display">Get a shortlist and dates</h2>
<p>Tell us your brand, budget and preferred dates. We reply with available screens, a written quote and the creative specification.</p>
<div class="cta-b"><a class="btn" href="tel:{PHONE}">Call {PHONE_TXT}</a><a class="btn ghost" href="mailto:{EMAIL}?subject={e('LED billboard enquiry: ' + h1)}">Email {EMAIL}</a></div>
<p class="hours">Sales &amp; marketing <a href="tel:{PHONE}">{PHONE_TXT}</a> · Office <a href="tel:{OFFICE}">{OFFICE_TXT}</a></p>
<p class="hours">Sat–Thu 9am–8pm · Friday 10am–12pm · {e(ADDRESS)}</p></div></section>
</main>
<footer class="pf"><div class="wrap">
<a class="wm" href="/" aria-label="LED AD PRO home"><img src="/assets/brand/logo-header-animated.svg" alt="LED AD PRO" width="300" height="70" data-replay></a>
<nav aria-label="Locations">{''.join(f'<a href="/locations/{x["id"]}/">{e(x["short"])}</a>' for x in LOCS)}</nav>
<p>&copy; {date.today().year} LED AD PRO · Sales <a href="tel:{PHONE}">{PHONE_TXT}</a> · Office <a href="tel:{OFFICE}">{OFFICE_TXT}</a> · Official LED partner to AD Pro · <a href="/">Home</a> · <a href="/locations/">All locations</a> · <a href="/services/metro-rail-led-advertising/">Metro Rail LED</a> · <a href="/services/led-caravan/">LED Caravan</a> · <a href="/clients/">Our clients</a></p>
</div></footer>
<script>(function(){{if(matchMedia("(prefers-reduced-motion: reduce)").matches||!("IntersectionObserver" in window))return;var io=new IntersectionObserver(function(es){{es.forEach(function(e){{if(!e.isIntersecting)return;var i=e.target,b=i.dataset.src||(i.dataset.src=i.getAttribute("src"));i.src=b+"#r"+Date.now();}});}},{{threshold:.6}});document.querySelectorAll("img[data-replay]").forEach(function(i){{io.observe(i);}});}})();</script>
<div class="sticky-cta"><a href="tel:{PHONE}">Call now</a><a href="mailto:{EMAIL}">Get a quote</a></div>
</body></html>
'''
    f = OUT / path.strip('/') / 'index.html' if path != '/' else OUT / 'index.html'
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(doc)
    PAGES.append((path, title))


PAGES = []


def cards(items, area_photo_note=True):
    out = []
    for p in items:
        out.append(f'''<figure class="sc"><img loading="lazy" src="{img(p['i'])}" alt="{e(p['n'])}" width="1200" height="800"><figcaption><b>{e(p['n'])}</b>{f'<span>Facing: {e(p["f"])}</span>' if p.get('f') else ''}{'<em>Area photo</em>' if p.get('ref') and area_photo_note else ''}</figcaption></figure>''')
    return '<div class="grid">' + ''.join(out) + '</div>'


def topic_nav(a, cur):
    base = f'/locations/{a["id"]}/'
    links = [f'<a href="{base}"{" aria-current=page" if cur == "" else ""}>Overview</a>'] + [
        f'<a href="{base}{s}/"{" aria-current=page" if cur == s else ""}>{e(lbl)}</a>' for s, lbl, *_ in TOPICS]
    return '<div class="wrap"><nav class="tn" aria-label="' + e(a['short']) + ' guides">' + ''.join(links) + '</nav></div>'


def faqs(a):
    n, c, sh = a['name'], len(a['p']), a['short']
    first = a['p'][0]['n']
    return [
        (f'How many LED billboards does LED AD PRO have in {sh}?', f'LED AD PRO lists {screens(a, c)} in {e(n)}: {e(", ".join(p["n"] for p in a["p"][:4]))}{" and more" if c > 4 else ""}. See <a href="/locations/{a["id"]}/led-screens/">every {e(sh)} screen with photos</a>.'),
        (f'How much does LED billboard advertising cost in {sh}?', f'It depends on the screen, the number of slots per hour and your dates. LED AD PRO’s published guide puts LED billboard time from about 100 to 600 BDT per minute; the written quote confirms the current rate. Read the <a href="/locations/{a["id"]}/advertising-cost/">{e(sh)} cost guide</a>.'),
        (f'Which {sh} screen should I choose?', f'Start with the direction your audience travels. Each screen faces a specific road or junction, for example {e(first)}{" (facing " + e(a["p"][0]["f"]) + ")" if a["p"][0].get("f") else ""}. Compare the facing of each screen on the <a href="/locations/{a["id"]}/audience-and-routes/">audience and routes page</a>.'),
        (f'How quickly can my ad run on a {sh} screen?', 'Once the dates, screens and artwork are confirmed in writing, an LED campaign can usually start within days, because there is nothing to print or install. Availability is confirmed when you enquire.'),
        ('What file format do LED billboards need?', 'Ask for the exact pixel size and orientation of each screen in your proposal. Most LED screens play a short video (MP4) or still image (JPG/PNG) made to that size, with large text and strong contrast so it reads from the road.'),
        (f'Can I book several {sh} screens together?', f'Yes. You can combine screens in {e(sh)} or add nearby areas such as ' + ', '.join(f'<a href="/locations/{x["id"]}/">{e(x["short"])}</a>' for x in nearby(a, 3)) + '. A package is priced by its screens and slots, not as one screen.'),
        ('Do you handle permissions and installation?', 'For LED AD PRO’s own screens the placement is already in place, so you book airtime only. For new billboards or custom LED displays, we discuss permissions, design and installation as part of the written proposal.'),
        ('How do I get a quote?', f'Call {PHONE_TXT} or email {EMAIL} with your brand, preferred area, dates and budget. You receive a shortlist of screens, availability and a written quote.'),
    ]


def build_area(a):
    n, sh, c, aid = a['name'], a['short'], len(a['p']), a['id']
    note, audience = AREA[aid]
    near = nearby(a)
    city = 'Dhaka' if a['kind'] == 'dhaka' else sh
    hero_img = img(a['img'])
    OG_DEFAULT[0] = hero_img
    svc = {'@type': 'Service', 'name': f'LED billboard advertising in {n}', 'serviceType': 'Digital out-of-home advertising',
           'provider': {'@id': SITE + '/#business'}, 'areaServed': {'@type': 'Place', 'name': f'{n}, {"Dhaka, " if a["kind"] == "dhaka" else ""}Bangladesh',
                                                                 'geo': {'@type': 'GeoCoordinates', 'latitude': a['lat'], 'longitude': a['lon']}}}
    itemlist = {'@type': 'ItemList', 'name': f'LED screens in {n}', 'numberOfItems': c, 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': p['n'], 'image': SITE + img(p['i'])} for i, p in enumerate(a['p'])]}
    base_crumb = [('Home', '/'), ('Locations', '/locations/'), (sh, f'/locations/{aid}/')]
    qas = faqs(a)
    answer = (f'LED AD PRO has <strong>{screens(a, c)}</strong> in {e(n)}, {city}. {e(note)} '
              f'The screens reach {e(audience)}. Call {PHONE_TXT} for dates and a written quote.')
    # ---- Area overview
    body = f'''{topic_nav(a, '')}
<section class="wrap two"><div><p class="answer">{answer}</p>
<table class="facts"><tr><th>Area</th><td>{e(n)}</td></tr><tr><th>City</th><td>{e(city)}</td></tr><tr><th>LED screens</th><td>{c}</td></tr>
{f'<tr><th>Static billboards</th><td>{len(a["static"])}</td></tr>' if a['static'] else ''}<tr><th>Best for</th><td>{e(audience.capitalize())}</td></tr>
<tr><th>Map</th><td><a href="https://www.openstreetmap.org/?mlat={a['lat']}&amp;mlon={a['lon']}#map=15/{a['lat']}/{a['lon']}" rel="nofollow">Open {e(sh)} on the map</a></td></tr></table></div>
<figure class="hero-ph"><img src="{hero_img}" alt="LED billboard in {e(n)}" width="1200" height="800"></figure></section>
<section class="wrap"><h2 class="display">LED screens in {e(sh)}</h2>{cards(a['p'])}</section>
{f'<section class="wrap"><h2 class="display">Static billboards near {e(sh)}</h2>{cards([{"n": s["n"], "i": s["i"], "f": ""} for s in a["static"]])}</section>' if a['static'] else ''}
<section class="wrap"><h2 class="display">{e(sh)} guides</h2><div class="tiles">{''.join(f'<a class="tile" href="/locations/{aid}/{s}/"><b>{e(h.format(n=sh, c=c))}</b><span>Read &#9656;</span></a>' for s, lbl, t, h in TOPICS)}</div></section>
<section class="wrap"><h2 class="display">Questions about {e(sh)}</h2>{''.join(f'<details><summary>{e(q)}</summary><p>{ans}</p></details>' for q, ans in qas[:4])}<p><a href="/locations/{aid}/faq/">All {e(sh)} questions &#9656;</a></p></section>
<section class="wrap"><h2 class="display">Nearby locations</h2><div class="tiles">{''.join(f'<a class="tile" href="/locations/{x["id"]}/"><b>{e(x["name"])}</b><span>{screens(x, len(x["p"]))} · {km(a, x):.0f} km &#9656;</span></a>' for x in near)}</div></section>'''
    page(f'/locations/{aid}/', f'LED Billboard Advertising in {n} ({c} {"Screen" if c == 1 else "Screens"}) | LED AD PRO',
         f'Advertise on {screens(a, c)} in {n}, {city}. See every location with photos and facing, costs, audiences and booking steps. Call {PHONE_TXT}.',
         f'LED billboard advertising in {n}', body, base_crumb, (org(), svc, itemlist, faq_ld(qas[:4])))

    # ---- Topic 1: LED screens
    rows = ''.join(f'<tr><td>{e(p["n"])}</td><td>{e(p.get("f") or "Ask for details")}</td></tr>' for p in a['p'])
    body = f'''{topic_nav(a, 'led-screens')}
<section class="wrap"><p class="answer">There {'is' if c == 1 else 'are'} <strong>{screens(a, c)}</strong> available through LED AD PRO in {e(n)}. Each one is listed below with its real photo and the direction it faces, so you can match it to your audience’s journey.</p>
<table class="facts wide"><tr><th>Screen</th><th>Facing</th></tr>{rows}</table></section>
<section class="wrap">{cards(a['p'])}</section>
<section class="wrap prose"><h2 class="display">How to compare {e(sh)} screens</h2>
<ul><li><b>Facing:</b> a screen is seen by traffic coming towards it, so the facing tells you which journey it reaches.</li>
<li><b>Size and height:</b> ask for the pixel size and the height above the road; it decides how much text people can read.</li>
<li><b>Slots:</b> LED screens share time between advertisers. Ask how many slots per hour your ad gets.</li>
<li><b>Recent photo:</b> ask for a current photo or video of the screen running, as surroundings change.</li></ul>
<p>Next: <a href="/locations/{aid}/advertising-cost/">what it costs in {e(sh)}</a> · <a href="/locations/{aid}/audience-and-routes/">who sees each screen</a></p></section>'''
    page(f'/locations/{aid}/led-screens/', TOPICS[0][2].format(n=sh, c=c), f'All {screens(a, c)} in {n} with photos and facing direction, so you can choose the right placement. LED AD PRO, Dhaka.',
         TOPICS[0][3].format(n=sh), body, base_crumb + [('LED screens', f'/locations/{aid}/led-screens/')], (org(), itemlist))

    # ---- Topic 2: cost
    body = f'''{topic_nav(a, 'advertising-cost')}
<section class="wrap prose"><p class="answer">LED billboard advertising in {e(sh)} is priced by <strong>screen, airtime and dates</strong>. LED AD PRO’s published guide puts LED billboard time from about <strong>100 to 600 BDT per minute</strong>, with premium junctions at the higher end. Your written quote confirms the current rate for the screens you choose.</p>
<h2 class="display">What changes the price</h2>
<table class="facts wide"><tr><th>Factor</th><th>Why it matters</th></tr>
<tr><td>Location and facing</td><td>Busy junctions{', such as ' + e(a['p'][0]['n']) if c else ''}, cost more than quieter roads.</td></tr>
<tr><td>Slots per hour</td><td>More plays per hour means more people see your ad, and a higher price.</td></tr>
<tr><td>Campaign length</td><td>Longer bookings are usually priced better per day than short bursts.</td></tr>
<tr><td>Number of screens</td><td>A package across {e(sh)}{' and nearby areas' if near else ''} is priced by its screens, not as one screen.</td></tr>
<tr><td>Creative</td><td>Bringing a finished video or image costs nothing extra; design and animation are quoted separately.</td></tr></table>
<h2 class="display">Static billboards</h2><p>Printed static billboards are priced differently: rent per square foot per month, plus printing and installation. LED AD PRO’s published guide puts regular billboard rent from about 500 to 3,000 BDT per square foot, depending on location and size.{f' See the <a href="/locations/{aid}/">static billboards near {e(sh)}</a>.' if a['static'] else ''}</p>
<h2 class="display">Get a firm price</h2><p>Send your preferred screens, dates and budget. We reply with availability and a written quote that lists the screens, slots, dates and total.</p>
<p>Related: <a href="/locations/{aid}/led-screens/">{e(sh)} screens</a> · <a href="/locations/{aid}/campaign-planning/">plan your campaign</a> · <a href="/locations/{aid}/faq/">{e(sh)} FAQ</a></p></section>'''
    page(f'/locations/{aid}/advertising-cost/', TOPICS[1][2].format(n=sh), f'How much LED billboard advertising costs in {n}: price factors, indicative per-minute rates and how to get a written quote from LED AD PRO.',
         TOPICS[1][3].format(n=sh), body, base_crumb + [('Advertising cost', f'/locations/{aid}/advertising-cost/')], (org(), svc))

    # ---- Topic 3: audience and routes
    facings = [p for p in a['p'] if p.get('f')]
    body = f'''{topic_nav(a, 'audience-and-routes')}
<section class="wrap prose"><p class="answer">{e(note)} LED screens here reach <strong>{e(audience)}</strong>. Which people see your ad depends on the direction each screen faces.</p>
<h2 class="display">Routes each screen faces</h2>
{'<table class="facts wide"><tr><th>Screen</th><th>Faces traffic from / towards</th></tr>' + ''.join(f'<tr><td>{e(p["n"])}</td><td>{e(p["f"])}</td></tr>' for p in facings) + '</table>' if facings else '<p>Ask us for the facing of each screen and a recent photo of the view.</p>'}
<h2 class="display">Match the screen to your goal</h2>
<ul><li><b>Shops and restaurants in {e(sh)}:</b> choose the screen on the road your customers use to reach you, and show the turning or landmark.</li>
<li><b>Brand awareness:</b> combine several facings so you meet traffic in both directions.</li>
<li><b>Launches and events:</b> run more slots for a short, intense burst before the date.</li>
<li><b>City-wide reach:</b> add nearby areas: {', '.join(f'<a href="/locations/{x["id"]}/">{e(x["short"])}</a>' for x in near[:3])}.</li></ul>
<p>Related: <a href="/locations/{aid}/led-screens/">{e(sh)} screens with photos</a> · <a href="/locations/{aid}/campaign-planning/">campaign planning</a></p></section>'''
    page(f'/locations/{aid}/audience-and-routes/', TOPICS[2][3].format(n=sh) + ' | LED AD PRO', f'Who sees LED billboards in {n}: the audience, the routes each screen faces and how to match a screen to your goal.',
         TOPICS[2][3].format(n=sh), body, base_crumb + [('Audience & routes', f'/locations/{aid}/audience-and-routes/')], (org(), svc))

    # ---- Topic 4: campaign planning
    steps = [('Set the goal', f'Decide what people should do after seeing the ad: visit a {e(sh)} outlet, call, search your name or remember a launch date.'),
             ('Pick screens and dates', f'Choose from the {screens(a, c)} in {e(sh)} by facing, and check availability for your dates.'),
             ('Confirm the specification', 'Get the pixel size, orientation, file format, ad length and slots per hour in writing.'),
             ('Make the creative', 'Use one message, a large logo and no more than about seven words. Test it on a phone held at arm’s length.'),
             ('Approve and go live', 'Approve the written quote and the artwork. LED campaigns can start within days because there is nothing to print.'),
             ('Check and report', 'Ask for photos or video of your ad running on each screen during the campaign.')]
    howto = {'@type': 'HowTo', 'name': f'How to plan an LED billboard campaign in {n}', 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': t, 'text': re.sub('<[^>]+>', '', html.unescape(d))} for i, (t, d) in enumerate(steps)]}
    body = f'''{topic_nav(a, 'campaign-planning')}
<section class="wrap prose"><p class="answer">An LED billboard campaign in {e(sh)} takes six steps: set the goal, pick screens and dates, confirm the specification, make the creative, approve and go live, then check that your ad is running.</p>
<ol class="steps">{''.join(f'<li><b>{t}</b><p>{d}</p></li>' for t, d in steps)}</ol>
<h2 class="display">Creative checklist for {e(sh)}</h2>
<ul><li>Large text with high contrast; people see it for a few seconds.</li><li>Your logo, one message and one action.</li><li>Movement in the first second for video ads.</li><li>A local cue, such as the {e(sh)} branch or a nearby landmark, makes the ad feel relevant.</li></ul>
<p>Related: <a href="/locations/{aid}/advertising-cost/">{e(sh)} cost guide</a> · <a href="/locations/{aid}/faq/">{e(sh)} FAQ</a></p></section>'''
    page(f'/locations/{aid}/campaign-planning/', TOPICS[3][2].format(n=sh), f'Step-by-step plan for an LED billboard campaign in {n}: goals, screens, dates, specification, creative checklist and reporting.',
         TOPICS[3][3].format(n=sh), body, base_crumb + [('Campaign planning', f'/locations/{aid}/campaign-planning/')], (org(), howto))

    # ---- Topic 5: FAQ
    body = f'''{topic_nav(a, 'faq')}
<section class="wrap prose">{''.join(f'<h2 class="q">{e(q)}</h2><p>{ans}</p>' for q, ans in qas)}</section>'''
    page(f'/locations/{aid}/faq/', TOPICS[4][2].format(n=sh), f'Answers about LED billboard advertising in {n}: screens, cost, facing, timing, file formats and booking with LED AD PRO.',
         TOPICS[4][3].format(n=sh), body, base_crumb + [('FAQ', f'/locations/{aid}/faq/')], (org(), faq_ld(qas)))
    OG_DEFAULT[0] = '/assets/brand/og-image.png'


def build_hub():
    total = sum(len(a['p']) for a in LOCS)
    groups = [('Dhaka', [a for a in LOCS if a['kind'] == 'dhaka']), ('Other cities', [a for a in LOCS if a['kind'] != 'dhaka'])]
    body = '<section class="wrap"><p class="answer">LED AD PRO lists <strong>' + str(total) + ' LED screens</strong> in ' + str(len(LOCS)) + ' areas across Bangladesh, plus ' + str(len(STATIC)) + ' static billboards in Dhaka. Choose an area to see every screen with photos, costs and booking steps.</p></section>'
    for g, items in groups:
        body += f'<section class="wrap"><h2 class="display">{g}</h2><div class="tiles">' + ''.join(
            f'<a class="tile img" href="/locations/{a["id"]}/"><img loading="lazy" src="{img(a["img"])}" alt="LED billboard in {e(a["name"])}" width="1200" height="800"><b>{e(a["name"])}</b><span>{screens(a, len(a["p"]))} &#9656;</span></a>' for a in items) + '</div></section>'
    il = {'@type': 'ItemList', 'name': 'LED AD PRO locations', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f'{SITE}/locations/{a["id"]}/', 'name': a['name']} for i, a in enumerate(LOCS)]}
    page('/locations/', f'LED Billboard Locations in Bangladesh ({total} Screens) | LED AD PRO', f'All {total} LED billboard screens by area: Gulshan, Dhanmondi, Mirpur, Mohakhali, Airport, Chattogram, Sylhet and more. Photos, facing and costs.',
         'LED billboard locations in Bangladesh', body, [('Home', '/'), ('Locations', '/locations/')], (org(), il))


def client_logo(c):  # sites/ledadpro-v2/img/clients/<slug>.svg|png|webp|jpg, if we have it
    slug = re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')
    for ext in ('svg', 'png', 'webp', 'jpg'):
        if (SRC / 'img' / 'clients' / f'{slug}.{ext}').exists():
            return f'/assets/img/clients/{slug}.{ext}'


def client_wall():
    out = [f'<span class="logo-tile" title="{e(c)}"><img src="{client_logo(c)}" alt="{e(c)} logo" loading="lazy"></span>' for c in CLIENTS if client_logo(c)]
    out.append('<a class="more-tile" href="/clients/"><b>400+</b>brands served</a>')
    return '<div class="wall">' + ''.join(out) + '</div>'


def build_services():
    for slug, s in SERVICES.items():
        steps = s['how']
        howto = {'@type': 'HowTo', 'name': f'How to book {s["name"]}', 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': t, 'text': d} for i, (t, d) in enumerate(steps)]}
        svc = {'@type': 'Service', 'name': s['name'], 'serviceType': 'Digital out-of-home advertising', 'provider': {'@id': SITE + '/#business'}, 'areaServed': {'@type': 'Country', 'name': 'Bangladesh'}}
        qas = [(q, a) for q, a in s['faq']]
        other = [x for x in SERVICES if x != slug][0]
        body = f'''<section class="wrap two"><div><p class="answer">{s['answer']}</p>
<h2 class="display">Who it reaches</h2><ul class="ticks">{''.join(f'<li>{e(w)}</li>' for w in s['who'])}</ul></div>
<figure class="hero-ph"><img src="/assets/{s['img']}" alt="{e(s['name'])}" width="1200" height="800"></figure></section>
<section class="wrap"><h2 class="display">Brands our team has delivered for</h2>{client_wall()}<p class="small-note">LED AD PRO is the official LED partner to AD Pro. <a href="/clients/">See campaigns &#9656;</a></p></section>
<section class="wrap prose"><h2 class="display">How it works</h2><ol class="steps">{''.join(f'<li><b>{e(t)}</b><p>{e(d)}</p></li>' for t, d in steps)}</ol></section>
{f'<section class="wrap"><figure class="hero-ph wide"><img loading="lazy" src="/assets/{s["img2"]}" alt="{e(s["name"])} in Dhaka" width="1200" height="640"></figure></section>' if s.get('img2') else ''}
<section class="wrap prose"><h2 class="display">Questions answered</h2>{''.join(f'<h2 class="q">{e(q)}</h2><p>{e(a)}</p>' for q, a in qas)}
<p>Also see: <a href="/services/{other}/">{e(SERVICES[other]['name'])}</a> · <a href="/locations/">LED billboard locations</a> · <a href="/clients/">Our clients</a></p></section>'''
        page(f'/services/{slug}/', s['title'], s['desc'], s['name'], body, [('Home', '/'), ('Services', '/#services'), (s['short'], f'/services/{slug}/')], (org(), svc, howto, faq_ld(qas)))


def build_clients():
    cases = ''.join(f'''<figure class="sc"><img loading="lazy" src="/assets/img/work/{f}" alt="{e(b)}: {e(w)}, {e(l)}" width="1200" height="800"><figcaption><b>{e(b)}</b><span>{e(w)} · {e(l)}</span></figcaption></figure>''' for f, b, w, l in CASES)
    body = f'''<section class="wrap"><p class="answer">Our team has planned and delivered outdoor and LED campaigns for <strong>400+ brands</strong> in Bangladesh, from international names such as BMW, Emirates and Malaysia Airlines to Aarong, Royal Enfield, Haier and Singer Beko. LED AD PRO is the <strong>official LED partner to AD Pro</strong>.</p>
<div class="stats"><div><b>400+</b><span>brands served by our team</span></div><div><b>{sum(len(a['p']) for a in LOCS)}</b><span>LED screens in our network</span></div><div><b>{len(LOCS)}</b><span>areas</span></div><div><b>10</b><span>cities</span></div></div></section>
<section class="wrap"><h2 class="display">Brands we have delivered for</h2>{client_wall()}</section>
<section class="wrap"><h2 class="display">Campaigns on the street</h2><div class="grid">{cases}</div></section>
<section class="wrap prose"><h2 class="display">What we deliver</h2><ul class="ticks"><li><a href="/locations/">LED billboards</a> in {len(LOCS)} areas across Bangladesh</li><li><a href="/services/metro-rail-led-advertising/">Metro Rail LED</a> screens inside Dhaka Metro coaches</li><li><a href="/services/led-caravan/">LED Caravan</a> mobile screens for roadshows and district tours</li><li>Static billboards, custom LED displays, event screens and store-launch branding</li></ul></section>'''
    il = {'@type': 'ItemList', 'name': 'Brands LED AD PRO\'s team has delivered for', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': c} for i, c in enumerate(CLIENTS)]}
    page('/clients/', 'Our Clients: BMW, Emirates, Aarong, Royal Enfield & 400+ Brands | LED AD PRO',
         'Brands our team has delivered outdoor and LED campaigns for: BMW, Emirates, Malaysia Airlines, Aarong, Royal Enfield, Haier, Singer Beko, ACI and 400+ more.',
         'Brands that trust our team', body, [('Home', '/'), ('Clients', '/clients/')], (org(), il))


def logo_strip():
    logos = [(c, client_logo(c)) for c in CLIENTS if client_logo(c)]
    if not logos:
        return ''
    imgs = ''.join(f'<img src="{src}" alt="{e(c)}" loading="lazy">' for c, src in logos)
    return (f'<section class="trusted" aria-label="Brands our team has delivered campaigns for">'
            f'<p>Trusted by brands like these · <a href="/clients/">see the work</a></p>'
            f'<div class="logo-row">{imgs}<span aria-hidden="true" style="display:contents">{imgs}</span></div></section>')


def build_home():
    s = (SRC / 'index.html').read_text()
    s = s.replace('<meta name="robots" content="noindex">', '<meta name="robots" content="index,follow,max-image-preview:large">\n<link rel="canonical" href="https://ledadpro.com/">')
    s = s.replace('<title>LED AD PRO | Digital Out of Home Advertising in Bangladesh</title>', '<title>LED AD PRO | LED Billboard Advertising in Dhaka &amp; Bangladesh</title>')
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="LED billboard advertising on {sum(len(a["p"]) for a in LOCS)} screens in Dhaka, Chattogram, Sylhet and more. Every location with photos, prices from 100 BDT/min. Call {PHONE_TXT}.">', s)
    s = re.sub(r'href="style\.css\?v=\d+"', 'href="/assets/style.css?v=10"', s)
    s = re.sub(r'src="locations\.js\?v=\d+"', 'src="/assets/locations.js?v=2"', s)
    s = re.sub(r'src="main\.js\?v=\d+"', 'src="/assets/main.js?v=9"', s)
    s = s.replace('src="img/', 'src="/assets/img/').replace('src="brand/', 'src="/assets/brand/').replace('data-img="img/', 'data-img="/assets/img/').replace('href="brand/', 'href="/assets/brand/')
    og = f'<meta property="og:type" content="website"><meta property="og:title" content="LED AD PRO | LED Billboard Advertising in Bangladesh"><meta property="og:url" content="{SITE}/"><meta property="og:image" content="{SITE}/assets/brand/og-image.png"><meta name="twitter:card" content="summary_large_image">'
    web = {'@type': 'WebSite', 'name': 'LED AD PRO', 'url': SITE + '/'}
    s = s.replace('</head>', og + ld(org(), web) + '\n</head>', 1)
    # crawlable links from the homepage to every location page
    links = '<nav class="foot-locs" aria-label="All locations">' + ''.join(f'<a href="/locations/{a["id"]}/">{e(a["short"])}</a>' for a in LOCS) + '</nav>'
    s = s.replace('<div class="foot-bar">', links + '\n    <div class="foot-bar">', 1)
    s = s.replace('<!--CLIENT-LOGOS-->', logo_strip(), 1)
    # SEO audit 2026-11: keyword H1 text, homepage FAQ, links to the new guide pages
    s = s.replace('<span class="sr-only">LED AD PRO: LED billboards and screens in Dhaka</span>', '<span class="sr-only">LED billboard advertising in Dhaka and across Bangladesh</span>', 1)
    import ledadpro_guides
    faq_html, faq_schema = ledadpro_guides.home_faq(sys.modules[__name__])
    s = s.replace('  <!-- Cyan band -->', faq_html + '\n  <!-- Cyan band -->', 1)
    s = s.replace('</head>', ld(faq_schema) + '\n</head>', 1)
    s = s.replace('<a href="#contact">Contact us</a></nav>', '<a href="/pricing/">Pricing</a><a href="/led-screen-rental/">LED screen rental</a><a href="/about/">About</a><a href="/guides/how-to-choose-a-billboard-location/">Choosing a location</a><a href="#contact">Contact us</a></nav>', 1)
    (OUT / 'index.html').write_text(s)
    PAGES.append(('/', 'Home'))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'assets').mkdir(parents=True)
    shutil.copytree(SRC / 'img', OUT / 'assets/img')
    shutil.copytree(SRC / 'brand', OUT / 'assets/brand')
    for f in ('style.css', 'main.js'):
        shutil.copy(SRC / f, OUT / 'assets' / f)
    shutil.copy(ROOT / 'sites/ledadpro-pages.css', OUT / 'assets/pages.css')
    (OUT / 'assets/locations.js').write_text(data.replace('"img/', '"/assets/img/'))
    build_home(); build_hub(); build_services(); build_clients()
    import ledadpro_guides
    ledadpro_guides.build(sys.modules[__name__])
    import ledadpro_redirects
    (OUT / 'redirects.conf').write_text(ledadpro_redirects.rules())  # read by vps/live-deploy.sh, not served
    for a in LOCS:
        build_area(a)
    sm = ''.join(f'<url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>' for p, _ in PAGES)
    (OUT / 'sitemap-ledadpro.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    llms = [f'# LED AD PRO\n\n> LED billboard and digital out-of-home advertising in Bangladesh: {sum(len(a["p"]) for a in LOCS)} LED screens in {len(LOCS)} areas, plus static billboards, custom LED displays and event screens. Office: {ADDRESS}. Sales and marketing {PHONE_TXT}, office {OFFICE_TXT}, {EMAIL}.\n\n## Locations\n']
    llms += [f'- [{a["name"]}]({SITE}/locations/{a["id"]}/): {screens(a, len(a["p"]))}; {AREA[a["id"]][0]}\n' for a in LOCS]
    NL = chr(10)
    llms += [NL + '## Prices, services and guides' + NL,
             f'- [Billboard advertising cost in Bangladesh]({SITE}/pricing/): LED billboards about 100-600 BDT per minute; static billboard rent about 500-3,000 BDT per square foot' + NL,
             f'- [LED screen rental]({SITE}/led-screen-rental/): LED screens and video walls for events, with setup and operator' + NL,
             f'- [LED caravan / LED van advertising]({SITE}/services/led-caravan/): mobile LED screen vehicle for roadshows' + NL,
             f'- [Metro Rail LED advertising]({SITE}/services/metro-rail-led-advertising/): screens inside Dhaka Metro coaches' + NL,
             f'- [How to choose a billboard location]({SITE}/guides/how-to-choose-a-billboard-location/)' + NL,
             f'- [About LED AD PRO]({SITE}/about/) · [Clients]({SITE}/clients/)' + NL]
    (OUT / 'llms.txt').write_text(''.join(llms))
    print(len(PAGES), 'pages')


if __name__ == '__main__':
    main()
