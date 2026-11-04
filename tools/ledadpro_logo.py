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

# Order the L lights up in when animated: down the stem, then along the base.
L_ORDER = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]


def mark(x, y, s, lit=PINK, on=CYAN, ghost=NAVY, ghost_op=.14, animate=False):
    """3x3 LED-dot mark at (x,y), total size s. Round dots (real LEDs are round diodes).
    Lit dots draw an L; the top-right dot is the cyan 'on' light."""
    gap = s * .08; d = (s - 2 * gap) / 3; r = d / 2
    out = []
    for row in range(3):
        for col in range(3):
            cx, cy = x + col * (d + gap) + r, y + row * (d + gap) + r
            if (col, row) in L_ORDER:
                i = L_ORDER.index((col, row))
                cls = f' class="lit" style="animation-delay:{.15 + i * .12:.2f}s"' if animate else ''
                if animate:   # ghost dot underneath so the grid is there before it lights
                    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{ghost}" fill-opacity="{ghost_op}"/>')
                out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{lit}"{cls}/>')
            elif (col, row) == (2, 0):
                if animate:
                    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{ghost}" fill-opacity="{ghost_op}"/>')
                    out.append(f'<circle class="glow" cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{on}"/>')
                    out.append(f'<circle class="on" cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{on}"/>')
                else:
                    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{on}"/>')
            else:
                out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{ghost}" fill-opacity="{ghost_op}"/>')
    return ''.join(out)


ANIM_CSS = """<style>
.lit,.on{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .32s cubic-bezier(.2,.8,.2,1.25) forwards}
.on{animation:pop .36s cubic-bezier(.2,.8,.2,1.3) .95s forwards}
.glow{transform-box:fill-box;transform-origin:center;opacity:0;animation:glow 2.6s ease-in-out 1.3s infinite}
.word{opacity:0;animation:fade .7s ease-out .75s forwards}
@keyframes pop{0%{opacity:0;transform:scale(.35)}100%{opacity:1;transform:scale(1)}}
@keyframes glow{0%,100%{opacity:0;transform:scale(1)}45%{opacity:.35;transform:scale(1.9)}}
@keyframes fade{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.lit,.on,.word{animation:none;opacity:1}.glow{animation:none}}
</style>"""


def word(x, base, size, main, pro):
    glyphs, w = text_paths('LED AD PRO', x, base, size)
    d_main = ''.join(d for i, (c, d) in enumerate(glyphs) if i < 5)
    d_pro = ''.join(d for i, (c, d) in enumerate(glyphs) if i >= 5)
    return f'<path d="{d_main}" fill="{main}"/><path d="{d_pro}" fill="{pro}"/>', w

def svg(w, h, body, bg=None, title='LED AD PRO'):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{title}"><title>{title}</title>{b}{body}</svg>\n'

def horizontal(main, pro, ghost, bg=None, name='logo-horizontal', lit=PINK, on=CYAN, animate=False):
    size = 100; capH = CAP / UPM * size; pad = 40
    m = capH * 1.36                      # mark a little taller than the caps, centred on them
    base = pad + (m + capH) / 2
    wbody, ww = word(pad + m + capH * .55, base, size, main, pro)
    W = pad + m + capH * .55 + ww + pad; H = pad * 2 + m
    body = (ANIM_CSS if animate else '') + mark(pad, pad, m, lit=lit, on=on, ghost=ghost, animate=animate) + (f'<g class="word">{wbody}</g>' if animate else wbody)
    (OUT / f'{name}.svg').write_text(svg(W, H, body, bg))

def stacked(main, pro, ghost, bg=None, name='logo-stacked', animate=False):
    size = 100; capH = CAP / UPM * size; pad = 40
    _, ww = text_paths('LED AD PRO', 0, 0, size)
    W = ww + pad * 2; m = capH * 2.4
    body = (ANIM_CSS if animate else '') + mark((W - m) / 2, pad, m, ghost=ghost, animate=animate)
    wbody, _ = word(pad, pad + m + capH * .7 + capH, size, main, pro)
    H = pad + m + capH * .7 + capH + pad
    (OUT / f'{name}.svg').write_text(svg(W, H, body + (f'<g class="word">{wbody}</g>' if animate else wbody), bg))

def mark_only(ghost, bg=None, name='mark', pad=24, s=192, bgr=0, animate=False):
    W = s + pad * 2
    b = f'<rect width="{W}" height="{W}" rx="{bgr}" fill="{bg}"/>' if bg else ''
    css = ANIM_CSS if animate else ''
    (OUT / f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" width="{W}" height="{W}" role="img" aria-label="LED AD PRO"><title>LED AD PRO</title>{b}{css}{mark(pad, pad, s, ghost=ghost, animate=animate)}</svg>\n')

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
# Animated versions (play once, then the cyan 'on' light keeps a slow glow)
horizontal(NAVY, PINK, NAVY, None, 'logo-horizontal-animated', animate=True)
horizontal(WHITE, PINK, WHITE, NAVY, 'logo-horizontal-reverse-animated', animate=True)
stacked(WHITE, PINK, WHITE, NAVY, 'logo-stacked-reverse-animated', animate=True)
mark_only(NAVY, None, 'mark-animated', animate=True)
mark_only(WHITE, NAVY, 'mark-reverse-animated', animate=True)
print(sorted(p.name for p in OUT.glob('*.svg')))
