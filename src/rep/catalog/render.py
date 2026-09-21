"""Jinja environment and page writers.

Every page is written as `<path>/index.html` so URLs carry a trailing slash and
static hosts serve them without extensionless-URL rewriting.
"""

from __future__ import annotations

import json
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


def make_env(templates: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates)),
        autoescape=True,
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
        "og_image": f"{SITE_URL}/assets/og-default.jpg",
        "jsonld": "",
        "page_indexable": True,
    }


def write(out: Path, path: str, html: str) -> None:
    """`path` is a URL path; '/for-sale/' becomes 'for-sale/index.html'."""
    target = out / path.strip("/") / "index.html" if path != "/" else out / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


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
