"""Render a standalone homepage for each site from previews/spec.yml.

These are the real page designs, not mockups: the copy and structure here are
what gets written into WordPress once provisioning runs. Each site has its own
palette, type pairing and layout archetype, because these are eight different
businesses rather than one template with the name swapped.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .config import ROOT

SPEC_FILE = ROOT / "previews" / "spec.yml"
OUT_DIR = ROOT / "previews" / "out"

VALID_ARCHETYPES = {"listings", "advisory", "product"}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

REQUIRED_PALETTE = (
    "ink", "accent", "accent2", "ground", "surface",
    "ink_dark", "accent_dark", "accent2_dark", "ground_dark", "surface_dark",
)


class SpecError(Exception):
    """The preview spec is wrong in a way we can explain."""


@dataclass
class PreviewSite:
    raw: dict[str, Any]

    def __getattr__(self, key: str) -> Any:
        try:
            return self.raw[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)


def load_spec(path: Path | None = None) -> list[PreviewSite]:
    path = path or SPEC_FILE
    if not path.exists():
        raise SpecError(f"missing {path}")
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sites = doc.get("sites") or []
    if not sites:
        raise SpecError(f"{path} has no `sites:` list")

    out: list[PreviewSite] = []
    for raw in sites:
        domain = raw.get("domain", "?")
        if raw.get("archetype") not in VALID_ARCHETYPES:
            raise SpecError(
                f"{domain}: archetype {raw.get('archetype')!r} is not one of "
                f"{sorted(VALID_ARCHETYPES)}"
            )
        palette = raw.get("palette") or {}
        for key in REQUIRED_PALETTE:
            value = palette.get(key)
            if not value or not HEX_RE.match(str(value)):
                raise SpecError(
                    f"{domain}: palette.{key} is {value!r}; expected a #rrggbb colour"
                )
        out.append(PreviewSite(raw))
    return out


def e(text: Any) -> str:
    return html.escape(str(text or "")).strip()


# -- illustrations ----------------------------------------------------------
# Drawn rather than photographed: a real photograph would either be a stock
# image with a licence question or a picture of a property that is not theirs.

ILLUSTRATIONS = {
    "tower": """
      <rect width="400" height="300" fill="url(#g-sky)"/>
      <rect x="236" y="84" width="72" height="216" fill="var(--c-stone2)"/>
      <rect x="118" y="38" width="114" height="262" fill="var(--c-stone)"/>
      <g fill="var(--c-glass)" opacity=".7">
        <rect x="132" y="58" width="27" height="17"/><rect x="169" y="58" width="27" height="17"/>
        <rect x="132" y="91" width="27" height="17"/><rect x="169" y="91" width="27" height="17"/>
        <rect x="132" y="124" width="27" height="17"/><rect x="169" y="124" width="27" height="17"/>
        <rect x="132" y="157" width="27" height="17"/><rect x="169" y="157" width="27" height="17"/>
        <rect x="132" y="190" width="27" height="17"/><rect x="169" y="190" width="27" height="17"/>
        <rect x="248" y="104" width="21" height="15"/><rect x="277" y="104" width="21" height="15"/>
        <rect x="248" y="135" width="21" height="15"/><rect x="277" y="135" width="21" height="15"/>
        <rect x="248" y="166" width="21" height="15"/><rect x="277" y="166" width="21" height="15"/>
      </g>
      <rect x="0" y="262" width="400" height="38" fill="var(--c-water)"/>
      <circle cx="332" cy="58" r="19" fill="var(--c-sun)" opacity=".85"/>
    """,
    "villa": """
      <rect width="400" height="300" fill="url(#g-sky)"/>
      <rect x="0" y="212" width="400" height="88" fill="var(--c-palm)" opacity=".3"/>
      <rect x="84" y="130" width="182" height="94" fill="var(--c-stone)"/>
      <path d="M68 132 L175 72 L282 132 Z" fill="var(--c-roof)"/>
      <rect x="110" y="162" width="35" height="35" fill="var(--c-glass)" opacity=".8"/>
      <rect x="163" y="162" width="35" height="35" fill="var(--c-glass)" opacity=".8"/>
      <rect x="214" y="158" width="31" height="66" fill="var(--c-roof)" opacity=".5"/>
      <rect x="58" y="236" width="288" height="44" rx="8" fill="var(--c-water)"/>
      <ellipse cx="344" cy="148" rx="12" ry="34" fill="var(--c-palm)"/>
      <rect x="340" y="148" width="6" height="84" fill="var(--c-roof)" opacity=".55"/>
    """,
    "islands": """
      <rect width="400" height="300" fill="url(#g-sky)"/>
      <circle cx="322" cy="64" r="22" fill="var(--c-sun)" opacity=".85"/>
      <path d="M0 176 L74 104 L132 152 L186 112 L248 176 Z" fill="var(--c-stone2)"/>
      <path d="M132 176 L200 122 L268 176 Z" fill="var(--c-stone)"/>
      <path d="M236 176 L306 118 L376 176 Z" fill="var(--c-stone2)" opacity=".8"/>
      <rect x="0" y="176" width="400" height="124" fill="var(--c-water)"/>
      <g fill="var(--c-glass)" opacity=".28">
        <rect x="24" y="204" width="86" height="4" rx="2"/>
        <rect x="150" y="226" width="120" height="4" rx="2"/>
        <rect x="56" y="252" width="98" height="4" rx="2"/>
        <rect x="240" y="268" width="110" height="4" rx="2"/>
      </g>
      <ellipse cx="72" cy="150" rx="11" ry="28" fill="var(--c-palm)"/>
      <rect x="69" y="150" width="5" height="30" fill="var(--c-roof)" opacity=".6"/>
      <ellipse cx="330" cy="152" rx="10" ry="24" fill="var(--c-palm)"/>
      <rect x="327" y="152" width="5" height="26" fill="var(--c-roof)" opacity=".6"/>
    """,
    "documents": """
      <rect width="400" height="300" fill="url(#g-sky)"/>
      <g transform="rotate(-7 150 160)">
        <rect x="72" y="72" width="150" height="192" rx="6" fill="var(--c-stone2)" opacity=".55"/>
      </g>
      <rect x="106" y="58" width="156" height="200" rx="6" fill="var(--c-glass)"/>
      <rect x="106" y="58" width="156" height="200" rx="6" fill="none" stroke="var(--c-stone2)" stroke-width="2"/>
      <g fill="var(--c-stone2)" opacity=".8">
        <rect x="126" y="86" width="86" height="9" rx="4"/>
        <rect x="126" y="112" width="116" height="6" rx="3"/>
        <rect x="126" y="128" width="116" height="6" rx="3"/>
        <rect x="126" y="144" width="92" height="6" rx="3"/>
        <rect x="126" y="172" width="116" height="6" rx="3"/>
        <rect x="126" y="188" width="104" height="6" rx="3"/>
      </g>
      <circle cx="252" cy="220" r="34" fill="var(--c-sun)" opacity=".3"/>
      <circle cx="252" cy="220" r="34" fill="none" stroke="var(--c-sun)" stroke-width="3"/>
      <path d="M236 220 L248 232 L270 208" fill="none" stroke="var(--c-roof)" stroke-width="5"
            stroke-linecap="round" stroke-linejoin="round"/>
    """,
    "town": """
      <rect width="400" height="300" fill="url(#g-sky)"/>
      <rect x="0" y="238" width="400" height="62" fill="var(--c-stone2)" opacity=".45"/>
      <rect x="46" y="120" width="94" height="120" fill="var(--c-stone)"/>
      <rect x="149" y="96" width="94" height="144" fill="var(--c-stone2)"/>
      <rect x="252" y="132" width="94" height="108" fill="var(--c-stone)"/>
      <path d="M38 122 L93 82 L148 122 Z" fill="var(--c-roof)"/>
      <path d="M141 98 L196 58 L251 98 Z" fill="var(--c-roof)"/>
      <path d="M244 134 L299 94 L354 134 Z" fill="var(--c-roof)"/>
      <g fill="var(--c-glass)" opacity=".8">
        <rect x="66" y="146" width="25" height="23"/><rect x="101" y="146" width="25" height="23"/>
        <rect x="169" y="124" width="25" height="23"/><rect x="204" y="124" width="25" height="23"/>
        <rect x="272" y="158" width="25" height="23"/><rect x="307" y="158" width="25" height="23"/>
      </g>
      <rect x="182" y="188" width="29" height="52" fill="var(--c-roof)" opacity=".6"/>
    """,
    "passport": """
      <rect width="400" height="300" fill="url(#g-sky)"/>
      <rect x="112" y="52" width="176" height="212" rx="10" fill="var(--c-stone)"/>
      <rect x="126" y="66" width="148" height="184" rx="6" fill="var(--c-stone2)" opacity=".55"/>
      <circle cx="200" cy="132" r="38" fill="none" stroke="var(--c-roof)" stroke-width="4"/>
      <ellipse cx="200" cy="132" rx="16" ry="38" fill="none" stroke="var(--c-roof)" stroke-width="3"/>
      <line x1="162" y1="132" x2="238" y2="132" stroke="var(--c-roof)" stroke-width="3"/>
      <line x1="168" y1="110" x2="232" y2="110" stroke="var(--c-roof)" stroke-width="2" opacity=".7"/>
      <line x1="168" y1="154" x2="232" y2="154" stroke="var(--c-roof)" stroke-width="2" opacity=".7"/>
      <g fill="var(--c-roof)" opacity=".5">
        <rect x="150" y="192" width="100" height="7" rx="3"/>
        <rect x="150" y="208" width="76" height="7" rx="3"/>
        <rect x="150" y="224" width="88" height="7" rx="3"/>
      </g>
      <circle cx="288" cy="212" r="34" fill="var(--c-sun)" opacity=".35"/>
      <circle cx="288" cy="212" r="34" fill="none" stroke="var(--c-sun)" stroke-width="3"/>
    """,
    "journey": """
      <rect width="400" height="300" fill="url(#g-sky)"/>
      <path d="M20 250 Q 110 250 130 200 T 250 130 T 380 70"
            fill="none" stroke="var(--c-roof)" stroke-width="4" stroke-dasharray="10 9" opacity=".65"/>
      <circle cx="20" cy="250" r="11" fill="var(--c-stone2)"/>
      <circle cx="130" cy="200" r="9" fill="var(--c-roof)" opacity=".8"/>
      <circle cx="250" cy="130" r="9" fill="var(--c-roof)" opacity=".8"/>
      <g transform="translate(356 62) rotate(-28)">
        <path d="M0 0 L34 11 L0 22 L7 11 Z" fill="var(--c-sun)"/>
      </g>
      <rect x="52" y="196" width="46" height="62" fill="var(--c-stone)"/>
      <path d="M46 198 L75 178 L104 198 Z" fill="var(--c-roof)"/>
      <rect x="286" y="150" width="52" height="52" fill="var(--c-stone)" opacity=".65"/>
      <path d="M280 152 L312 130 L344 152 Z" fill="var(--c-roof)" opacity=".7"/>
    """,
    "shares": """
      <rect width="400" height="300" fill="url(#g-sky)"/>
      <rect x="120" y="126" width="160" height="102" fill="var(--c-stone)"/>
      <path d="M104 128 L200 68 L296 128 Z" fill="var(--c-roof)"/>
      <rect x="146" y="158" width="32" height="32" fill="var(--c-glass)" opacity=".8"/>
      <rect x="222" y="158" width="32" height="32" fill="var(--c-glass)" opacity=".8"/>
      <rect x="186" y="188" width="28" height="40" fill="var(--c-roof)" opacity=".55"/>
      <g stroke="var(--c-water)" stroke-width="3" fill="none" opacity=".85">
        <circle cx="200" cy="176" r="98" stroke-dasharray="60 17"/>
      </g>
      <g fill="var(--c-water)">
        <circle cx="200" cy="78" r="9"/><circle cx="269" cy="107" r="9"/>
        <circle cx="298" cy="176" r="9"/><circle cx="269" cy="245" r="9"/>
        <circle cx="200" cy="274" r="9"/><circle cx="131" cy="245" r="9"/>
        <circle cx="102" cy="176" r="9"/><circle cx="131" cy="107" r="9"/>
      </g>
      <circle cx="200" cy="78" r="15" fill="none" stroke="var(--c-sun)" stroke-width="3"/>
    """,
}


# -- CSS --------------------------------------------------------------------

def css(site: PreviewSite) -> str:
    """Per-site stylesheet. The palette is defined in full on bare :root, and
    only re-declared for dark, so the page renders correctly in all three
    viewer states (explicit light, explicit dark, and unstamped system)."""
    p = site.palette
    return f"""
