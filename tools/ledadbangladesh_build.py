#!/usr/bin/python3
"""ledadbangladesh.com: one-page studio-style site (light typographic hero with a letter pattern,
dark work list, screen network table, client logos, contact footer).
Source of truth for facts: the LED AD PRO data (locations.js, ledadpro_extra.py). Own photos only.
Writes sites/ledadbangladesh/; deploy with vps-run site-deploy.sh "ledadbangladesh.com ledadbangladesh"."""
import json, re, shutil, sys
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from ledadpro_extra import CLIENTS, CASES  # noqa: E402

V2 = ROOT / 'sites/ledadpro-v2'
OUT = ROOT / 'sites/ledadbangladesh'
SITE = 'https://ledadbangladesh.com'
PHONE, PHONE_TXT = '+8801958503753', '+880 1958-503753'   # Sales and Marketing
OFFICE, OFFICE_TXT = '+8801316743003', '+880 1316-743003'  # office
EMAIL = 'info@ledadpro.com'
ADDRESS = 'Flat A1, House 99 (1st floor), Road 10/2, Block D, Niketon, Gulshan 1, Dhaka'

# ---- data
src = (V2 / 'locations.js').read_text()
LOCS, _ = json.JSONDecoder().raw_decode(src, src.index('window.LOCS=') + len('window.LOCS='))
SCREENS = sum(len(a['p']) for a in LOCS)
AREAS = len(LOCS)
CITIES = 1 + sum(1 for a in LOCS if a['kind'] == 'city')  # Dhaka + the district cities

# Screens shown in the list: our own network photos (area, caption, file)
NETWORK = [
    ('Gulshan Circle-2', 'LED billboards on the main junction of Gulshan', 'gulshan-circle-2-1200.webp'),
    ('Mirpur-10 Circle', 'Four screens round one roundabout', 'mirpur-10-circle-4-screens-1200.webp'),
    ('Shimanto Square', 'Six LED screens at Dhanmondi’s shopping corner', 'shimanto-square-6-led-screens-1200.webp'),
    ('Science Lab Circle', 'Dhanmondi, New Market and Elephant Road traffic', 'science-lab-circle-1200.webp'),
    ('Sonargaon Mor', 'Karwan Bazar, the business crossing of Dhaka', 'sonargaon-mor-karwan-bazar-1200.webp'),
    ('SKS Tower, Mohakhali', 'Flyover-facing screen on the airport road', 'sks-tower-exit-gate-mohakhali-1200.webp'),
    ('Airport Entrance', 'Banani-facing screen on the way to the airport', 'airport-entrance-banani-facing-1200.webp'),
    ('Dhanmondi 27', 'Opposite Rapa Plaza', 'dhanmondi-27-opposite-of-rapa-plaza-1200.webp'),
    ('Sylhet, Bondor Bazar', 'One of eight screens across Sylhet', 'sylhet-bondor-bazar-1200.webp'),
    ('Agrabad, Chattogram', 'The port city’s business district', 'agrabad-circle-chittagong-1200.webp'),
    ('Sughondha Point, Cox’s Bazar', 'Beach-road traffic all season', 'sughondha-point-coxs-bazar-1200.webp'),
    ('Shaheb Bazar, Rajshahi', 'Two screens, both sides of the road', 'rajshahi-shaheb-bazar-2-screens-both-sides-1200.webp'),
]


def slug(c):
    return re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')


def logo_file(c):
    for ext in ('svg', 'png'):
        f = V2 / 'img/clients' / f'{slug(c)}.{ext}'
        if f.exists():
            return f


# ---- copy assets
if OUT.exists():
    shutil.rmtree(OUT)
for d in ('img/work', 'img/loc', 'img/clients', 'brand'):
    (OUT / d).mkdir(parents=True)
for f, *_ in CASES:
    shutil.copy(V2 / 'img/work' / f, OUT / 'img/work' / f)
