#!/usr/bin/python3
"""LED AD PRO 11-year anniversary social posts (01 Dec 2015 -> 01 Dec 2026).
Writes one HTML per size into brand/ledadpro/social/; render with tools/render_social.js."""
import base64, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from ledadpro_extra import CLIENTS  # noqa: E402
A = ROOT / 'brand/ledadpro/classic/assets'
OUT = ROOT / 'brand/ledadpro/social'; OUT.mkdir(parents=True, exist_ok=True)
V2 = ROOT / 'sites/ledadpro-v2'


def uri(p):
    p = Path(p); mime = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg'}[p.suffix]
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()


def logo_uri(c):
    s = re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')
    for ext in ('svg', 'png'):
        f = V2 / 'img/clients' / f'{s}.{ext}'
        if f.exists():
            return uri(f)


# 5x7 LED font for the digit 1
ONE = ['..#..', '.##..', '#.#..', '..#..', '..#..', '..#..', '#####']


def led_eleven(cell):
    """Two '1' glyphs as glowing LED dots (lit) on a faint dot grid (unlit)."""
    cols, rows, gap = 5, 7, 2
    W = (cols * 2 + gap) * cell; H = rows * cell; r = cell * .40
    dots = []
    for g in range(2):
        ox = g * (cols + gap)
        for y, row in enumerate(ONE):
            for x, ch in enumerate(row):
                cx, cy = (ox + x + .5) * cell, (y + .5) * cell
                lit = ch == '#'
                delay = (g * 7 + y + x) * .03
                dots.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" class="{"on" if lit else "off"}" style="--d:{delay:.2f}s"/>')
    for x in range(gap):  # unlit dots in the gap between the digits
        for y in range(rows):
            cx, cy = (cols + x + .5) * cell, (y + .5) * cell
            dots.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" class="off"/>')
    return f'''<svg class="eleven" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>
<radialGradient id="ledg" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#E9F8FF"/><stop offset=".45" stop-color="#5FD0FF"/><stop offset="1" stop-color="#0674BB"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{cell * .22:.1f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<g filter="url(#glow)">{"".join(d for d in dots if 'class="on"' in d)}</g>{"".join(d for d in dots if 'class="off"' in d)}</svg>'''


CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
body{width:var(--w);height:var(--h);overflow:hidden;font-family:Inter,sans-serif;color:#fff;
 background:radial-gradient(70% 45% at 50% 38%,rgba(6,116,187,.55),transparent 70%),radial-gradient(60% 40% at 85% 95%,rgba(91,191,106,.18),transparent 70%),linear-gradient(180deg,#071634 0%,#050d22 100%)}
.grid{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(138,213,242,.10) 1.6px,transparent 2px);background-size:22px 22px;
 -webkit-mask-image:radial-gradient(75% 55% at 50% 40%,#000 30%,transparent 80%)}
.frame{position:absolute;inset:var(--pad);display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center}
.top img{height:var(--logo)}
.est{border:2px solid rgba(138,213,242,.45);border-radius:999px;padding:12px 22px;font:800 20px/1 Inter;letter-spacing:.2em;text-transform:uppercase;color:#bfe9fb}
.est b{color:#fff}
.hero{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.kick{font:800 var(--kick)/1 Inter;letter-spacing:.42em;text-transform:uppercase;color:#8AD5F2;margin-bottom:var(--g1)}
.eleven{width:var(--eleven);height:auto;overflow:visible}
.eleven .on{fill:url(#ledg)}.eleven .off{fill:rgba(138,213,242,.09)}
.years{font:900 var(--years)/.95 "Inter Display",Inter;letter-spacing:-.01em;margin-top:var(--g1);text-transform:uppercase}.years span{display:block;white-space:nowrap}
.years em{font-style:normal;background:linear-gradient(90deg,#3FC1F0,#8AD5F2 45%,#5BBF6A);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{font:600 var(--sub)/1.35 Inter;color:#cfe1f3;margin-top:var(--g2);max-width:var(--subw)}
.dates{display:flex;align-items:center;gap:18px;margin-top:var(--g2);font:800 22px/1 Inter;letter-spacing:.14em;color:#fff}
.dates i{display:block;width:120px;height:3px;background:linear-gradient(90deg,#0674BB,#3FC1F0,#5BBF6A);border-radius:3px;position:relative}
.dates i::after{content:"";position:absolute;right:-4px;top:-5px;width:13px;height:13px;border-radius:50%;background:#5BBF6A;box-shadow:0 0 14px #5BBF6A}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:var(--g3)}
.stats div{background:rgba(255,255,255,.06);border:1px solid rgba(138,213,242,.22);border-radius:18px;padding:20px 12px;text-align:center}
.stats b{display:block;font:900 var(--stat)/1 "Inter Display",Inter;color:#fff}
.stats span{display:block;margin-top:8px;font:800 14px/1.2 Inter;letter-spacing:.12em;text-transform:uppercase;color:#8AD5F2}
.logos{margin-top:18px;background:#fff;border-radius:20px;padding:16px 22px;display:grid;grid-template-columns:repeat(var(--lc),1fr);gap:14px 18px;align-items:center}
.logos img{width:100%;height:var(--lh);object-fit:contain}
.trust{margin-top:12px;text-align:center;font:700 15px/1.3 Inter;letter-spacing:.14em;text-transform:uppercase;color:#9fb4cf}
.bottom{margin-top:var(--g3);display:flex;justify-content:space-between;align-items:center;gap:20px;padding-top:22px;border-top:1px solid rgba(138,213,242,.22)}
.call{display:flex;align-items:center;gap:16px}
.call .ic{width:62px;height:62px;border-radius:50%;background:#0674BB;display:grid;place-items:center;box-shadow:0 0 0 6px rgba(6,116,187,.25)}
.call small{display:block;font:800 14px/1 Inter;letter-spacing:.2em;text-transform:uppercase;color:#8AD5F2;margin-bottom:6px}
.call b{font:900 var(--phone)/1 "Inter Display",Inter}
.web{text-align:right;font:800 var(--web)/1.3 Inter}.web span{display:block;font:700 14px/1.3 Inter;letter-spacing:.14em;text-transform:uppercase;color:#9fb4cf}
.strip{position:absolute;left:0;right:0;bottom:0;height:10px;background:linear-gradient(90deg,#0674BB,#3FC1F0,#5BBF6A)}
'''

SIZES = {  # name: (w, h, vars, logos shown, logo columns)
    'post-4x5': (1080, 1350, dict(pad='58px', logo='88px', kick='20px', eleven='470px', years='66px', sub='23px', subw='760px', stat='42px', phone='34px', web='22px', lh='34px', g1='10px', g2='16px', g3='22px'), 12, 6),
    'square': (1080, 1080, dict(pad='50px', logo='76px', kick='17px', eleven='330px', years='54px', sub='19px', subw='760px', stat='34px', phone='30px', web='20px', lh='30px', g1='8px', g2='12px', g3='16px'), 6, 6),
    'story-9x16': (1080, 1920, dict(pad='80px', logo='112px', kick='26px', eleven='700px', years='76px', sub='30px', subw='820px', stat='50px', phone='42px', web='26px', lh='44px', g1='22px', g2='30px', g3='44px'), 12, 4),
}


def build(name):
    w, h, v, nlogos, cols = SIZES[name]
    logos = [c for c in CLIENTS if logo_uri(c)][:nlogos]
    css_vars = ';'.join(f'--{k}:{val}' for k, val in v.items()) + f';--w:{w}px;--h:{h}px;--lc:{cols}'
    stats = '' if name == 'square' else '''<div class="stats"><div><b>400+</b><span>brands served</span></div><div><b>56</b><span>LED screens</span></div><div><b>21</b><span>areas</span></div><div><b>10</b><span>cities</span></div></div>'''
    sq_stats = '<div class="stats" style="margin-top:18px"><div><b>400+</b><span>brands</span></div><div><b>56</b><span>LED screens</span></div><div><b>21</b><span>areas</span></div><div><b>10</b><span>cities</span></div></div>' if name == 'square' else ''
    phone_ic = '<svg viewBox="0 0 24 24" width="30" height="30"><path fill="#fff" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>'
    cell = 64
    SUBSTYLE = 'style="display:none"' if name == 'square' else ''
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="{css_vars}">
<div class="grid"></div>
<div class="frame">
 <div class="top"><img src="{uri(A / 'logo-classic-dark.svg')}" alt="LED AD PRO"><div class="est">Est. <b>01·12·2015</b></div></div>
 <div class="hero">
  <p class="kick">Celebrating</p>
  {led_eleven(cell)}
  <h1 class="years"><span>Years of <em>lighting up</em></span><span>Bangladesh</span></h1>
  <p class="sub" {SUBSTYLE}>LED billboards, Metro Rail LED, LED caravans and outdoor campaigns for the brands Bangladesh trusts.</p>
  <div class="dates"><span>01 DEC 2015</span><i></i><span>01 DEC 2026</span></div>
  {stats}
 </div>
 {sq_stats}
 <div class="logos">{"".join(f'<img src="{logo_uri(c)}" alt="{c}">' for c in logos)}</div>
 <p class="trust">Thank you to every brand that chose our team</p>
 <div class="bottom"><div class="call"><span class="ic">{phone_ic}</span><div><small>Book your next campaign</small><b>+880 1958-503753</b></div></div>
  <div class="web">ledadpro.com<span>Official LED partner to AD Pro</span></div></div>
</div><div class="strip"></div></body></html>'''
    f = OUT / f'anniv11-{name}.html'; f.write_text(html); return f, w, h


if __name__ == '__main__':
    for n in SIZES:
        f, w, h = build(n); print(f'{f} {w} {h}')