:root {{
  --ink:{p['ink']}; --ground:{p['ground']}; --surface:{p['surface']};
  --accent:{p['accent']}; --accent2:{p['accent2']};
  --ink-soft:color-mix(in srgb, {p['ink']} 72%, {p['ground']});
  --muted:color-mix(in srgb, {p['ink']} 52%, {p['ground']});
  --line:color-mix(in srgb, {p['ink']} 14%, {p['ground']});
  --accent-soft:color-mix(in srgb, {p['accent']} 12%, {p['surface']});
  --on-accent:#fff;
  --c-sky1:color-mix(in srgb, {p['accent']} 26%, {p['ground']});
  --c-sky2:color-mix(in srgb, {p['accent']} 8%, {p['ground']});
  --c-stone:color-mix(in srgb, {p['ink']} 18%, {p['ground']});
  --c-stone2:color-mix(in srgb, {p['ink']} 28%, {p['ground']});
  --c-roof:{p['accent']}; --c-water:color-mix(in srgb, {p['accent']} 55%, {p['ground']});
  --c-glass:{p['surface']}; --c-sun:{p['accent2']};
  --c-palm:color-mix(in srgb, {p['accent']} 42%, {p['ground']});
  --shadow:0 1px 2px rgba(0,0,0,.05), 0 14px 34px -18px rgba(0,0,0,.28);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ink:{p['ink_dark']}; --ground:{p['ground_dark']}; --surface:{p['surface_dark']};
    --accent:{p['accent_dark']}; --accent2:{p['accent2_dark']};
    --ink-soft:color-mix(in srgb, {p['ink_dark']} 78%, {p['ground_dark']});
    --muted:color-mix(in srgb, {p['ink_dark']} 55%, {p['ground_dark']});
    --line:color-mix(in srgb, {p['ink_dark']} 18%, {p['ground_dark']});
    --accent-soft:color-mix(in srgb, {p['accent_dark']} 16%, {p['surface_dark']});
    --on-accent:{p['ground_dark']};
    --c-sky1:color-mix(in srgb, {p['accent_dark']} 24%, {p['ground_dark']});
    --c-sky2:color-mix(in srgb, {p['accent_dark']} 8%, {p['ground_dark']});
    --c-stone:color-mix(in srgb, {p['ink_dark']} 16%, {p['ground_dark']});
    --c-stone2:color-mix(in srgb, {p['ink_dark']} 26%, {p['ground_dark']});
    --c-roof:{p['accent_dark']}; --c-water:color-mix(in srgb, {p['accent_dark']} 45%, {p['ground_dark']});
    --c-glass:{p['surface_dark']}; --c-sun:{p['accent2_dark']};
    --c-palm:color-mix(in srgb, {p['accent_dark']} 38%, {p['ground_dark']});
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 14px 34px -18px rgba(0,0,0,.7);
  }}
}}
:root[data-theme="dark"] {{
  --ink:{p['ink_dark']}; --ground:{p['ground_dark']}; --surface:{p['surface_dark']};
  --accent:{p['accent_dark']}; --accent2:{p['accent2_dark']};
  --ink-soft:color-mix(in srgb, {p['ink_dark']} 78%, {p['ground_dark']});
  --muted:color-mix(in srgb, {p['ink_dark']} 55%, {p['ground_dark']});
  --line:color-mix(in srgb, {p['ink_dark']} 18%, {p['ground_dark']});
  --accent-soft:color-mix(in srgb, {p['accent_dark']} 16%, {p['surface_dark']});
  --on-accent:{p['ground_dark']};
  --c-sky1:color-mix(in srgb, {p['accent_dark']} 24%, {p['ground_dark']});
  --c-sky2:color-mix(in srgb, {p['accent_dark']} 8%, {p['ground_dark']});
  --c-stone:color-mix(in srgb, {p['ink_dark']} 16%, {p['ground_dark']});
  --c-stone2:color-mix(in srgb, {p['ink_dark']} 26%, {p['ground_dark']});
  --c-roof:{p['accent_dark']}; --c-water:color-mix(in srgb, {p['accent_dark']} 45%, {p['ground_dark']});
  --c-glass:{p['surface_dark']}; --c-sun:{p['accent2_dark']};
  --c-palm:color-mix(in srgb, {p['accent_dark']} 38%, {p['ground_dark']});
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 14px 34px -18px rgba(0,0,0,.7);
}}