for _, _, f in NETWORK:
    shutil.copy(V2 / 'img/loc' / f, OUT / 'img/loc' / f)
LOGOS = [(c, logo_file(c)) for c in CLIENTS if logo_file(c)]
for c, f in LOGOS:
    shutil.copy(f, OUT / 'img/clients' / f.name)
for f in ('favicon.svg', 'favicon-32.png', 'favicon-180.png', 'favicon.ico'):
    shutil.copy(V2 / 'brand' / f, OUT / 'brand' / f)
shutil.copy(OUT / 'brand/favicon.ico', OUT / 'favicon.ico')

# ---- html pieces
items = []
n = 0
for f, brand, what, where in CASES:
    n += 1
    items.append(f'''<li class="it"><div class="it-h"><span class="n">{n:02d}</span><span class="t">{e(brand)}</span><span class="y">( {e(where)} )</span></div>
<figure><img loading="lazy" decoding="async" src="img/work/{f}" alt="{e(brand)} LED billboard campaign, {e(where)}" width="1600" height="1000"><figcaption>{e(what)}</figcaption></figure></li>''')
work_html = ''.join(items)
items = []
for name, cap, f in NETWORK:
    n += 1
    items.append(f'''<li class="it"><div class="it-h"><span class="n">{n:02d}</span><span class="t">{e(name)}</span><span class="y">( LED screen )</span></div>
<figure><img loading="lazy" decoding="async" src="img/loc/{f}" alt="LED billboard at {e(name)}" width="1200" height="800"><figcaption>{e(cap)}</figcaption></figure></li>''')
net_html = ''.join(items)

rows = sorted(LOCS, key=lambda a: (-len(a['p']), a['name']))
table_html = ''.join(f'<tr><td>{e(a["name"])}</td><td>{len(a["p"])}</td></tr>' for a in rows)
logos_html = ''.join(f'<li><img loading="lazy" decoding="async" src="img/clients/{f.name}" alt="{e(c)}"></li>' for c, f in LOGOS)
more_names = [c for c in CLIENTS if not logo_file(c)]

schema = json.dumps({
    "@context": "https://schema.org", "@type": "AdvertisingAgency", "name": "LED AD Bangladesh", "url": SITE + '/',
    "telephone": PHONE, "email": EMAIL,
    "address": {"@type": "PostalAddress", "streetAddress": "Flat A1, House 99, Road 10/2, Block D, Niketon", "addressLocality": "Gulshan 1, Dhaka", "addressCountry": "BD"},
    "areaServed": "Bangladesh", "parentOrganization": {"@type": "Organization", "name": "LED AD PRO", "url": "https://ledadpro.com/"},
    "contactPoint": [{"@type": "ContactPoint", "telephone": PHONE, "contactType": "sales", "areaServed": "BD"}]}, ensure_ascii=False)

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LED AD Bangladesh: LED Billboard Advertising across Bangladesh</title>
<meta name="description" content="LED AD Bangladesh runs {SCREENS} LED billboard screens in {AREAS} areas and {CITIES} cities, from Gulshan and Dhanmondi to Sylhet, Chattogram and Cox’s Bazar. Campaigns for 400+ brands since 2015. Call +880 1958-503753.">
<link rel="canonical" href="{SITE}/">
<meta property="og:title" content="LED AD Bangladesh">
<meta property="og:description" content="{SCREENS} LED screens. {AREAS} areas. {CITIES} cities. One call.">
<meta property="og:image" content="{SITE}/img/work/royal-enfield-gulshan-2.jpg">
<meta property="og:url" content="{SITE}/">
<meta name="theme-color" content="#0a0a0a">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="brand/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="brand/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v=1">
<script type="application/ld+json">{schema}</script>
</head>
<body>
<header class="hero" id="home">
  <canvas id="pattern" aria-hidden="true"></canvas>
  <div class="bar">
    <p class="about">LED billboard advertising company based in Dhaka, Bangladesh.</p>
    <p class="where"><span>Everywhere in Bangladesh</span><span class="mut">({CITIES} cities)</span></p>
    <p class="clock"><i class="dot" aria-hidden="true"></i><time id="clock" datetime="">--:--:--</time></p>
    <a class="contact" href="#contact">Contact</a>
  </div>
  <a class="scroll" href="#work">scroll down</a>
  <h1 class="mark" aria-label="LED AD Bangladesh"><span class="fit" data-fit>LED AD Bangladesh</span></h1>
