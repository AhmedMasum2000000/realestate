#!/usr/bin/python3
"""ledadhub.com: one-page agency-style site (giant wordmark hero with a photo reel, statement, highlights,
logo strip, at-a-glance cards, approach, photo mosaic, CTA, menu overlay, wordmark footer).
Facts come from the LED AD PRO data (locations.js, ledadpro_extra.py). Own photos only.
Writes sites/ledadhub/; deploy with vps-run site-deploy.sh "ledadhub.com ledadhub"."""
import json, re, shutil, sys
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from ledadpro_extra import CLIENTS, CASES  # noqa: E402

V2 = ROOT / 'sites/ledadpro-v2'
OUT = ROOT / 'sites/ledadhub'
SITE = 'https://ledadhub.com'
PHONE, PHONE_TXT = '+8801958503753', '+880 1958-503753'
OFFICE, OFFICE_TXT = '+8801316743003', '+880 1316-743003'
EMAIL = 'info@ledadpro.com'
ADDRESS = 'Flat A1, House 99 (1st floor), Road 10/2, Block D, Niketon, Gulshan 1, Dhaka'
WA = f'https://wa.me/{PHONE[1:]}?text=' + 'Hi%20LED%20AD%20Hub%2C%20I%20want%20to%20book%20LED%20screens.'

src = (V2 / 'locations.js').read_text()
LOCS, _ = json.JSONDecoder().raw_decode(src, src.index('window.LOCS=') + len('window.LOCS='))
SCREENS = sum(len(a['p']) for a in LOCS)
AREAS = len(LOCS)
CITIES = 1 + sum(1 for a in LOCS if a['kind'] == 'city')

REEL = ['loc/gulshan-circle-2-1200.webp', 'static/banani-expressway-static.webp', 'loc/mirpur-10-circle-4-screens-1200.webp',
        'loc/shimanto-square-6-led-screens-1200.webp', 'static/bijoy-sarani-static.webp', 'loc/sylhet-bondor-bazar-1200.webp']
MOSAIC = [('loc/science-lab-circle-1200.webp', 'Science Lab'), ('loc/sonargaon-mor-karwan-bazar-1200.webp', 'Karwan Bazar'),
          ('loc/airport-entrance-banani-facing-1200.webp', 'Airport road'), ('loc/dhanmondi-27-opposite-of-rapa-plaza-1200.webp', 'Dhanmondi 27'),
          ('loc/agrabad-circle-chittagong-1200.webp', 'Chattogram'), ('loc/sughondha-point-coxs-bazar-1200.webp', 'Cox’s Bazar'),
          ('loc/rajshahi-shaheb-bazar-2-screens-both-sides-1200.webp', 'Rajshahi'), ('loc/sks-tower-exit-gate-mohakhali-1200.webp', 'Mohakhali'),
          ('static/mirpur-metro-static.webp', 'Mirpur'), ('loc/kandirpar-cumilla-1200.webp', 'Cumilla'), ('loc/shapla-mor-rangpur-1200.webp', 'Rangpur'),
          ('loc/police-plaza-bogura-1200.webp', 'Bogura')]
WORDS = ['Gulshan', 'Mirpur', 'Dhanmondi', 'Sylhet', 'Chattogram', 'Cox’s Bazar', 'Rajshahi', 'Rangpur', 'Cumilla', 'Bogura', 'Feni', 'Narayanganj']


def slug(c):
    return re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')


def logo_file(c):
    for ext in ('svg', 'png'):
        f = V2 / 'img/clients' / f'{slug(c)}.{ext}'
        if f.exists():
            return f


if OUT.exists():
    shutil.rmtree(OUT)
for d in ('img/work', 'img/loc', 'img/static', 'img/clients', 'brand'):
    (OUT / d).mkdir(parents=True)
for f, *_ in CASES:
    shutil.copy(V2 / 'img/work' / f, OUT / 'img/work' / f)
for f in REEL + [m for m, _ in MOSAIC]:
    shutil.copy(V2 / 'img' / f, OUT / 'img' / f)
LOGOS = [(c, logo_file(c)) for c in CLIENTS if logo_file(c)]
for c, f in LOGOS:
    shutil.copy(f, OUT / 'img/clients' / f.name)
for f in ('favicon.svg', 'favicon-32.png', 'favicon-180.png', 'favicon.ico'):
    shutil.copy(V2 / 'brand' / f, OUT / 'brand' / f)
