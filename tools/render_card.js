// node tools/render_card.js card.html out.pdf previewDir — print PDF (with bleed) + PNG previews (trimmed) + mockup
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [inp, out, dir] = process.argv.slice(2);
  const b = await chromium.launch(); const mm = 96 / 25.4;
  const p = await b.newPage({ viewport: { width: Math.round(95 * mm), height: Math.round(57 * mm) }, deviceScaleFactor: 6 });
  await p.goto('file://' + path.resolve(inp), { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  await p.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  const cards = await p.$$('section.card');
  for (let i = 0; i < cards.length; i++) {
    const bb = await cards[i].boundingBox();
    await p.screenshot({ fullPage: true, path: path.join(dir, `card-${i ? 'back' : 'front'}.png`), clip: { x: bb.x + 3 * mm, y: bb.y + 3 * mm, width: 89 * mm, height: 51 * mm } });
  }
  // mockup
  const m = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
  const fs = require('fs'); const du = n => 'data:image/png;base64,' + fs.readFileSync(path.join(dir, n)).toString('base64');
  await m.setContent(`<body style="margin:0;height:100vh;display:flex;gap:70px;align-items:center;justify-content:center;background:radial-gradient(circle at 30% 20%,#2a3550,#0d1222)">
    <img src="${du('card-front.png')}" style="width:640px;border-radius:10px;box-shadow:0 40px 80px rgba(0,0,0,.55);transform:rotate(-4deg)">
    <img src="${du('card-back.png')}" style="width:640px;border-radius:10px;box-shadow:0 40px 80px rgba(0,0,0,.55);transform:rotate(3deg) translateY(40px)"></body>`);
  await m.waitForTimeout(600); await m.screenshot({ path: path.join(dir, 'card-mockup.png') });
  await b.close();
})();
