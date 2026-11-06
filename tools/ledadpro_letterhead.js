// LED AD PRO blank letterhead (A4) -> brand/ledadpro/stationery/LED-AD-PRO-Letterhead.docx
const fs = require('fs'), path = require('path');
const d = require('docx');
const S = path.join(__dirname, '../brand/ledadpro/stationery');
const img = f => fs.readFileSync(path.join(S, f));
const NAVY = '0B1B3F', PINK = '0674BB', GREY = '5B6782', FONT = 'Arial';
const mm = v => Math.round(v * 56.6929);      // mm -> twips
const emu = v => Math.round(v * 36000);       // mm -> EMU
const px = v => Math.round(v * 3.7795);       // mm -> px at 96 dpi
const TEXT_W = 11906 - 2 * mm(20);

const floating = (data, wMm, hMm, xMm, yMm) => new d.ImageRun({
  type: 'png', data, transformation: { width: px(wMm), height: px(hMm) },
  floating: {
    horizontalPosition: { relative: d.HorizontalPositionRelativeFrom.PAGE, offset: emu(xMm) },
    verticalPosition: { relative: d.VerticalPositionRelativeFrom.PAGE, offset: emu(yMm) },
    behindDocument: true, allowOverlap: true, lockAnchor: true,
  },
});
const t = (text, o = {}) => new d.TextRun({ text, font: FONT, size: 15, color: GREY, ...o });
const none = { style: d.BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: none, bottom: none, left: none, right: none };
const cell = (children, w, align) => new d.TableCell({
  width: { size: w, type: d.WidthType.DXA }, borders: noBorders, verticalAlign: d.VerticalAlign.BOTTOM,
  margins: { top: 0, bottom: 0, left: 0, right: 0 },
  children: children.map(c => new d.Paragraph({ alignment: align, spacing: { after: 20 }, children: c })),
});

const header = new d.Header({
  children: [
    new d.Paragraph({ children: [floating(img('strip.png'), 210, 2, 0, 0), floating(img('watermark.png'), 70, 70, 152, 176)] }),
    new d.Paragraph({
      tabStops: [{ type: d.TabStopType.RIGHT, position: TEXT_W }], spacing: { after: 0, line: 240, lineRule: d.LineRuleType.AUTO },
      children: [
        new d.ImageRun({ type: 'png', data: img('logo-classic-1600.png'), transformation: { width: px(46), height: px(46 * 629 / 1600) } }),
        t('\tSALES & MARKETING   ', { size: 12, bold: true, color: PINK, characterSpacing: 30 }), t('+880 1958-503753', { color: NAVY, bold: true, size: 17 }),
      ],
    }),
    new d.Paragraph({ alignment: d.AlignmentType.RIGHT, spacing: { after: 0 }, children: [t('info@ledadpro.com   ·   ledadpro.com')] }),
    new d.Paragraph({ spacing: { after: 0 }, children: [] }),
  ],
});

const footer = new d.Footer({
  children: [new d.Paragraph({
    border: { top: { style: d.BorderStyle.SINGLE, size: 4, color: 'DFE5EF', space: 6 } },
    tabStops: [{ type: d.TabStopType.RIGHT, position: TEXT_W }],
    children: [
      t('Flat A1, House 99, Road 10/2, Block D, Niketon, Gulshan 1, Dhaka', { size: 14 }),
      t('\tOffice +880 1316-743003   ·   ', { size: 14 }),
      t('OFFICIAL LED PARTNER TO AD PRO', { size: 12, bold: true, color: NAVY, characterSpacing: 20 }),
    ],
  })],
});

const doc = new d.Document({
  creator: 'LED AD PRO', title: 'LED AD PRO Letterhead',
  styles: { default: { document: { run: { font: FONT, size: 21, color: '1F2A44' }, paragraph: { spacing: { line: 320, lineRule: d.LineRuleType.AUTO, after: 120 } } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: mm(38), bottom: mm(28), left: mm(20), right: mm(20), header: mm(12), footer: mm(10) } } },
    headers: { default: header }, footers: { default: footer },
    children: [new d.Paragraph({ children: [] })],
  }],
});
d.Packer.toBuffer(doc).then(b => { const out = path.join(S, 'LED-AD-PRO-Letterhead.docx'); fs.writeFileSync(out, b); console.log(out); });
