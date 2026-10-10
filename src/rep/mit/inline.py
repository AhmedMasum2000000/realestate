"""The small slice of Markdown that page copy needs, and nothing more.

Content lives in YAML as plain strings. Only two inline forms are
recognised: **bold** and [text](url) links. Everything else is escaped, so a
stray < in copy can never become markup.
"""

from __future__ import annotations

import re

from markupsafe import Markup, escape

_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")


def inline(text: str | None) -> Markup:
    if not text:
        return Markup("")
    out = str(escape(text))

    def link(m: re.Match) -> str:
        label, href = m.group(1), m.group(2)
        external = href.startswith("http") and "moveinthailand.com" not in href
        attrs = ' rel="noopener" target="_blank"' if external else ""
        return f'<a href="{href}"{attrs}>{label}</a>'

    out = _LINK.sub(link, out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    return Markup(out)


def plain(text: str | None) -> str:
    """Copy with the markup forms stripped, for meta tags and JSON-LD."""
    if not text:
        return ""
    return _BOLD.sub(r"\1", _LINK.sub(r"\1", text))