</header>

<main class="page">
  <nav class="top" aria-label="Sections">
    <p class="links"><a href="#home">Home</a>, <a href="#work">Work</a>, <a href="#screens">Screens</a>, <a href="#clients">Clients</a></p>
    <a href="#contact">Contact</a>
  </nav>
  <p class="title" aria-hidden="true">LED AD Bangladesh</p>

  <section id="work" class="sec">
    <div class="sec-h"><h2>Work</h2><p class="tog"><button type="button" data-toggle="work-list" aria-expanded="true" aria-controls="work-list">Show</button> &ndash; <button type="button" data-toggle="work-list" data-hide aria-controls="work-list">Hide</button></p></div>
    <ul class="list" id="work-list">{work_html}</ul>
  </section>

  <section id="screens" class="sec">
    <div class="sec-h"><h2>Screens</h2><p class="tog"><button type="button" data-toggle="net-list" aria-expanded="true" aria-controls="net-list">Show</button> &ndash; <button type="button" data-toggle="net-list" data-hide aria-controls="net-list">Hide</button></p></div>
    <ul class="list" id="net-list">{net_html}</ul>
  </section>

  <section class="sec text">
    <h2 class="lbl">The network</h2>
    <p class="lead">Not just screens. Every board is on a junction people already pass every day: Gulshan, Mirpur, Dhanmondi, the airport road, and the main crossings of nine more cities. One brief, one schedule, the whole country.</p>
    <table class="tbl"><tbody>{table_html}</tbody></table>
    <p class="sum">That is <b>{SCREENS}</b> LED screens in <b>{AREAS}</b> areas and <b>{CITIES}</b> cities.</p>
  </section>

  <section id="clients" class="sec text">
    <h2 class="lbl">Selected clients</h2>
    <p class="lead">Our team has planned and run outdoor and LED campaigns for 400+ brands since 2015, from BMW, Emirates and Coca-Cola to Aarong, Walton and Square. LED AD Bangladesh works with the LED AD PRO team, the official LED partner to AD Pro.</p>
    <ul class="logos">{logos_html}<li class="more">And <span>more</span></li></ul>
    <p class="fine">Also: {e(', '.join(more_names[:9]))} and others.</p>
  </section>

  <footer id="contact" class="foot">
    <p class="where"><span>Dhaka, Bangladesh</span><span class="mut">(Gulshan 1)</span><span class="clock"><i class="dot" aria-hidden="true"></i><time data-clock>--:--:--</time></span></p>
    <div class="cols">
      <p><span class="lbl">&copy; LED AD Bangladesh</span>Team since 2015<br>Official LED partner to AD Pro</p>
      <p><span class="lbl">Let&rsquo;s talk</span><a href="tel:{PHONE}">{PHONE_TXT}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p><span class="lbl">Office</span>{e(ADDRESS)}<br><a href="tel:{OFFICE}">{OFFICE_TXT}</a></p>
      <p><span class="lbl">Elsewhere</span><a href="https://ledadpro.com/" rel="noopener">ledadpro.com</a><br><a href="https://wa.me/{PHONE[1:]}?text={e('Hi LED AD Bangladesh, I want to advertise.').replace(' ', '%20')}" rel="noopener" target="_blank">WhatsApp</a></p>
    </div>
  </footer>