*,*::before,*::after {{ box-sizing:border-box; }}
body {{ background:var(--ground); color:var(--ink);
  font-family:{site.fonts['body_stack']}; font-size:16px; line-height:1.65;
  -webkit-font-smoothing:antialiased; }}
h1,h2,h3,.display {{ font-family:{site.fonts['display_stack']}; font-weight:600;
  line-height:1.12; letter-spacing:-.012em; text-wrap:balance; margin:0; }}
a {{ color:var(--accent); }}
a:focus-visible, button:focus-visible {{ outline:2px solid var(--accent); outline-offset:3px; border-radius:4px; }}
img,svg {{ max-width:100%; }}

.draft {{ background:var(--accent); color:var(--on-accent); text-align:center;
  padding:.5rem 1rem; font-size:.8rem; letter-spacing:.06em; text-transform:uppercase;
  font-family:{site.fonts['body_stack']}; font-weight:600; }}

.bar {{ border-bottom:1px solid var(--line); background:var(--surface); }}
.bar__in {{ max-width:72rem; margin:0 auto; padding:.9rem clamp(1rem,3vw,2rem);
  display:flex; align-items:center; gap:1.5rem; }}
.brand {{ display:flex; align-items:center; gap:.6rem; font-family:{site.fonts['display_stack']};
  font-weight:600; font-size:1.12rem; letter-spacing:-.01em; }}
