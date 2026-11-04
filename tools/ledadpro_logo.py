"""Generate the LED AD PRO logo set as SVG (text outlined, no font needed).
Mark: 3x3 LED pixel grid; lit pixels form an L (pink), top-right pixel is the cyan "on" light,
the rest are faint ghost pixels. Wordmark: Inter Display Black, navy with PRO in pink."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = Path(__file__).resolve().parent.parent / 'brand/ledadpro/logo'
NAVY, PINK, CYAN, WHITE = '#0B1B3F', '#FF1F6E', '#00C2F2', '#FFFFFF'
FONT = TTFont('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf')
GS, CMAP, UPM = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['head'].unitsPerEm
CAP = FONT['OS/2'].sCapHeight

def text_paths(s, x, y, size, track=-0.01, word_gap=0.18):
    """Return [(path_d, width_of_glyph)] for each char, plus total width. y = baseline."""
    scale, out, cx = size / UPM, [], x
    for ch in s:
        if ch == ' ':
            cx += size * word_gap; continue
        g = CMAP[ord(ch)]; pen = SVGPathPen(GS)
        GS[g].draw(TransformPen(pen, (scale, 0, 0, -scale, cx, y)))
        out.append((ch, pen.getCommands()))
        cx += GS[g].width * scale + size * track
    return out, cx - x - size * track

def mark(x, y, s, lit=PINK, on=CYAN, ghost=NAVY, ghost_op=.14, r=.16):
    """3x3 pixel mark at (x,y) with total size s."""
    gap = s * .1; p = (s - 2 * gap) / 3; rr = p * r
    L = {(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)}
    out = []
    for row in range(3):
        for col in range(3):
            px, py = x + col * (p + gap), y + row * (p + gap)
            if (col, row) in L: fill, op = lit, 1
            elif (col, row) == (2, 0): fill, op = on, 1
            else: fill, op = ghost, ghost_op
            if op == 0: continue
            opa = f' fill-opacity="{op}"' if op < 1 else ''
            out.append(f'<rect x="{px:.2f}" y="{py:.2f}" width="{p:.2f}" height="{p:.2f}" rx="{rr:.2f}" fill="{fill}"{opa}/>')
    return ''.join(out)

def word(x, base, size, main, pro):
    glyphs, w = text_paths('LED AD PRO', x, base, size)
    d_main = ''.join(d for i, (c, d) in enumerate(glyphs) if i < 5)
    d_pro = ''.join(d for i, (c, d) in enumerate(glyphs) if i >= 5)
    return f'<path d="{d_main}" fill="{main}"/><path d="{d_pro}" fill="{pro}"/>', w

def svg(w, h, body, bg=None, title='LED AD PRO'):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{title}"><title>{title}</title>{b}{body}</svg>\n'

def horizontal(main, pro, ghost, bg=None, name='logo-horizontal', lit=PINK, on=CYAN):
    size = 100; capH = CAP / UPM * size; pad = 40
    m = capH * 1.36                      # mark a little taller than the caps, centred on them
    base = pad + (m + capH) / 2
    wbody, ww = word(pad + m + capH * .55, base, size, main, pro)
    W = pad + m + capH * .55 + ww + pad; H = pad * 2 + m
    body = mark(pad, pad, m, lit=lit, on=on, ghost=ghost) + wbody
    (OUT / f'{name}.svg').write_text(svg(W, H, body, bg))

def stacked(main, pro, ghost, bg=None, name='logo-stacked'):
    size = 100; capH = CAP / UPM * size; pad = 40
    _, ww = text_paths('LED AD PRO', 0, 0, size)
    W = ww + pad * 2; m = capH * 2.4
    body = mark((W - m) / 2, pad, m, ghost=ghost)
    wbody, _ = word(pad, pad + m + capH * .7 + capH, size, main, pro)
    H = pad + m + capH * .7 + capH + pad
    (OUT / f'{name}.svg').write_text(svg(W, H, body + wbody, bg))

def mark_only(ghost, bg=None, name='mark', pad=24, s=192, bgr=0):
    W = s + pad * 2
    b = f'<rect width="{W}" height="{W}" rx="{bgr}" fill="{bg}"/>' if bg else ''
    (OUT / f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" width="{W}" height="{W}" role="img" aria-label="LED AD PRO"><title>LED AD PRO</title>{b}{mark(pad, pad, s, ghost=ghost)}</svg>\n')

OUT.mkdir(parents=True, exist_ok=True)
horizontal(NAVY, PINK, NAVY)                                        # primary, on light
horizontal(WHITE, PINK, WHITE, NAVY, 'logo-horizontal-reverse')     # on navy
stacked(NAVY, PINK, NAVY)
stacked(WHITE, PINK, WHITE, NAVY, 'logo-stacked-reverse')
horizontal('#000', '#000', '#000', None, 'logo-mono-black', '#000', '#000')
horizontal(WHITE, WHITE, WHITE, '#000', 'logo-mono-white', WHITE, WHITE)
mark_only(NAVY)
mark_only(WHITE, NAVY, 'mark-reverse')
mark_only(WHITE, NAVY, 'favicon', pad=40, s=176, bgr=56)            # app icon / favicon
print(sorted(p.name for p in OUT.glob('*.svg')))
