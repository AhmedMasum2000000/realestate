"""Jinja environment and page writers.

Every page is written as `<path>/index.html` so URLs carry a trailing slash and
static hosts serve them without extensionless-URL rewriting.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from . import content
from .art import placeholder
from .model import Listing
from .tokens import BRAND, FONTS, PALETTE

PAGE_SIZE = 24
SITE_URL = "https://pattayahomepro.com"

# Areas shown in the footer: the ones with enough inventory to be worth a click.
FOOTER_AREA_LIMIT = 6

# (label, href, nav key) for the full-screen menu.
MENU_ITEMS = [
    ("Home", "/", "home"),
    ("All properties", "/properties/", "properties"),
    ("For sale", "/for-sale/", "for-sale"),
    ("For rent", "/for-rent/", "for-rent"),
    ("Businesses", "/businesses-for-sale/", "business"),
    ("Services", "/services/", "services"),
    ("Meet the team", "/meet-the-team/", "team"),
    ("Done deals", "/done-deals/", "deals"),
    ("Get in touch", "/get-in-touch/", "contact"),
]


def _autoescape(name: str | None) -> bool:
    """HTML templates only.

    Escaping CSS mangles anything with a quote in it — a font stack like
    `'Archivo', sans-serif` becomes `&#39;Archivo&#39;` and the whole
    declaration is discarded by the parser, silently falling back to a serif.
    """
    return bool(name) and name.endswith((".html.j2", ".xml.j2"))


def make_env(templates: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates)),
        autoescape=_autoescape,
        undefined=StrictUndefined,
        trim_blocks=False,
        lstrip_blocks=False,
        keep_trailing_newline=True,
    )
    env.globals["art"] = placeholder
    return env


def base_context(areas: list[dict], build_year: int) -> dict:
    return {
        "brand": BRAND,
        "palette": PALETTE,
        "fonts": FONTS,
        "site_url": SITE_URL,
        "year": build_year,
        "footer_areas": areas[:FOOTER_AREA_LIMIT],
        "nav_current": "",
        "og_image": f"{SITE_URL}/assets/brand/og-default.jpg",
        "menu_items": MENU_ITEMS,
        "body_attrs": "",
        "jsonld": "",
        "page_indexable": True,
    }


_ROOT_REF = re.compile(r'(href|src)="/(?!/)')


def rebase(html: str, base: str) -> str:
    """Prefix root-relative links so the site works under a sub-path.

    GitHub project Pages serve at `/<repo>/`, where every `href="/…"` would
    otherwise resolve against the domain root. Canonical and og:url tags are
    left alone: they are absolute with a scheme and still name the real
    production URL, which is what keeps a preview from competing in search.
    """
    if not base:
        return html
    return _ROOT_REF.sub(rf'\1="{base}/', html)


def write(out: Path, path: str, html: str, base: str = "") -> None:
    """`path` is a URL path; '/for-sale/' becomes 'for-sale/index.html'."""
    target = out / path.strip("/") / "index.html" if path != "/" else out / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rebase(html, base), encoding="utf-8")


def paginate(items: list, size: int = PAGE_SIZE) -> list[list]:
    if not items:
        return [[]]
    return [items[i:i + size] for i in range(0, len(items), size)]


def jsonld(payload: dict) -> str:
    # separators + sort_keys keep the serialized block byte-stable between builds.
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def breadcrumb_ld(trail: list[tuple[str, str]], current: str, current_path: str) -> dict:
    items = [
        {
            "@type": "ListItem",
            "position": i + 1,
            "name": label,
            "item": f"{SITE_URL}{href}",
        }
        for i, (label, href) in enumerate(trail)
    ]
    items.append({
        "@type": "ListItem",
        "position": len(items) + 1,
        "name": current,
        "item": f"{SITE_URL}{current_path}",
    })
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def organization_ld() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "name": BRAND["name"],
        "url": SITE_URL + "/",
        "telephone": BRAND["phone_display"],
        "email": BRAND["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": BRAND["address_street"],
            "addressLocality": BRAND["address_locality"],
            "addressRegion": BRAND["address_region"],
            "postalCode": BRAND["address_postal"],
            "addressCountry": BRAND["address_country"],
        },
        "areaServed": [{"@type": "Place", "name": a} for a in sorted(content.AREA_COPY)],
    }


def listing_ld(l: Listing) -> dict:
    offer_type = "https://schema.org/BusinessFunction/LeaseOut" if l.deal == "rent" else "https://schema.org/Sell"
    payload = {
        "@context": "https://schema.org",
        "@type": "RealEstateListing",
        "name": l.title,
        "url": f"{SITE_URL}{l.url}",
        "identifier": l.reference,
        "description": l.meta_description,
        "datePosted": l.last_update,
        "offers": {
            "@type": "Offer",
            "price": l.price_thb,
            "priceCurrency": "THB",
            "businessFunction": offer_type,
            "availability": "https://schema.org/InStock",
        },
    }
    if l.location:
        payload["address"] = {
            "@type": "PostalAddress",
            "addressLocality": l.location,
            "addressRegion": "Chonburi",
            "addressCountry": "TH",
        }
    if l.hero_image:
        payload["image"] = l.hero_image if l.hero_image.startswith("http") else SITE_URL + l.hero_image
    if l.bedrooms is not None:
        payload["numberOfBedrooms"] = l.bedrooms
    if l.bathrooms:
        payload["numberOfBathroomsTotal"] = l.bathrooms
    return payload
