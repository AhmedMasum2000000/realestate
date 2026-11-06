// node tools/render_pdf.js in.html out.pdf [sheet.png]  — renders a print-sized HTML doc to PDF (+ optional page sheet)
const { chromium } = require('playwright');
(async () => {
  const [inp, out, sheet] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1123, height: 631 } });
  await p.goto('file://' + require('path').resolve(inp), { waitUntil: 'networkidle' }); await p.waitForTimeout(1200);
  await p.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  if (sheet) { const s = await p.$$('section.pg'); for (let i = 0; i < s.length; i++) await s[i].screenshot({ path: sheet.replace('.png', '-' + (i + 1) + '.png') }); }
  await b.close();
})();
