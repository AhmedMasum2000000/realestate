// Export the approved classic LED AD PRO logo (brand/ledadpro/classic/logo-classic.html) as a clean asset set.
// node tools/classic_logo_export.js  -> brand/ledadpro/classic/assets/*
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const SRC = path.resolve(__dirname, '../brand/ledadpro/classic/logo-classic.html');
const OUT = path.resolve(__dirname, '../brand/ledadpro/classic/assets'); fs.mkdirSync(OUT, { recursive: true });

const SPIN = `<style>#lands{animation:spin 7s linear infinite}@keyframes spin{from{transform:translateX(0)}to{transform:translateX(220px)}}
#scrsh{animation:sh 3.2s ease-in-out infinite}@keyframes sh{0%,55%{transform:translateX(-160px) skewX(-20deg)}100%{transform:translateX(420px) skewX(-20deg)}}
@media (prefers-reduced-motion:reduce){#lands,#scrsh{animation:none}}</style>`;

(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + SRC); await p.waitForTimeout(200); await p.evaluate(() => render(2, true));
  const base = await p.evaluate(() => {
    const s = document.getElementById('s').cloneNode(true);
    ['glowfx', 'fx', 'sheen', 'orbit', 'gring'].forEach(id => { const e = s.querySelector('#' + id); if (e) e.remove(); });
    s.querySelector('#scrcontent').innerHTML = '';
    s.querySelector('#letters').removeAttribute('filter');
    s.querySelectorAll('#letters g').forEach(g => g.removeAttribute('opacity'));
    s.querySelector('#globe').setAttribute('transform', 'translate(1122 407)');
    s.querySelector('#lands').setAttribute('transform', 'translate(0 0)');
    const fr = s.querySelector('#frame'); fr.removeAttribute('stroke-dasharray'); fr.removeAttribute('stroke-dashoffset');
    s.removeAttribute('id'); s.removeAttribute('width'); s.removeAttribute('height');
    s.setAttribute('viewBox', '28 36 1212 476');
    return s.outerHTML;
  });
  const OUTLINE = '<style>#letters path,#letters rect{stroke:#0A5C99;stroke-width:1.4;stroke-linejoin:round;paint-order:stroke}#letters .face{stroke:#4FA9D8}</style>';
  const shine = '<rect id="scrsh" x="840" y="40" width="70" height="200" fill="url(#sweep)" opacity=".8"/>';
  const light = base.replace('<g id="scrcontent" clip-path="url(#scrclip)"></g>', `<g clip-path="url(#scrclip)">${shine}</g>`)
                    .replace('<g clip-path="url(#scrclip)" id="scrcontent"></g>', `<g clip-path="url(#scrclip)">${shine}</g>`);
  const withHead = (svg, extra) => svg.replace(/<svg([^>]*)>/, (m, a) => `<svg${a} role="img" aria-label="LED AD PRO"><title>LED AD PRO</title>${OUTLINE}${extra}`);
  // dark-background variant: light frame and legs, brighter letter blues, light outline
  const darkify = s => s.replace(/fill="#0E2238"/g, 'fill="#CFEFFF"').replace('stroke="#0E2238"', 'stroke="#CFEFFF"')
    .replace(/#1585D2/g, '#2A9BE6').replace(/#0562A3/g, '#0B74C0');
  const DARKLINE = '<style>#letters path,#letters rect{stroke:#7FCBEF;stroke-width:1.2}</style>';
  const files = {
    'logo-classic.svg': withHead(light.replace(shine, ''), ''),
    'logo-classic-animated.svg': withHead(light, SPIN),
    'logo-classic-dark.svg': withHead(darkify(light.replace(shine, '')), '').replace('</svg>', DARKLINE + '</svg>'),
    'logo-classic-dark-animated.svg': withHead(darkify(light), SPIN).replace('</svg>', DARKLINE + '</svg>'),
  };
  // white variant for brand-blue backgrounds (menu, bands)
  const whiten = s => s.replace(/fill="#0E2238"/g, 'fill="#FFFFFF"').replace('stroke="#0E2238"', 'stroke="#FFFFFF"')
    .replace(/#1585D2/g, '#FFFFFF').replace(/#0562A3/g, '#E4F4FD').replace(/#B4E6F8/g, '#9FDDF6').replace(/#7FCDEE/g, '#5EC0EC');
  const WHITELINE = '<style>#letters path,#letters rect{stroke:none}</style>';
  files['logo-classic-white.svg'] = withHead(whiten(light.replace(shine, '')), '').replace('</svg>', WHITELINE + '</svg>');
  files['logo-classic-white-animated.svg'] = withHead(whiten(light), SPIN).replace('</svg>', WHITELINE + '</svg>');
  for (const [f, c] of Object.entries(files)) fs.writeFileSync(path.join(OUT, f), c);
  // favicon: the O block with the globe
  const fav = base.replace(/viewBox="[^"]*"/, 'viewBox="1011 318 223 186"').replace(/<rect id="legL"[^>]*>(<\/rect>)?/, '').replace(/<rect id="legR"[^>]*>(<\/rect>)?/, '');
  fs.writeFileSync(path.join(OUT, 'favicon-classic.svg'), withHead(fav.replace(/<g id="board">[\s\S]*?<\/g>\s*<\/g>\s*<\/g>/, ''), ''));
  // PNGs
  const shot = async (svgFile, w, h, bg, out, pad = 0) => {
    const pg = await b.newPage({ viewport: { width: w, height: h } });
    const svg = fs.readFileSync(path.join(OUT, svgFile), 'utf8').replace('<svg', `<svg style="width:${w - 2 * pad}px;height:${h - 2 * pad}px;display:block"`);
    await pg.setContent(`<body style="margin:0;background:${bg};display:grid;place-items:center;height:${h}px">${svg}</body>`);
    await pg.waitForTimeout(150); await pg.screenshot({ path: path.join(OUT, out), omitBackground: bg === 'transparent' }); await pg.close();
  };
  await shot('logo-classic.svg', 1600, 629, 'transparent', 'logo-classic-1600.png');
  await shot('logo-classic-dark.svg', 1600, 629, 'transparent', 'logo-classic-dark-1600.png');
  for (const s of [32, 180, 512]) await shot('favicon-classic.svg', s, s, 'transparent', `favicon-classic-${s}.png`, Math.round(s * .04));
  await shot('logo-classic.svg', 1200, 630, '#ffffff', 'og-image-classic.png', 150);
  await b.close(); console.log(fs.readdirSync(OUT).join('\n'));
})();