.brand__mark {{ width:30px; height:30px; border-radius:7px; background:var(--accent);
  display:grid; place-items:center; color:var(--on-accent); font-size:.82rem; font-weight:700;
  font-family:{site.fonts['body_stack']}; flex:none; }}
.nav {{ margin-left:auto; display:flex; gap:1.4rem; font-size:.92rem; }}
.nav a {{ color:var(--ink-soft); text-decoration:none; }}
.nav a:hover {{ color:var(--accent); }}
@media (max-width:46rem) {{ .nav {{ display:none; }} }}

.wrap {{ max-width:72rem; margin:0 auto; padding:0 clamp(1rem,3vw,2rem); }}
section {{ padding:clamp(2.75rem,6vw,4.5rem) 0; }}
.eyebrow {{ font-size:.74rem; letter-spacing:.15em; text-transform:uppercase;
  color:var(--accent); font-weight:600; font-family:{site.fonts['body_stack']}; }}
.h2 {{ font-size:clamp(1.6rem,3.6vw,2.3rem); margin:.5rem 0 0; }}
.sub {{ color:var(--muted); margin:.6rem 0 0; max-width:40rem; }}

.hero {{ display:grid; grid-template-columns:1.15fr .85fr; gap:clamp(1.5rem,4vw,3.5rem);
  align-items:center; padding:clamp(2.5rem,6vw,4.5rem) 0; }}