shutil.copy(OUT / 'brand/favicon.ico', OUT / 'favicon.ico')

reel_html = ''.join(f'<img src="img/{f}" alt="" {"" if i else "fetchpriority=high"} {"loading=lazy" if i > 1 else ""} width="1200" height="800" class="{"on" if i == 0 else ""}">' for i, f in enumerate(REEL))
big, *small = CASES
hl_html = f'''<a class="card big" href="https://ledadpro.com/clients/" rel="noopener"><img loading="lazy" decoding="async" src="img/work/{big[0]}" alt="{e(big[1])} campaign on LED billboards, {e(big[3])}" width="1600" height="1000"><span><b>{e(big[1])}</b>{e(big[2])}</span></a>
<div class="pair">''' + ''.join(f'<a class="card" href="https://ledadpro.com/clients/" rel="noopener"><img loading="lazy" decoding="async" src="img/work/{f}" alt="{e(b)} campaign, {e(w)}" width="1600" height="1000"><span><b>{e(b)}</b>{e(w)}</span></a>' for f, b, _, w in small[:2]) + '</div>'
logos_html = ''.join(f'<li><img loading="lazy" decoding="async" src="img/clients/{f.name}" alt="{e(c)}"></li>' for c, f in LOGOS)
mosaic_html = ''
for i in range(24):
    if i % 2 == (i // 6) % 2:
        f, cap = MOSAIC[(i // 2) % len(MOSAIC)]
        mosaic_html += f'<figure><img loading="lazy" decoding="async" src="img/{f}" alt="LED billboard, {e(cap)}" width="600" height="600"></figure>'
    else:
        mosaic_html += f'<p>{e(WORDS[(i // 2) % len(WORDS)])}</p>'

schema = json.dumps({
    "@context": "https://schema.org", "@type": "AdvertisingAgency", "name": "LED AD Hub", "url": SITE + '/', "telephone": PHONE, "email": EMAIL,
    "address": {"@type": "PostalAddress", "streetAddress": "Flat A1, House 99, Road 10/2, Block D, Niketon", "addressLocality": "Gulshan 1, Dhaka", "addressCountry": "BD"},
    "areaServed": "Bangladesh", "parentOrganization": {"@type": "Organization", "name": "LED AD PRO", "url": "https://ledadpro.com/"},
    "contactPoint": [{"@type": "ContactPoint", "telephone": PHONE, "contactType": "sales", "areaServed": "BD"}]}, ensure_ascii=False)

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LED AD Hub: Book LED Billboards across Bangladesh</title>
<meta name="description" content="LED AD Hub is the one place to book LED billboard advertising in Bangladesh: {SCREENS} screens in {AREAS} areas and {CITIES} cities, Metro Rail LED and LED caravans, planned and run by the LED AD PRO team. Call +880 1958-503753.">
<link rel="canonical" href="{SITE}/">
<meta property="og:title" content="LED AD Hub"><meta property="og:description" content="{SCREENS} LED screens. {AREAS} areas. {CITIES} cities. One call."><meta property="og:image" content="{SITE}/img/work/royal-enfield-gulshan-2.jpg"><meta property="og:url" content="{SITE}/">
<meta name="theme-color" content="#0b0b0b">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="brand/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="brand/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@900&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v=1">
<script type="application/ld+json">{schema}</script>
</head>
<body>
<header class="bar" id="bar">
  <p class="tag"><span class="t1">The LED billboard hub of Bangladesh</span><span class="t2" aria-hidden="true">LED AD HUB</span></p>
  <button type="button" class="menu-btn" id="menu-btn" aria-expanded="false" aria-controls="menu"><span>Menu</span><span>Close</span></button>
</header>
<nav class="menu" id="menu" hidden>
  <ul class="menu-links">
    <li><a href="#top">Home</a></li><li><a href="#work">Work</a></li><li><a href="#screens">Screens</a></li><li><a href="#approach">Approach</a></li><li><a href="#contact">Contact</a></li>
  </ul>
  <div class="menu-side">
    <p><a href="https://ledadpro.com/" rel="noopener">LED AD PRO &nearr;</a><a href="{WA}" rel="noopener" target="_blank">WhatsApp &nearr;</a></p>
    <p><span>New business:</span><a href="tel:{PHONE}">{PHONE_TXT}</a><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p class="mut">&copy;15&ndash;26</p>
  </div>
</nav>

<main id="top">
  <section class="hero">
    <h1 class="mark" aria-label="LED AD Hub"><span data-fit>LED AD HUB</span></h1>
    <div class="hero-row">
      <p>Billboards, Metro,<br>Caravans.</p>
      <p>LED advertising network<br>across Bangladesh.</p>
      <a class="down" href="#reel" aria-label="Scroll down">&darr;</a>
    </div>
  </section>

  <section class="reel" id="reel" aria-label="Our screens">
    <div class="reel-frame">{reel_html}</div>
    <p class="reel-title">Live reel</p>
    <p class="reel-note">Our own screens, as they stand today</p>
  </section>

  <section class="statement rv">
    <p>We put brands on the junctions Bangladesh already drives through every day: <b>{SCREENS} LED screens</b>, Metro Rail LED and LED caravans, planned, booked and proven, all under one roof. Explore <a href="#screens">our screens</a>.</p>
  </section>

  <section class="two rv">
    <h2>Every junction,<br>one call.</h2>
    <div>
      <p>Since 2015 the LED AD PRO team has run outdoor campaigns for 400+ brands, from BMW, Emirates and Coca-Cola to Aarong, Walton and Square.</p>
      <p>We pick the junctions that match your buyers, fit your creative to each screen, and send photos of your ad running the day it goes live.</p>
      <a class="arrow" href="https://ledadpro.com/" rel="noopener">Learn more &nearr;</a>
    </div>
  </section>

  <section class="hl rv" id="work">
    <div class="row"><h2>Highlights</h2><a class="arrow" href="https://ledadpro.com/clients/" rel="noopener">See the work &nearr;</a></div>
    {hl_html}
  </section>

  <section class="strip" aria-label="Brands we have worked for">
    <ul class="logos">{logos_html}</ul>
    <ul class="logos" aria-hidden="true">{logos_html}</ul>
  </section>

  <section class="glance rv" id="screens">
    <div class="row"><h2>LED AD Hub at a glance.</h2><a href="mailto:{EMAIL}">{EMAIL}</a></div>
    <div class="cards">
      <div class="gc dark"><p><b>{SCREENS}</b> LED screens in {AREAS} areas of Dhaka and {CITIES - 1} more cities</p><span>LED AD HUB</span></div>
      <figure class="gc photo"><img loading="lazy" decoding="async" src="img/loc/mirpur-10-circle-4-screens-1200.webp" alt="LED screens at Mirpur-10 circle" width="1200" height="800"><figcaption>Mirpur-10<br>Four screens, one roundabout</figcaption></figure>
      <div class="gc light"><p><b>400+</b> brands served by our team since 2015</p></div>
      <div class="gc light"><p><b>11</b> years on air on 1 December 2026</p></div>
    </div>
  </section>

  <section class="approach rv" id="approach">
    <h2>Our approach.</h2>
    <div class="cols">
      <p class="lead">A simple rule:<br>the right junction beats a big budget.</p>
      <div>
        <p>We plan around where your buyers already are. A screen on Gulshan Circle-2 at 6 pm, a board on the airport road, four screens round Mirpur-10: each one chosen for who passes it, not for how it looks on a map.</p>
        <p>Then we make it work. Creative cut to each screen size, a written schedule, and proof photos when it is live. Attention and performance; you need both.</p>
      </div>
    </div>
    <div class="mosaic" aria-hidden="true">{mosaic_html}</div>
    <a class="cta" href="{WA}" rel="noopener" target="_blank">Get a quote</a>
  </section>
</main>

<footer class="foot" id="contact">
  <div class="fcols">
    <p><span>New business</span><a href="tel:{PHONE}">{PHONE_TXT}</a><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p><span>Office</span>{e(ADDRESS)}<a href="tel:{OFFICE}">{OFFICE_TXT}</a></p>
    <p><span>Talk to us now</span><a href="{WA}" rel="noopener" target="_blank">WhatsApp &nearr;</a><a href="https://ledadpro.com/" rel="noopener">ledadpro.com &nearr;</a></p>
    <p><span>Dhaka, Bangladesh</span>Official LED partner to AD Pro<br>&copy;15&ndash;26 LED AD Hub</p>
  </div>
  <p class="mark" aria-hidden="true"><span data-fit>LED AD HUB</span></p>
</footer>
<script src="main.js?v=1" defer></script>
</body>
</html>
'''

css = '''*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0b0b0b;--fg:#f3f3f3;--mute:#8d8d8d;--line:#262626;--paper:#f3f3f1;--ink:#111;--pad:clamp(16px,2.4vw,36px)}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{background:var(--bg);color:var(--fg);font:400 14px/1.4 Inter,"Helvetica Neue",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%;height:auto}
button{font:inherit;color:inherit;background:none;border:0;cursor:pointer}
h2{font-weight:400;font-size:inherit}
.arrow:hover,.two a:hover,.row a:hover{text-decoration:underline;text-underline-offset:3px}

/* top bar + menu */
.bar{position:fixed;top:0;left:0;right:0;z-index:20;display:flex;justify-content:space-between;align-items:center;padding:14px var(--pad);mix-blend-mode:difference;color:#fff}
.bar .tag{position:relative;height:1.4em;overflow:hidden}
.bar .tag span{display:block;transition:transform .5s cubic-bezier(.7,0,.2,1)}
.bar .t2{font:900 15px/1.4 Archivo,Inter,sans-serif;letter-spacing:-.02em}
.bar.scrolled .tag span{transform:translateY(-100%)}
.menu-btn{border:1px solid currentColor;border-radius:999px;padding:0 14px;display:block;position:relative;overflow:hidden;height:30px}
.menu-btn span{display:block;line-height:30px;transition:transform .4s cubic-bezier(.7,0,.2,1)}
.menu-btn[aria-expanded="true"] span{transform:translateY(-100%)}
.menu{position:fixed;inset:0;z-index:15;background:var(--bg);color:var(--fg);padding:72px var(--pad) var(--pad);display:grid;grid-template-columns:1fr 1fr;align-content:start;gap:40px var(--pad)}
.menu[hidden]{display:none}
.menu-links{list-style:none;font-size:clamp(28px,4vw,56px);line-height:1.15;letter-spacing:-.02em}
.menu-links a{display:block;transform:translateY(20px);opacity:0;animation:up .6s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--i,0)*60ms)}
.menu-side p{display:grid;gap:6px;margin-bottom:24px}
.menu-side span{color:var(--mute)}
.menu-side a:hover{text-decoration:underline}
.mut{color:var(--mute)}
@keyframes up{to{transform:none;opacity:1}}
body.menu-open{overflow:hidden}

/* wordmark */
.mark{font:900 100px/.84 Archivo,Inter,sans-serif;letter-spacing:-.045em;white-space:nowrap;overflow:hidden;line-height:.84}
.mark span{display:inline-block;padding:0 .06em 0 .02em;transform:translateY(110%);animation:rise 1s cubic-bezier(.2,.9,.2,1) .15s forwards}
@keyframes rise{to{transform:none}}
.foot .mark span{animation:none;transform:none}

/* hero */
.hero{min-height:100svh;display:flex;flex-direction:column;justify-content:space-between;padding:60px var(--pad) var(--pad)}
.hero .mark{margin:0 calc(var(--pad)*-.15)}
.hero-row{display:grid;grid-template-columns:1fr 1fr auto;gap:var(--pad);align-items:end;padding-top:40px}
.hero-row p{max-width:16em}
.down{font-size:20px;line-height:1}

/* reel */
.reel{position:relative;margin:0 var(--pad);aspect-ratio:16/10;max-height:86vh;overflow:hidden;background:#161616}
.reel-frame{position:absolute;inset:0}
.reel-frame img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transform:scale(1.06);transition:opacity 1.4s ease,transform 7s linear}
.reel-frame img.on{opacity:1;transform:scale(1)}
.reel-title{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);font-size:clamp(28px,5vw,64px);letter-spacing:-.02em;text-decoration:underline;text-underline-offset:.12em;text-decoration-thickness:1px;color:#fff;text-shadow:0 2px 24px rgba(0,0,0,.4)}
.reel-note{position:absolute;left:var(--pad);bottom:var(--pad);color:#fff;text-shadow:0 1px 12px rgba(0,0,0,.5)}
@media (max-width:760px){.reel{aspect-ratio:4/5;margin:0}}

/* text blocks */
.statement{padding:clamp(80px,14vh,160px) var(--pad);font-size:clamp(22px,2.9vw,44px);line-height:1.25;letter-spacing:-.015em;text-align:center}
.statement p{max-width:30em;margin:0 auto}
.statement b{font-weight:500}
.statement a{text-decoration:underline;text-underline-offset:.12em;text-decoration-thickness:1px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:var(--pad);padding:0 var(--pad) clamp(80px,12vh,140px);border-top:1px solid var(--line);padding-top:18px}
.two h2{max-width:14em}
.two div{max-width:30em;display:grid;gap:14px}
.arrow{display:inline-block}

/* highlights */
.hl{padding:0 var(--pad) clamp(60px,10vh,120px)}
.row{display:flex;justify-content:space-between;align-items:baseline;padding:18px 0 14px;border-top:1px solid var(--line)}
.card{position:relative;display:block;overflow:hidden;background:#161616}
.card img{width:100%;aspect-ratio:16/10;object-fit:cover;transition:transform 1.2s cubic-bezier(.2,.8,.2,1)}
.card:hover img{transform:scale(1.03)}
.card span{position:absolute;left:18px;bottom:16px;color:#fff;text-shadow:0 1px 10px rgba(0,0,0,.5)}
.card span b{display:block;font-weight:500}
.card.big img{aspect-ratio:16/9}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}
.pair .card img{aspect-ratio:4/5}

/* logo strip */
.strip{background:var(--paper);display:flex;overflow:hidden;padding:26px 0}
.logos{list-style:none;display:flex;flex-shrink:0;align-items:center;gap:clamp(40px,6vw,96px);padding-right:clamp(40px,6vw,96px);animation:slide 60s linear infinite}
.logos li{height:26px;width:96px;display:grid;place-items:center}
.logos img{max-height:100%;max-width:100%;width:auto;filter:grayscale(1)}
@keyframes slide{to{transform:translateX(-100%)}}
.strip:hover .logos{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.logos{animation:none}}

/* glance */
.glance{background:var(--paper);color:var(--ink);padding:0 var(--pad) clamp(60px,10vh,120px)}
.glance .row{border-top-color:#d9d9d6}
.cards{display:grid;grid-auto-flow:column;grid-auto-columns:min(78vw,300px);gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;padding:6px 0 10px;scrollbar-width:none}
.cards::-webkit-scrollbar{display:none}
.gc{scroll-snap-align:start;border-radius:14px;aspect-ratio:1;padding:18px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;position:relative}
.gc b{display:block;font-size:40px;font-weight:500;letter-spacing:-.03em;line-height:1;margin-bottom:10px}
.gc.dark{background:var(--bg);color:var(--fg)}
.gc.dark span{font:900 13px/1 Archivo,Inter,sans-serif;letter-spacing:-.02em}
.gc.light{background:#fff;border:1px solid #e4e4e1}
.gc.photo{padding:0;color:#fff}
.gc.photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.gc.photo figcaption{position:relative;padding:18px;text-shadow:0 1px 10px rgba(0,0,0,.6)}
@media (min-width:900px){.cards{grid-auto-flow:row;grid-template-columns:repeat(4,1fr);overflow:visible}}

/* approach + mosaic + cta */
.approach{background:var(--paper);color:var(--ink);padding:0 var(--pad) clamp(60px,10vh,120px)}
.approach h2{font-size:clamp(30px,4.4vw,60px);letter-spacing:-.03em;line-height:1;padding:18px 0 40px;border-top:1px solid #d9d9d6}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:var(--pad);max-width:1100px}
.cols .lead{max-width:14em}
.cols div{display:grid;gap:14px;max-width:30em}
.mosaic{display:grid;grid-template-columns:repeat(6,1fr);margin:clamp(50px,8vh,100px) auto;max-width:900px}
.mosaic figure,.mosaic p{aspect-ratio:1;overflow:hidden}
.mosaic img{width:100%;height:100%;object-fit:cover}
.mosaic p{display:grid;place-items:center;font-size:11px;color:var(--mute);background:#fff;border:1px solid #ecece9}
.cta{display:block;width:max-content;margin:0 auto;font-size:clamp(28px,4vw,56px);letter-spacing:-.02em;text-decoration:underline;text-underline-offset:.14em;text-decoration-thickness:1px}
.cta:hover{text-decoration-thickness:2px}

/* footer */
.foot{padding:40px var(--pad) 0;overflow:hidden}
.fcols{display:grid;grid-template-columns:repeat(2,1fr);gap:28px var(--pad);padding-bottom:60px}
.fcols p{display:grid;gap:4px;align-content:start}
.fcols span{color:var(--mute);margin-bottom:4px}
.fcols a:hover{text-decoration:underline}
.foot .mark{margin:0 calc(var(--pad)*-.15) -.02em}
@media (min-width:900px){.fcols{grid-template-columns:repeat(4,1fr)}}

/* reveal */
.rv{opacity:0;transform:translateY(24px);transition:opacity .8s ease,transform .8s cubic-bezier(.2,.8,.2,1)}
.rv.in{opacity:1;transform:none}
@media (prefers-reduced-motion:reduce){.rv{opacity:1;transform:none}.mark span{animation:none;transform:none}.reel-frame img{transition:none}}

@media (max-width:760px){
  .hero{padding-top:56px}
  .hero-row{grid-template-columns:1fr 1fr auto;font-size:13px}
  .two,.cols{grid-template-columns:1fr}
  .menu{grid-template-columns:1fr}
  .mosaic{grid-template-columns:repeat(4,1fr)}
  .mosaic figure:nth-child(n+17),.mosaic p:nth-child(n+17){display:none}
}
'''

js = r'''(function () {
  var d = document, b = d.body, reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // wordmarks fill the width
  var marks = [].slice.call(d.querySelectorAll('[data-fit]'));
  function fit() {
    marks.forEach(function (s) {
      var box = s.parentNode.clientWidth; if (!box) return;
      s.style.fontSize = '100px'; s.style.fontSize = (100 * box / s.offsetWidth * 0.995).toFixed(1) + 'px';
    });
  }
  fit(); addEventListener('resize', fit);
  if (d.fonts) { d.fonts.ready.then(fit); d.fonts.addEventListener('loadingdone', fit); if (d.fonts.load) d.fonts.load('900 100px Archivo').then(fit, fit); }
  setTimeout(fit, 2500);

  // top bar swaps the tagline for the small wordmark once the hero is gone
  var bar = d.getElementById('bar'), hero = d.querySelector('.hero');
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { bar.classList.toggle('scrolled', !es[0].isIntersecting); }, { threshold: 0.15 }).observe(hero);

  // menu overlay
  var btn = d.getElementById('menu-btn'), menu = d.getElementById('menu');
  [].forEach.call(menu.querySelectorAll('.menu-links a'), function (a, i) { a.style.setProperty('--i', i); });
  function toggle(open) {
    menu.hidden = !open; btn.setAttribute('aria-expanded', open); b.classList.toggle('menu-open', open);
  }
  btn.addEventListener('click', function () { toggle(menu.hidden); });
  menu.addEventListener('click', function (ev) { if (ev.target.closest('a')) toggle(false); });
  addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && !menu.hidden) toggle(false); });

  // reel: crossfade our own screen photos
  var slides = [].slice.call(d.querySelectorAll('.reel-frame img')), cur = 0;
  if (slides.length > 1 && !reduce) setInterval(function () {
    slides[cur].classList.remove('on'); cur = (cur + 1) % slides.length; slides[cur].classList.add('on');
  }, 4200);

  // reveal sections as they come in
  var rv = [].slice.call(d.querySelectorAll('.rv'));
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -10% 0px' });
    rv.forEach(function (x) { io.observe(x); });
  } else rv.forEach(function (x) { x.classList.add('in'); });
})();
'''

htaccess = '''DirectoryIndex index.html
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/\\.well-known/
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} !^ledadhub\\.com$ [NC]
RewriteRule ^ https://ledadhub.com%{REQUEST_URI} [L,R=301]
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType image/webp "access plus 30 days"
ExpiresByType image/jpeg "access plus 30 days"
ExpiresByType image/png "access plus 30 days"
ExpiresByType image/svg+xml "access plus 30 days"
ExpiresByType text/css "access plus 7 days"
ExpiresByType application/javascript "access plus 7 days"
</IfModule>
'''

(OUT / 'index.html').write_text(html)
(OUT / 'style.css').write_text(css)
(OUT / 'main.js').write_text(js)
(OUT / '.htaccess').write_text(htaccess)
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
(OUT / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE}/</loc></url></urlset>\n')
print(f'{OUT}: {SCREENS} screens, {AREAS} areas, {CITIES} cities, {len(LOGOS)} logos')
