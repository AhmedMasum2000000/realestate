"""LED AD PRO loading intro: inline SVG logo that assembles while the page loads.

First visit in a browser session: full intro (globe pops in spinning with orbiting dots, letters snap
together, billboard rises), at least ~1.1 s, at most 3 s. Later pages: hidden unless loading takes more
than 350 ms, then only the spinning globe shows. On internal link clicks assets/ux.js shows the globe
in front while the next page loads. No JS / reduced motion: never shown.
"""
import re
from pathlib import Path

SVG = Path(__file__).resolve().parent.parent / 'sites/ledadpro-v2/brand/logo-classic-dark-animated.svg'

CSS = '''<style>
.intro{position:fixed;inset:0;z-index:9999;overflow:hidden;display:grid;place-items:center;background:radial-gradient(120% 90% at 50% 40%,#0d2550 0%,#07122b 70%);transition:opacity .35s ease,visibility 0s linear .35s}
.intro .iw{width:min(560px,78vw);position:relative}
.intro svg{width:100%;height:auto;display:block;overflow:visible}
.intro .il,.intro #board{opacity:0;transform-box:fill-box;transform-origin:50% 60%}
.intro .il{animation:ipop .55s cubic-bezier(.2,1.5,.4,1) calc(.22s + var(--i)*.065s) both}
.intro #board{animation:irise .45s cubic-bezier(.2,1.3,.4,1) .78s both}
.intro #globe{transform-box:fill-box;transform-origin:center;animation:igpop .5s cubic-bezier(.2,1.6,.4,1) both}
.intro .ring{fill:none;stroke:#8AD5F2;stroke-width:4;transform-box:fill-box;transform-origin:center;animation:iring 1.1s ease-out .15s infinite}
.intro .orb{transform-origin:1122px 407px;animation:iorb 1.6s linear infinite}
.intro .bar{height:3px;margin:28px auto 0;width:46%;background:rgba(255,255,255,.12);border-radius:3px;overflow:hidden}
.intro .bar i{display:block;height:100%;width:100%;background:linear-gradient(90deg,#0674BB,#3FC1F0,#5BBF6A);transform-origin:left;animation:ibar 1.15s cubic-bezier(.6,.1,.3,1) both}
@keyframes ipop{from{opacity:0;scale:.35;translate:0 40px}to{opacity:1;scale:1;translate:0 0}}
@keyframes irise{from{opacity:0;translate:0 60px;scale:.8}to{opacity:1;translate:0 0;scale:1}}
@keyframes igpop{0%{scale:.1;opacity:0}60%{scale:1.35;opacity:1}100%{scale:1}}
@keyframes iring{from{scale:1;opacity:.8}to{scale:2.4;opacity:0}}
@keyframes iorb{to{rotate:360deg}}
@keyframes ibar{from{transform:scaleX(0)}to{transform:scaleX(1)}}
/* quick mode (later pages, link clicks): globe only */
.intro.q{opacity:0;visibility:hidden}
.intro.q.show{opacity:1;visibility:visible;transition:opacity .18s ease}
.intro.q .il,.intro.q #board{animation:none;opacity:1}
.intro.q .bar{display:none}
.intro.q .iw{width:min(420px,70vw)}
.intro.out{opacity:0;visibility:hidden}
@media (prefers-reduced-motion:reduce){.intro{display:none}}
</style><noscript><style>.intro{display:none}</style></noscript>'''

JS = '''<script>(function(){var i=document.getElementById('intro'),s=0,t0=Date.now(),d=0;
try{s=sessionStorage.getItem('lap-intro');sessionStorage.setItem('lap-intro','1')}catch(e){}
if(s){i.classList.add('q');var sh=setTimeout(function(){i.classList.add('show')},350)}
function done(){if(d)return;d=1;clearTimeout(sh);i.classList.add('out');setTimeout(function(){i.classList.remove('show','leave');i.classList.add('q')},400)}
window.lapIntroDone=done;var min=s?0:1150;
window.addEventListener('load',function(){setTimeout(done,Math.max(0,min-(Date.now()-t0)))});
setTimeout(done,3000);
window.addEventListener('pageshow',function(e){if(e.persisted){i.classList.remove('show');i.classList.add('q','out')}})})();</script>'''


def intro_html():
    svg = SVG.read_text()
    svg = re.sub(r'<title>.*?</title>', '', svg)
    for k, gid in enumerate(['L', 'E', 'D1', 'A', 'D2', 'P', 'R', 'O']):
        svg = svg.replace(f'<g id="{gid}" ', f'<g class="il" style="--i:{k}" id="{gid}" ', 1)
    ring = ('<circle class="ring" cx="1122" cy="407" r="70"/>'
            '<g class="orb"><circle cx="1122" cy="307" r="7" fill="#8AD5F2"/><circle cx="1222" cy="407" r="5" fill="#5BBF6A"/>'
            '<circle cx="1022" cy="407" r="5" fill="#3FC1F0"/><circle cx="1122" cy="507" r="6" fill="#FFD60A"/></g>')
    svg = svg.replace('<g id="globe"', ring + '<g id="globe"', 1)
    svg = svg.replace('role="img" aria-label="LED AD PRO"', 'aria-hidden="true" focusable="false"', 1)
    return f'{CSS}<div class="intro" id="intro" aria-hidden="true"><div class="iw">{svg}<div class="bar"><i></i></div></div></div>{JS}'