@media (max-width:54rem) {{ .hero {{ grid-template-columns:1fr; }} }}
.hero h1 {{ font-size:clamp(2.1rem,5.4vw,3.5rem); }}
.hero p {{ color:var(--ink-soft); font-size:1.08rem; margin:1rem 0 0; max-width:34rem; }}
.hero__art {{ border-radius:14px; overflow:hidden; box-shadow:var(--shadow); aspect-ratio:4/3; }}
.hero__art svg {{ width:100%; height:100%; display:block; }}

.actions {{ display:flex; flex-wrap:wrap; gap:.75rem; margin-top:1.6rem; }}
.btn {{ display:inline-block; padding:.72rem 1.5rem; border-radius:7px; text-decoration:none;
  font-weight:600; font-size:.95rem; font-family:{site.fonts['body_stack']}; }}
.btn--primary {{ background:var(--accent); color:var(--on-accent); }}
.btn--ghost {{ border:1px solid var(--line); color:var(--ink); background:var(--surface); }}

.searchbar {{ background:var(--surface); border:1px solid var(--line); border-radius:10px;
  padding:1rem; display:flex; flex-wrap:wrap; gap:.75rem; align-items:end; box-shadow:var(--shadow); }}
.field {{ display:flex; flex-direction:column; gap:.25rem; font-size:.76rem; color:var(--muted);
  font-family:{site.fonts['body_stack']}; letter-spacing:.04em; text-transform:uppercase; }}
.field select {{ padding:.5rem .65rem; border:1px solid var(--line); border-radius:6px;
  font:inherit; font-size:.95rem; text-transform:none; letter-spacing:0; min-width:9.5rem;
  background:var(--surface); color:var(--ink); }}
.searchbar .btn {{ padding:.6rem 1.35rem; }}

.grid3 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));
  gap:1.25rem; margin-top:1.75rem; }}
.card {{ background:var(--surface); border:1px solid var(--line); border-radius:11px;
  overflow:hidden; display:flex; flex-direction:column; box-shadow:var(--shadow); }}
.card__art {{ aspect-ratio:4/3; background:var(--c-sky2); position:relative; }}
.card__art svg {{ width:100%; height:100%; display:block; }}
.tag {{ position:absolute; top:.65rem; left:.65rem; background:var(--accent); color:var(--on-accent);
  font-size:.68rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
  padding:.18rem .55rem; border-radius:100px; font-family:{site.fonts['body_stack']}; }}
.tag--alt {{ background:var(--accent2); }}
.card__body {{ padding:.95rem 1.1rem 1.15rem; display:flex; flex-direction:column; gap:.3rem; flex:1; }}
.card__place {{ font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted);
  font-family:{site.fonts['body_stack']}; }}
.card__title {{ font-size:1.06rem; }}
.card__price {{ font-weight:600; color:var(--accent); font-variant-numeric:tabular-nums;
  font-family:{site.fonts['body_stack']}; }}