</main>
<script src="main.js?v=1" defer></script>
</body>
</html>
'''

css = '''*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#111;--paper:#e5e5e5;--bg:#0a0a0a;--fg:#f2f2f2;--mute:#8a8a8a;--line:#2a2a2a;--acc:#3FC1F0;--pad:clamp(14px,2vw,28px)}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{background:var(--bg);color:var(--fg);font:400 14px/1.35 Inter,"Helvetica Neue",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:3px}
img{display:block;max-width:100%;height:auto}
button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;padding:0}

/* ---- hero (sticky; the dark page scrolls over it) */
.hero{position:sticky;top:0;height:100svh;min-height:520px;overflow:hidden;background:var(--paper);color:var(--ink);z-index:0}
#pattern{position:absolute;inset:0;width:100%;height:100%}
.hero .bar{position:absolute;top:0;left:0;right:0;display:grid;grid-template-columns:1fr 1fr auto 1fr;gap:16px;padding:var(--pad);align-items:start;z-index:2}
.hero .about{max-width:200px}
.hero .where{display:flex;gap:1.6em;flex-wrap:wrap}
.mut{color:var(--mute)}
.hero .clock{justify-self:center}
.clock{display:inline-flex;align-items:center;gap:8px;font-variant-numeric:tabular-nums}
.dot{width:9px;height:9px;border-radius:50%;background:currentColor;display:inline-block}
.hero .contact{justify-self:end}
.hero .scroll{position:absolute;left:50%;top:48%;transform:translateX(-50%);z-index:2}
.hero .mark{position:absolute;left:0;right:0;bottom:-.06em;z-index:2;font-weight:500;letter-spacing:-.045em;line-height:.86;white-space:nowrap;pointer-events:none}
.hero .mark .fit{display:inline-block;white-space:nowrap;padding:0 .02em}
@media (max-width:760px){
  .hero .bar{grid-template-columns:1fr auto}
  .hero .where{display:none}
  .hero .clock{justify-self:end}
  .hero .contact{display:none}
  .hero .mark{bottom:0}
  .hero .mark .fit{display:block;white-space:normal;padding:0 12px 6px}
}

