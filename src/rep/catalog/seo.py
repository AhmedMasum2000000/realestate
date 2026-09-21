"""Sitemaps and robots.txt.

Only indexable pages enter the sitemap. Submitting a URL that carries a
`noindex` tag is a contradictory signal, and at this volume it is the kind of
thing that gets a whole domain reassessed.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from .render import SITE_URL

URLS_PER_SHARD = 2000


def _urlset(paths: list[str], today: str) -> str:
    rows = "\n".join(
        f"  <url><loc>{escape(SITE_URL + p)}</loc><lastmod>{today}</lastmod></url>"
        for p in paths
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{rows}\n</urlset>\n"
    )


def write_sitemaps(out: Path, pages: list[tuple[str, bool]], today: date | None = None) -> int:
    stamp = (today or date.today()).isoformat()
    indexable = sorted({path for path, ok in pages if ok})

    shards = [
        indexable[i:i + URLS_PER_SHARD]
        for i in range(0, len(indexable), URLS_PER_SHARD)
    ] or [[]]

    names = []
    for i, shard in enumerate(shards, start=1):
        name = f"sitemap-{i}.xml"
        (out / name).write_text(_urlset(shard, stamp), encoding="utf-8")
        names.append(name)

    body = "\n".join(
        f"  <sitemap><loc>{SITE_URL}/{n}</loc><lastmod>{stamp}</lastmod></sitemap>"
        for n in names
    )
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</sitemapindex>\n",
        encoding="utf-8",
    )
    return len(indexable)


def write_robots(out: Path, preview: bool = False) -> None:
    if preview:
        # A preview deployment is a duplicate of the production site. Letting it
        # be crawled would put the two in competition for the same queries.
        (out / "robots.txt").write_text(
            "User-agent: *\nDisallow: /\n", encoding="utf-8"
        )
        return
    (out / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        f"\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )
