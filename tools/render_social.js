// node tools/render_social.js file.html W H out.png  — renders a fixed-size social design to PNG (and JPG alongside)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [inp, w, h, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(inp), { waitUntil: 'networkidle' }); await p.waitForTimeout(500);
  await p.screenshot({ path: out });
  await p.screenshot({ path: out.replace(/\.png$/, '.jpg'), type: 'jpeg', quality: 92 });
  await b.close();
})();
