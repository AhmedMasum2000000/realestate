"""Build moveinthailand.com from content/mit/*.yml.

Every page is a YAML record: who it is for, the answer, the sections that
carry it, an FAQ, its sources and the next step in the reader's journey.
Templates own the layout; content owns the words. A page that links to a
path the site does not have, or an old URL left without a destination, fails
the build rather than shipping a dead end.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import yaml

from ..catalog.build import merge_enrichment
from ..catalog.legacy import htaccess
from ..catalog.loader import read_catalog
from ..catalog.render import jsonld, make_env, write
from .inline import inline, plain

SITE_URL = "https://moveinthailand.com"
PARTNER_URL = "https://pattayahomepro.com"
TEMPLATES = ("templates", "mit")
CONTENT = ("content", "mit")


class ContentError(Exception):
    pass


PAGE_DEFAULTS = {
    "template": "guide", "sections": list, "faq": list, "sources": list, "related": list,
    "groups": list, "facts": list, "kicker": "", "lead": "", "verified": "", "for": "",
    "short": "", "card": "", "ask": "", "next": "", "noindex": False, "show_homes": False,
    "tool": "",
}
SECTION_KEYS = ("h2", "toc", "p", "list", "steps", "table", "after", "note", "warn")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", plain(text).lower()).strip("-")[:60]


def parent_of(path: str) -> str:
    parts = path.strip("/").split("/")
    return "/" if len(parts) <= 1 else "/" + "/".join(parts[:-1]) + "/"


# -- content ----------------------------------------------------------------

def load(root: Path) -> tuple[dict, list[dict]]:
    base = root.joinpath(*CONTENT)
    site = yaml.safe_load((base / "site.yml").read_text(encoding="utf-8"))
    pages: list[dict] = []
    for f in sorted(base.glob("*.yml")):
        if f.name == "site.yml":
            continue
        for page in (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("pages", []):
            # Templates run under StrictUndefined so a misspelt key fails the
            # build; every optional key therefore gets an explicit empty value.
            for key, empty in PAGE_DEFAULTS.items():
                page.setdefault(key, empty() if callable(empty) else empty)
            for s in page["sections"]:
                for key in SECTION_KEYS:
                    s.setdefault(key, None)
            for g in page["groups"]:
                g.setdefault("intro", "")
            page["_file"] = f.name
            pages.append(page)
    return site, pages


def validate(site: dict, pages: list[dict], legacy: list[str]) -> list[str]:
    problems = []
    paths = [p["path"] for p in pages]
    dupes = {x for x in paths if paths.count(x) > 1}
    if dupes:
        problems.append(f"duplicate paths: {sorted(dupes)}")
    known = set(paths)
    for p in pages:
        where = f"{p['_file']}:{p.get('path')}"
        for key in ("path", "title", "description", "h1"):
            if not p.get(key):
                problems.append(f"{where}: missing {key}")
        if not p["path"].startswith("/") or not p["path"].endswith("/"):
            problems.append(f"{where}: path must start and end with /")
        d = plain(p.get("description", ""))
        if not 70 <= len(d) <= 170:
            problems.append(f"{where}: description is {len(d)} chars (70-170)")
        for ref in list(p["related"]) + [p.get("next")] + [x for g in p.get("groups", []) for x in g.get("items", [])]:
            if ref and ref.startswith("/") and ref not in known:
                problems.append(f"{where}: links to missing page {ref}")
        for text in _all_text(p):
            for href in re.findall(r"\]\((/[^)\s]*)\)", text):
                if href.split("#")[0] not in known:
                    problems.append(f"{where}: inline link to missing page {href}")
    for old in legacy:
        if old not in known and old not in site.get("redirects", {}):
            problems.append(f"old URL {old} has no page and no redirect")
    for old, new in site.get("redirects", {}).items():
        if new.split("#")[0] not in known:
            problems.append(f"redirect {old} -> {new}: target missing")
    return problems


def _all_text(page: dict):
    yield page.get("lead", "")
    for s in page["sections"]:
        yield from s.get("p") or []
        yield from s.get("list") or []
        yield from s.get("steps") or []
        yield from s.get("after") or []
        yield s.get("note") or ""
        yield s.get("warn") or ""
        for row in (s.get("table") or {}).get("rows", []):
            yield from row
    for qa in page["faq"]:
        yield qa.get("a", "")


# -- listings from the partner site -------------------------------------------

def featured_homes(root: Path, limit: int = 6) -> list[dict]:
    path = root / "data" / "catalog.json"
    if not path.exists():
        return []
    listings = read_catalog(path)
    merge_enrichment(listings, root / "data" / "enrichment.json")
    with_photos = [l for l in listings if l.hero_image and l.deal in ("sale", "rent")]
    with_photos.sort(key=lambda l: (l.last_update or ""), reverse=True)
    picked, seen_deal = [], {"sale": 0, "rent": 0}
    for l in with_photos:
        if seen_deal[l.deal] >= limit // 2:
            continue
        seen_deal[l.deal] += 1
        img = l.hero_image if l.hero_image.startswith("http") else PARTNER_URL + l.hero_image
        picked.append({
            "title": l.title, "url": PARTNER_URL + l.url, "image": img,
            "price": l.price_display, "where": l.location or "Pattaya",
            "deal": "For rent" if l.deal == "rent" else "For sale",
            "beds": l.bedrooms,
        })
        if len(picked) >= limit:
            break
    return picked


# -- structured data ----------------------------------------------------------

def page_ld(site: dict, page: dict, crumbs: list[tuple[str, str]]) -> list[dict]:
    url = SITE_URL + page["path"]
    graph: list[dict] = [{
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE_URL + href}
            for i, (name, href) in enumerate(crumbs + [(page["h1"], page["path"])])
        ],
    }]
    if page["template"] in ("guide", "hub"):
        art = {
            "@type": "Article",
            "headline": plain(page["h1"])[:110],
            "description": plain(page["description"]),
            "url": url,
            "mainEntityOfPage": url,
            "author": {"@type": "Organization", "name": site["brand"]["name"], "url": SITE_URL + "/"},
            "publisher": {"@type": "Organization", "name": site["brand"]["name"], "url": SITE_URL + "/"},
        }
        if page.get("verified"):
            art["dateModified"] = str(page["verified"])
        graph.append(art)
    if page["faq"]:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": plain(q["q"]),
                 "acceptedAnswer": {"@type": "Answer", "text": plain(q["a"])}}
                for q in page["faq"]
            ],
        })
    return graph


def org_ld(site: dict) -> dict:
    b = site["brand"]
    return {
        "@type": "ProfessionalService",
        "name": b["name"],
        "url": SITE_URL + "/",
        "telephone": b["phone_display"],
        "areaServed": "TH",
        "description": b["tagline"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": b["address_street"],
            "addressLocality": b["address_locality"],
            "addressRegion": b["address_region"],
            "postalCode": b["address_postal"],
            "addressCountry": "TH",
        },
    }


# -- build --------------------------------------------------------------------

def build(root: Path, out: Path, preview: bool = False, base: str = "") -> dict:
    site, pages = load(root)
    legacy_file = root / "data" / "research" / "moveinthailand.json"
    legacy = []
    if legacy_file.exists():
        crawl = json.loads(legacy_file.read_text(encoding="utf-8"))
        legacy = sorted({(p["path"].rstrip("/") + "/") if p["path"] != "/" else "/" for p in crawl["pages"]}
                        | {r["from"].split(".com", 1)[-1] for r in crawl.get("redirects", [])})
    problems = validate(site, pages, legacy)
    if problems:
        raise ContentError("\n".join(problems))

    by_path = {p["path"]: p for p in pages}
    for p in pages:
        p["_parent"] = parent_of(p["path"]) if p["path"] != "/" else None
        p["_children"] = [c for c in pages if c is not p and parent_of(c["path"]) == p["path"] and c["path"] != "/"]
        for s in p["sections"]:
            s["_id"] = slug(s.get("h2", ""))

    env = make_env(root.joinpath(*TEMPLATES))
    env.filters["md"] = inline
    env.filters["plain"] = plain
    homes = featured_homes(root)
    today = date.today()

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    common = {
        "site": site, "brand": site["brand"], "palette": site["palette"], "fonts": site["fonts"],
        "site_url": SITE_URL, "partner_url": PARTNER_URL, "year": today.year,
        "menu": site["menu"], "pages": by_path, "homes": homes, "preview": preview,
        "gsc_meta": site.get("gsc_meta", ""),
    }

    for p in pages:
        crumbs = []
        cur = p["_parent"]
        while cur and cur in by_path:
            crumbs.insert(0, (by_path[cur].get("short") or plain(by_path[cur]["h1"]), cur))
            cur = by_path[cur]["_parent"]
        if p["path"] != "/" and (not crumbs or crumbs[0][1] != "/"):
            crumbs.insert(0, ("Home", "/"))
        nxt = by_path.get(p.get("next")) if p.get("next") else None
        related = [by_path[r] for r in p["related"]]
        graph = page_ld(site, p, crumbs if p["path"] != "/" else [])
        if p["path"] == "/":
            graph = [org_ld(site), {"@type": "WebSite", "name": site["brand"]["name"], "url": SITE_URL + "/"}]
        ctx = common | {
            "page": p, "crumbs": crumbs, "next": nxt, "related": related,
            "page_title": p["title"], "page_description": plain(p["description"]),
            "page_path": p["path"], "nav_current": p["path"].strip("/").split("/")[0],
            "jsonld": jsonld({"@context": "https://schema.org", "@graph": graph}),
            "body_class": "page--hero" if p["template"] == "home" else "",
        }
        html = env.get_template(f"{p['template']}.html.j2").render(**ctx)
        write(out, p["path"], html, base)

    (out / "404.html").write_text(env.get_template("404.html.j2").render(
        **common, page={"path": "/404/", "noindex": True}, crumbs=[], page_title=f"Page not found | {site['brand']['name']}",
        page_description="This page has moved. Start from the visa finder or the step-by-step moving guide.",
        page_path="/404/", nav_current="", jsonld="", body_class=""), encoding="utf-8")

    assets = out / "assets"
    (assets / "brand").mkdir(parents=True)
    (assets / "site.css").write_text(env.get_template("site.css.j2").render(**common), encoding="utf-8")
    (assets / "site.js").write_text(env.get_template("site.js.j2").render(**common), encoding="utf-8")
    fonts_src = root / "assets" / "brand" / "fonts"
    if fonts_src.exists():
        shutil.copytree(fonts_src, assets / "brand" / "fonts")
    fonts_css = root / "assets" / "brand" / "fonts.css"
    if fonts_css.exists():
        shutil.copy(fonts_css, assets / "brand" / "fonts.css")
    mit_assets = root / "assets" / "mit"
    if mit_assets.exists():
        for f in mit_assets.iterdir():
            shutil.copy(f, assets / "brand" / f.name)
    hero = site.get("hero_image")
    if hero and (root / hero).exists():
        shutil.copy(root / hero, assets / "brand" / Path(hero).name)

    # sitemap + robots
    stamp = today.isoformat()
    urls = "\n".join(
        f"  <url><loc>{xml_escape(SITE_URL + p['path'])}</loc><lastmod>{p.get('verified', stamp)}</lastmod></url>"
        for p in sorted(pages, key=lambda x: x["path"]) if not p.get("noindex")
    )
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n", encoding="utf-8")
    robots = ("User-agent: *\nDisallow: /\n" if preview
              else f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    (out / "robots.txt").write_text(robots, encoding="utf-8")

    redirects = dict(site.get("redirects", {}))
    (out / ".htaccess").write_text(htaccess(redirects), encoding="utf-8")
    (out / "_redirects").write_text("".join(f"{a} {b} 301\n" for a, b in sorted(redirects.items())),
                                    encoding="utf-8")
    return {"pages": len(pages), "redirects": len(redirects), "homes": len(homes), "legacy": len(legacy)}