.card__facts {{ list-style:none; display:flex; flex-wrap:wrap; gap:.85rem; padding:0; margin:.2rem 0 0;
  font-size:.85rem; color:var(--muted); font-family:{site.fonts['body_stack']}; }}
.card__facts strong {{ color:var(--ink-soft); font-variant-numeric:tabular-nums; }}

.points {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(16rem,1fr)); gap:1.5rem; margin-top:1.75rem; }}
.point h3 {{ font-size:1.12rem; margin-bottom:.35rem; }}
.point p {{ color:var(--muted); margin:0; font-size:.95rem; }}
.point__rule {{ width:2.2rem; height:3px; background:var(--accent2); border-radius:2px; margin-bottom:.85rem; }}

.steps {{ counter-reset:s; display:flex; flex-direction:column; gap:1px; margin-top:1.75rem;
  background:var(--line); border:1px solid var(--line); border-radius:11px; overflow:hidden; }}
.step {{ background:var(--surface); padding:1.25rem 1.4rem; display:flex; gap:1.15rem; align-items:flex-start; }}
.step::before {{ counter-increment:s; content:counter(s,decimal-leading-zero);
  font-family:{site.fonts['body_stack']}; font-size:.8rem; font-weight:700; color:var(--accent);
  background:var(--accent-soft); border-radius:6px; padding:.3rem .5rem; flex:none; }}
.step h3 {{ font-size:1.08rem; margin-bottom:.2rem; }}
.step p {{ color:var(--muted); margin:0; font-size:.95rem; }}

.chips {{ list-style:none; display:flex; flex-wrap:wrap; gap:.55rem; padding:0; margin:1.5rem 0 0; }}
.chips a {{ display:inline-block; padding:.42rem .95rem; border:1px solid var(--line); border-radius:100px;
  text-decoration:none; color:var(--ink); background:var(--surface); font-size:.9rem;
  font-family:{site.fonts['body_stack']}; }}
.chips a:hover {{ border-color:var(--accent); color:var(--accent); }}

.band {{ background:var(--surface); border-top:1px solid var(--line); border-bottom:1px solid var(--line); }}
.cta {{ background:var(--accent); color:var(--on-accent); border-radius:14px;
  padding:clamp(1.75rem,4vw,3rem); display:flex; flex-wrap:wrap; gap:1.5rem;
  align-items:center; justify-content:space-between; }}
.cta h2 {{ font-size:clamp(1.4rem,3vw,2rem); max-width:26rem; }}
.cta p {{ margin:.5rem 0 0; opacity:.85; max-width:28rem; }}
.cta .btn {{ background:var(--surface); color:var(--accent); }}

footer {{ border-top:1px solid var(--line); background:var(--surface); }}
.foot {{ max-width:72rem; margin:0 auto; padding:2.25rem clamp(1rem,3vw,2rem);
  display:grid; grid-template-columns:repeat(auto-fit,minmax(12rem,1fr)); gap:1.75rem; }}
.foot h4 {{ font-size:.78rem; letter-spacing:.12em; text-transform:uppercase; color:var(--muted);
  margin:0 0 .6rem; font-family:{site.fonts['body_stack']}; font-weight:600; }}
.foot ul {{ list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:.35rem;
  font-size:.92rem; }}
.foot a {{ color:var(--ink-soft); text-decoration:none; }}
.foot a:hover {{ color:var(--accent); }}
.foot__base {{ border-top:1px solid var(--line); }}
.foot__base div {{ max-width:72rem; margin:0 auto; padding:1rem clamp(1rem,3vw,2rem);
  font-size:.84rem; color:var(--muted); display:flex; flex-wrap:wrap; gap:.75rem;
  justify-content:space-between; }}
