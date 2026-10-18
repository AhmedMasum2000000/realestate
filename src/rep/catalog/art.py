"""Placeholder illustrations.

Most listings have no photograph, and a broken-image grid reads as a broken
site. These are deliberate brand-coloured silhouettes rather than grey boxes:
a card without a photo should still look designed.

Variants are chosen from the reference string so the grid has rhythm, and
because the reference never changes the choice is stable across rebuilds.
"""

from __future__ import annotations

_SKY = "#16244C"
_SKY_2 = "#0E1734"
_FORM = "#22346B"
_GOLD = "#C9A86E"
_GOLD_DIM = "#8E7548"


# Background tones, cycled independently of composition so a grid of cards
# reads as varied rather than tiled.
_GROUNDS = ["#0E1734", "#132046", "#101A3A", "#16244C", "#0C1530", "#142452"]


def _frame(body: str, tone: int = 0) -> str:
    ground = _GROUNDS[tone % len(_GROUNDS)]
    return (
        '<svg viewBox="0 0 400 300" role="img" aria-hidden="true" '
        'preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
        f'<rect width="400" height="300" fill="{ground}"/>{body}</svg>'
    )


def _tower(v: int, tone: int = 0) -> str:
    a, b, left, moon = [
        (150, 60, 138, 322), (120, 40, 108, 300), (175, 80, 158, 340),
        (196, 96, 92, 296), (134, 168, 176, 344), (162, 112, 126, 312),
    ][v]
    rows = "".join(
        f'<rect x="{left + 12 + i * 22}" y="{y}" width="14" height="9" '
        f'fill="{_GOLD}" opacity=".35"/>'
        for y in range(300 - a + 18, 282, 24)
        for i in range(3)
    )
    return _frame(
        f'<circle cx="{moon}" cy="62" r="26" fill="{_GOLD}" opacity=".2"/>'
        f'<rect x="{left + 104}" y="{300 - b}" width="72" height="{b}" fill="{_FORM}"/>'
        f'<rect x="{left}" y="{300 - a}" width="82" height="{a}" fill="{_SKY}"/>'
        f'{rows}'
        f'<rect x="0" y="272" width="400" height="28" fill="{_GOLD_DIM}" opacity=".28"/>',
        tone,
    )


def _villa(v: int, tone: int = 0) -> str:
    lift = [0, 12, -8, 6, -14, 18][v]
    return _frame(
        f'<circle cx="330" cy="58" r="24" fill="{_GOLD}" opacity=".2"/>'
        f'<rect x="0" y="216" width="400" height="84" fill="{_SKY}" opacity=".55"/>'
        f'<rect x="96" y="{140 + lift}" width="176" height="82" fill="{_FORM}"/>'
        f'<path d="M78 {142 + lift} L184 {88 + lift} L290 {142 + lift} Z" fill="{_GOLD_DIM}"/>'
        f'<rect x="120" y="{166 + lift}" width="32" height="30" fill="{_GOLD}" opacity=".4"/>'
        f'<rect x="170" y="{166 + lift}" width="32" height="30" fill="{_GOLD}" opacity=".4"/>'
        f'<rect x="222" y="{162 + lift}" width="26" height="60" fill="{_GOLD_DIM}" opacity=".5"/>'
        f'<rect x="64" y="238" width="272" height="40" rx="4" fill="{_GOLD}" opacity=".18"/>'
        f'<ellipse cx="348" cy="150" rx="12" ry="34" fill="{_GOLD_DIM}" opacity=".45"/>',
        tone,
    )


def _shop(v: int, tone: int = 0) -> str:
    bays = [7, 5, 9, 6, 8, 4][v]
    step = 284 / bays
    awning = "".join(
        f'<rect x="{58 + i * step:.1f}" y="118" width="{step / 2:.1f}" height="14" '
        f'fill="{_GOLD if i % 2 else _GOLD_DIM}" opacity=".7"/>'
        for i in range(bays)
    )
    return _frame(
        f'<rect x="0" y="240" width="400" height="60" fill="{_SKY}" opacity=".6"/>'
        f'<rect x="58" y="92" width="284" height="148" fill="{_FORM}"/>'
        f'<rect x="58" y="92" width="284" height="26" fill="{_GOLD_DIM}" opacity=".75"/>'
        f'{awning}'
        f'<rect x="92" y="156" width="74" height="84" fill="{_GOLD}" opacity=".3"/>'
        f'<rect x="186" y="156" width="74" height="84" fill="{_GOLD}" opacity=".3"/>'
        f'<rect x="282" y="172" width="40" height="68" fill="{_GOLD_DIM}" opacity=".55"/>',
        tone,
    )


def _land(v: int, tone: int = 0) -> str:
    ridge = [
        "M0 186 L96 148 L188 176 L272 144 L400 182",
        "M0 196 L110 158 L206 188 L300 152 L400 176",
        "M0 178 L88 160 L180 168 L288 138 L400 190",
        "M0 204 L120 166 L214 196 L318 160 L400 194",
        "M0 172 L80 152 L172 182 L280 148 L400 178",
        "M0 190 L104 172 L196 158 L296 182 L400 164",
    ][v]
    pegs = [(84, 234), (162, 194), (306, 212), (230, 256)]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{_GOLD}"/>' for x, y in pegs)
    return _frame(
        f'<circle cx="318" cy="56" r="22" fill="{_GOLD}" opacity=".22"/>'
        f'<path d="{ridge} L400 300 L0 300 Z" fill="{_SKY}" opacity=".7"/>'
        f'<path d="M84 234 L162 194 L306 212 L230 256 Z" fill="none" '
        f'stroke="{_GOLD}" stroke-width="3" stroke-dasharray="10 7" opacity=".85"/>'
        f'{dots}',
        tone,
    )


_RENDERERS = {
    "condos": _tower,
    "apartments": _tower,
    "hotels": _tower,
    "pool-villas": _villa,
    "houses": _villa,
    "townhouses": _villa,
    "businesses": _shop,
    "commercial": _shop,
    "land": _land,
}


def placeholder(type_slug: str, reference: str) -> str:
    render = _RENDERERS.get(type_slug, _tower)
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(reference))
    # Composition and tone are seeded separately so neighbouring references
    # do not land on the same pairing.
    return render(seed % 6, (seed // 6) % len(_GROUNDS))