/* ---- dark page */
.page{position:relative;z-index:1;background:var(--bg);padding:0 var(--pad) var(--pad);min-height:100vh}
.top{position:sticky;top:0;z-index:5;background:var(--bg);display:flex;justify-content:space-between;padding:var(--pad) 0 10px}
.title{font-size:clamp(40px,7.4vw,112px);font-weight:500;letter-spacing:-.04em;line-height:1;padding:4px 0 18px}
.sec{border-top:1px solid var(--line)}
.sec-h{display:flex;justify-content:space-between;align-items:baseline;padding:10px 0}
.sec-h h2{font-size:14px;font-weight:400}
.tog{color:var(--mute)}
.tog button[aria-expanded="true"],.tog button.on{color:var(--fg)}
.list{list-style:none}
.list[hidden]{display:none}
.it{border-top:1px solid var(--line)}
.it-h{display:grid;grid-template-columns:2.4em 1fr auto;padding:9px 0;text-transform:uppercase;font-variant-numeric:tabular-nums}
.it-h .n{font-size:11px;padding-top:2px}
.it-h .y{color:var(--mute);text-transform:none}
.it figure{margin:0 0 10px}
.it img{width:100%;aspect-ratio:16/10;object-fit:cover;background:#161616;opacity:0;transform:translateY(12px);transition:opacity .6s ease,transform .6s ease}
.it img.in{opacity:1;transform:none}
.it figcaption{padding:8px 0 4px;color:var(--mute)}
@media (min-width:900px){
  .it{display:grid;grid-template-columns:1fr 1fr;gap:0 var(--pad);align-items:start}
  .it-h{position:sticky;top:64px}
  .it figure{margin:9px 0 14px}
}

.text{padding:18px 0 40px}
.lbl{display:block;text-transform:uppercase;font-size:12px;letter-spacing:.02em;margin-bottom:14px}
.lead{max-width:38em;margin-bottom:28px}
.tbl{width:100%;max-width:560px;border-collapse:collapse;text-transform:uppercase}
.tbl td{border-bottom:1px solid var(--line);padding:7px 0}
.tbl td:last-child{text-align:right;color:var(--acc);font-variant-numeric:tabular-nums}
.sum{margin-top:18px;color:var(--mute)}.sum b{color:var(--acc);font-weight:500}
.logos{list-style:none;display:grid;grid-template-columns:repeat(2,1fr);border-top:1px solid var(--bg);border-left:1px solid var(--bg)}
.logos li{background:var(--paper);color:var(--ink);border:1px solid var(--bg);border-width:0 1px 1px 0;aspect-ratio:2.2;min-width:0;overflow:hidden;display:grid;place-items:center;padding:17% 24%}
.logos img{width:100%;height:100%;object-fit:contain;filter:grayscale(1)}
.logos .more{font-size:16px}.logos .more span{color:#0674BB}
.fine{color:var(--mute);margin-top:14px;max-width:48em}
@media (min-width:760px){.logos{grid-template-columns:repeat(4,1fr)}}

.foot{border-top:1px solid var(--line);padding:16px 0 0}
.foot .where{display:flex;gap:1.6em;flex-wrap:wrap;align-items:center;padding-bottom:28px}
.foot .where .clock{margin-left:auto}
.foot .cols{display:grid;grid-template-columns:repeat(2,1fr);gap:28px var(--pad);border-top:1px solid var(--line);padding:16px 0 8px}
.foot .cols .lbl{margin-bottom:6px}
@media (min-width:900px){.foot .cols{grid-template-columns:repeat(4,1fr)}}
'''

js = r'''(function () {
  var d = document, reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- Dhaka clock (UTC+6)
  var clocks = [].slice.call(d.querySelectorAll('#clock, [data-clock]'));
  function tick() {
    var n = new Date(), t = new Date(n.getTime() + (n.getTimezoneOffset() + 360) * 60000);
    var s = [t.getHours(), t.getMinutes(), t.getSeconds()].map(function (x) { return (x < 10 ? '0' : '') + x; }).join(':');
    clocks.forEach(function (c) { c.textContent = s; c.setAttribute('datetime', s); });
  }
  tick(); setInterval(tick, 1000);

  // ---- fit the wordmark to the width
  var fit = d.querySelector('[data-fit]'), mark = fit && fit.parentNode;
  function fitMark() {
    if (!fit) return;
    var box = mark.clientWidth; if (!box) return;
    if (innerWidth <= 760) { // two lines on phones: fit the longer word
      fit.innerHTML = 'LED AD<br>Bangladesh';
      fit.style.fontSize = '100px';
      var probe = d.createElement('span'); probe.textContent = 'Bangladesh'; probe.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font-size:100px';
      mark.appendChild(probe); var w = probe.offsetWidth; mark.removeChild(probe);
      fit.style.fontSize = Math.floor(100 * (box - 24) / w) + 'px';
    } else {
      fit.textContent = 'LED AD Bangladesh';
      fit.style.fontSize = '100px';
      fit.style.fontSize = Math.floor(100 * box / fit.offsetWidth * 0.995) + 'px';
    }
  }
  fitMark(); addEventListener('resize', fitMark);
  if (d.fonts) { d.fonts.ready.then(fitMark); d.fonts.addEventListener('loadingdone', fitMark); if (d.fonts.load) d.fonts.load('500 100px Inter').then(fitMark, fitMark); }
  setTimeout(fitMark, 2500);

  // ---- letter pattern: nested diamonds of our letters spreading out from two points, like a
  // signal going out; each letter has its own brightness; the pointer lights letters up
  var c = d.getElementById('pattern'), hero = c && c.parentNode;
  if (c && c.getContext) {
    var X = c.getContext('2d'), WORD = 'LED AD ', dpr = Math.min(2, devicePixelRatio || 1);
    var cw, ch, cols, rows, W, H, mx = -1e4, my = -1e4, visible = true, last = 0, t0 = performance.now();
    function size() {
      W = hero.clientWidth; H = hero.clientHeight; c.width = W * dpr; c.height = H * dpr;
      var base = W < 760 ? 12 : 13; cw = base * dpr; ch = (base - 2) * dpr; cols = Math.ceil(c.width / cw); rows = Math.ceil(c.height / ch);
      X.font = '500 ' + (base - 3.5) * dpr + 'px Inter, Helvetica, Arial, sans-serif'; X.textBaseline = 'middle'; X.textAlign = 'center';
      draw(performance.now());
    }
    function tri(v, p, w) { v = ((v % p) + p) % p; var dd = Math.min(v, p - v); return dd < w ? 1 - dd / w : 0; }
    function hash(x, y) { var s = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453; return s - Math.floor(s); }
    function draw(now) {
      var t = reduce ? 0 : (now - t0) / 1000;
      X.clearRect(0, 0, c.width, c.height);
      var P = 15, Wd = 3.4, r = 9, k = cw / ch, cy = rows * 0.5;
      var cx1 = cols * (W < 760 ? 0.5 : 0.27), cx2 = cols * 0.73;
      for (var y = 0; y < rows; y++) {
        var dy = Math.abs(y - cy) * k;
        for (var x = 0; x < cols; x++) {
          var rad = Math.abs(x - cx1) + dy; if (W >= 760) rad = Math.min(rad, Math.abs(x - cx2) + dy);
          var a = tri(rad - t * 1.6, P, Wd);
          var px = x - mx, py = y - my, dist = Math.sqrt(px * px + py * py);
          if (dist < r) a += (1 - dist / r) * 0.9;
          if (a < 0.08) continue;
          var ch1 = WORD[(x + (y >> 1)) % 7]; if (ch1 === ' ') continue;
          X.fillStyle = 'rgba(17,17,17,' + Math.min(0.85, a * (0.45 + 0.55 * hash(x, y))).toFixed(3) + ')';
          X.fillText(ch1, (x + 0.5) * cw, (y + 0.5) * ch);
        }
      }
    }
    function loop(now) {
      if (visible && now - last > 40) { last = now; draw(now); }
      if (!reduce) requestAnimationFrame(loop);
    }
    size(); addEventListener('resize', size);
    if (!reduce) requestAnimationFrame(loop);
    hero.addEventListener('pointermove', function (ev) { var b = c.getBoundingClientRect(); mx = (ev.clientX - b.left) * dpr / cw; my = (ev.clientY - b.top) * dpr / ch; }, { passive: true });
    hero.addEventListener('pointerleave', function () { mx = my = -1e4; });
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(hero);
  }

  // ---- show / hide lists
  d.addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-toggle]'); if (!b) return;
    var list = d.getElementById(b.dataset.toggle), hide = b.hasAttribute('data-hide');
    list.hidden = hide;
    var box = b.parentNode; [].forEach.call(box.querySelectorAll('button'), function (x) { x.classList.toggle('on', x.hasAttribute('data-hide') === hide); x.setAttribute('aria-expanded', !hide); });
  });

  // ---- reveal images as they arrive
  var imgs = [].slice.call(d.querySelectorAll('.it img'));
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    imgs.forEach(function (i) { io.observe(i); });
  } else imgs.forEach(function (i) { i.classList.add('in'); });
})();
'''

htaccess = '''DirectoryIndex index.html
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/\\.well-known/
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} !^ledadbangladesh\\.com$ [NC]
RewriteRule ^ https://ledadbangladesh.com%{REQUEST_URI} [L,R=301]
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
print(f'{OUT}: {SCREENS} screens, {AREAS} areas, {CITIES} cities, {len(LOGOS)} logos, {len(CASES) + len(NETWORK)} list items')