@media (prefers-reduced-motion: reduce) {{ *,*::before,*::after {{ animation:none!important; transition:none!important; }} }}
"""


# -- sample listings --------------------------------------------------------
# Clearly-marked placeholders so the layout can be judged. Replaced wholesale
# by the real CSV import -- nothing here is presented as a genuine listing.

SAMPLE_LISTINGS = [
    ("Sea-view condo, high floor", "฿4,500,000", "2", "2", "78", "For sale", "tower"),
    ("Pool villa, walk to the beach", "฿45,000 / month", "3", "3", "210", "For rent", "villa"),
    ("Townhouse in a gated project", "฿3,250,000", "3", "2", "140", "For sale", "town"),
]


def listing_cards(site: PreviewSite) -> str:
    areas = list(site.get("areas") or [])
    out = []
    for i, (title, price, beds, baths, sqm, tag, art) in enumerate(SAMPLE_LISTINGS):
        area = areas[i] if i < len(areas) else ""
        alt = " tag--alt" if tag == "For rent" else ""
        out.append(f"""
        <article class="card">
          <div class="card__art"><svg viewBox="0 0 400 300" role="img" aria-label="Illustration of a property"><use href="#ill"/></svg><span class="tag{alt}">{e(tag)}</span></div>
          <div class="card__body">
            <span class="card__place">{e(area)}</span>
            <h3 class="card__title">{e(title)}</h3>
            <p class="card__price">{e(price)}</p>
            <ul class="card__facts">
              <li><strong>{e(beds)}</strong> bed</li>
              <li><strong>{e(baths)}</strong> bath</li>
              <li><strong>{e(sqm)}</strong> sqm</li>
            </ul>
          </div>
        </article>""")
    return "".join(out)


def points_html(site: PreviewSite) -> str:
    return "".join(
        f"""
        <div class="point">
          <div class="point__rule"></div>
          <h3>{e(p['title'])}</h3>
          <p>{e(p['text'])}</p>
        </div>"""
        for p in site.get("points") or []
    )


def steps_html(site: PreviewSite) -> str:
    return "".join(
        f"""
        <div class="step">
          <div>
            <h3>{e(s['title'])}</h3>
            <p>{e(s['text'])}</p>
          </div>
        </div>"""
        for s in site.get("steps") or []
    )


def chips_html(items: list[str]) -> str:
    return "".join(f'<li><a href="#">{e(i)}</a></li>' for i in items)


def initials(name: str) -> str:
    parts = [w for w in name.split() if w]
    return "".join(w[0] for w in parts[:2]).upper()


# -- archetype bodies -------------------------------------------------------

def body_listings(site: PreviewSite) -> str:
    areas = list(site.get("areas") or [])
    return f"""
  <section class="wrap">
    <form class="searchbar" onsubmit="return false">
      <label class="field"><span>Area</span>
        <select>{''.join(f'<option>{e(a)}</option>' for a in ['Any area'] + areas)}</select></label>
      <label class="field"><span>Type</span>
        <select><option>Any type</option><option>Condo</option><option>House</option>
          <option>Villa</option><option>Townhouse</option><option>Land</option></select></label>
      <label class="field"><span>Bedrooms</span>
        <select><option>Any</option><option>1+</option><option>2+</option><option>3+</option><option>4+</option></select></label>
      <label class="field"><span>Buy or rent</span>
        <select><option>Either</option><option>For sale</option><option>For rent</option></select></label>
      <a class="btn btn--primary" href="#">Search</a>
    </form>
  </section>

  <section class="wrap">
    <span class="eyebrow">Featured</span>
    <h2 class="h2">Recently listed</h2>
    <p class="sub">Sample properties, shown so the layout can be judged. Your own listings replace these when the spreadsheet is imported.</p>
    <div class="grid3">{listing_cards(site)}</div>
  </section>

  <section class="band">
    <div class="wrap">
      <span class="eyebrow">Areas</span>
      <h2 class="h2">Where we cover</h2>
      <p class="sub">Every area gets its own page, so a search engine has a route in for each one.</p>
      <ul class="chips">{chips_html(areas)}</ul>
    </div>
  </section>

  <section class="wrap">
    <span class="eyebrow">Why us</span>
    <h2 class="h2">What you get</h2>
    <div class="points">{points_html(site)}</div>
  </section>
"""


def body_advisory(site: PreviewSite) -> str:
    return f"""
  <section class="band">
    <div class="wrap">
      <span class="eyebrow">The process</span>
      <h2 class="h2">How it works</h2>
      <p class="sub">Four stages, each ending with something written down that you can act on.</p>
      <div class="steps">{steps_html(site)}</div>
    </div>
  </section>

  <section class="wrap">
    <span class="eyebrow">Why us</span>
    <h2 class="h2">What makes the difference</h2>
    <div class="points">{points_html(site)}</div>
  </section>
"""


def body_product(site: PreviewSite) -> str:
    return f"""
  <section class="band">
    <div class="wrap">
      <span class="eyebrow">The mechanics</span>
      <h2 class="h2">How a share works</h2>
      <p class="sub">Fractional ownership is often explained vaguely. Here is the actual structure.</p>
      <div class="steps">{steps_html(site)}</div>
    </div>
  </section>

  <section class="wrap">
    <span class="eyebrow">Example</span>
    <h2 class="h2">What a share looks like</h2>
    <p class="sub">An illustration of the structure, not an offer. Real opportunities carry their own figures.</p>
    <div class="grid3">
      <article class="card"><div class="card__body">
        <span class="card__place">Share size</span><h3 class="card__title">One eighth</h3>
        <p class="card__price">6&ndash;7 weeks a year</p>
        <ul class="card__facts"><li>Rotating calendar</li></ul></div></article>
      <article class="card"><div class="card__body">
        <span class="card__place">Owners</span><h3 class="card__title">Eight maximum</h3>
        <p class="card__price">Fixed at purchase</p>
        <ul class="card__facts"><li>Agreed in advance</li></ul></div></article>
      <article class="card"><div class="card__body">
        <span class="card__place">Exit</span><h3 class="card__title">Transferable</h3>
        <p class="card__price">Sell your share</p>
        <ul class="card__facts"><li>To an owner or openly</li></ul></div></article>
    </div>
  </section>

  <section class="band">
    <div class="wrap">
      <span class="eyebrow">Why us</span>
      <h2 class="h2">What we commit to</h2>
      <div class="points">{points_html(site)}</div>
    </div>
  </section>
"""


BODIES = {"listings": body_listings, "advisory": body_advisory, "product": body_product}


def render(site: PreviewSite) -> str:
    """One complete standalone page."""
    fonts = site.fonts
    families = "&".join(
        f"family={fonts[k].replace(' ', '+')}" for k in ("display", "body")
    )
    art = ILLUSTRATIONS.get(site.get("illustration", "tower"), ILLUSTRATIONS["tower"])
    nav = (
        ["Properties", "Areas", "About", "Contact"]
        if site.archetype == "listings"
        else ["Services", "How it works", "About", "Contact"]
    )

    return f"""<title>{e(site.name)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{families}&display=swap">
<style>{css(site)}</style>

<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <linearGradient id="g-sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="var(--c-sky1)"/><stop offset="100%" stop-color="var(--c-sky2)"/>
  </linearGradient>
  <symbol id="ill" viewBox="0 0 400 300">{art}</symbol>
</defs></svg>

<p class="draft">Design preview &middot; {e(site.domain)} &middot; not yet published</p>

<header class="bar">
  <div class="bar__in">
    <span class="brand"><span class="brand__mark">{e(initials(site.name))}</span>{e(site.name)}</span>
    <nav class="nav">{''.join(f'<a href="#">{e(n)}</a>' for n in nav)}</nav>
  </div>
</header>

<main>
  <div class="wrap">
    <div class="hero">
      <div>
        <span class="eyebrow">{e(site.tagline)}</span>
        <h1>{e(site.hero_title)}</h1>
        <p>{e(site.hero_text)}</p>
        <div class="actions">
          <a class="btn btn--primary" href="#">{e(site.cta)}</a>
          <a class="btn btn--ghost" href="#">{e(site.cta_secondary)}</a>
        </div>
      </div>
      <div class="hero__art">
        <svg viewBox="0 0 400 300" role="img" aria-label="Illustration representing {e(site.name)}"><use href="#ill"/></svg>
      </div>
    </div>
  </div>

{BODIES[site.archetype](site)}

  <section class="wrap">
    <div class="cta">
      <div>
        <h2>{e(site.cta)}</h2>
        <p>Tell us what you are trying to do and we will say what is involved, before any fee.</p>
      </div>
      <a class="btn" href="#">{e(site.cta_secondary)}</a>
    </div>
  </section>
</main>

<footer>
  <div class="foot">
    <div>
      <span class="brand"><span class="brand__mark">{e(initials(site.name))}</span>{e(site.name)}</span>
      <p style="color:var(--muted);font-size:.9rem;margin:.6rem 0 0">{e(site.tagline)}</p>
    </div>
    <div><h4>{'Properties' if site.archetype == 'listings' else 'Services'}</h4>
      <ul>{''.join(f'<li><a href="#">{e(n)}</a></li>' for n in nav)}</ul></div>
    <div><h4>Company</h4>
      <ul><li><a href="#">About</a></li><li><a href="#">Contact</a></li>
        <li><a href="#">Privacy</a></li><li><a href="#">Terms</a></li></ul></div>
    <div><h4>Contact</h4>
      <ul><li>Pattaya, Chonburi</li><li>Thailand</li></ul></div>
  </div>
  <div class="foot__base"><div>
    <span>&copy; 2026 {e(site.name)}</span>
    <span>Design preview &mdash; placeholder copy, no live data</span>
  </div></div>
</footer>
"""


def build_all(out_dir: Path | None = None) -> list[Path]:
    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for site in load_spec():
        path = out_dir / f"{site.domain.replace('.', '-')}.html"
        path.write_text(render(site), encoding="utf-8")
        written.append(path)
    return written
