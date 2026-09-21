"""Site build.

Reads the committed `data/catalog.json` (plus `data/enrichment.json` when it
exists) and writes a complete static site. No network, no CSV — so CI can
reproduce the output exactly.
"""

from __future__ import annotations

import json
import shutil
from html import escape
from datetime import date
from pathlib import Path

from . import content
from .aggregate import percentile, sort_for_display, summarize
from .hubs import area_siblings, build_hubs
from .links import build_related_index
from .loader import read_catalog
from .model import Listing, format_price
from .render import (
    PAGE_SIZE,
    SITE_URL,
    base_context,
    breadcrumb_ld,
    jsonld,
    listing_ld,
    make_env,
    organization_ld,
    paginate,
    write,
)

GALLERY_LIMIT = 10
FORM_ACTION = "https://formspree.io/f/placeholder"


def merge_enrichment(listings: list[Listing], path: Path) -> int:
    """Fold scraped photos and copy into the catalog.

    Enrichment is additive and optional: a missing or partial file just means
    fewer listings carry photos, never a failed build.
    """
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    by_ref = {l.reference: l for l in listings}
    applied = 0
    for ref, payload in data.get("listings", {}).items():
        listing = by_ref.get(ref)
        if not listing:
            continue
        images = payload.get("images") or []
        if images:
            listing.images = images
            # Prefer the copy on our own origin; fall back to the remote URL
            # only if the download did not land.
            listing.hero_image = (
                payload.get("hero_local") or payload.get("hero") or images[0]
            )
            applied += 1
    return applied


def comparison_note(listing: Listing, pool: list[Listing]) -> str:
    """Price context against a genuine cohort, or nothing.

    Only quoted when there are enough comparable listings to make a median
    meaningful — an invented benchmark is worse than no benchmark.
    """
    cohort = [
        l for l in pool
        if l.deal == listing.deal
        and l.type_slug == listing.type_slug
        and l.location_slug == listing.location_slug
        and l.price_thb > 0
        and l.reference != listing.reference
    ]
    if len(cohort) < 5 or listing.price_thb <= 0:
        return ""

    prices = [l.price_thb for l in cohort]
    median = percentile(prices, 50)
    noun = "rents" if listing.deal == "rent" else "asking prices"
    where = listing.location or "Pattaya"
    plural = listing.type_label_plural.lower()

    delta = round(100 * (listing.price_thb - median) / median)
    head = (
        f"Across the {len(cohort)} other {plural} we hold {'to rent' if listing.deal == 'rent' else 'for sale'} "
        f"in {where}, median {noun} sit at {format_price(median, listing.deal)}."
    )
    if delta <= -8:
        tail = f" This one is around {abs(delta)}% below that — worth asking why before you assume it's a bargain."
    elif delta >= 8:
        tail = f" This one sits about {delta}% above, so it should be showing you something the others don't."
    else:
        tail = " This one is priced in line with the area."
    return head + tail


def build(root: Path, out: Path, base: str = "", preview: bool = False) -> dict:
    templates = root / "templates" / "phpro"
    env = make_env(templates)
    today = date.today()

    listings = read_catalog(root / "data" / "catalog.json")
    enriched = merge_enrichment(listings, root / "data" / "enrichment.json")

    hubs = build_hubs(listings)
    related_index = build_related_index(listings)
    by_ref = {l.reference: l for l in listings}

    area_hubs = sorted(
        (h for h in hubs if h.kind == "area"),
        key=lambda h: (-h.count, h.h1),
    )
    areas = [
        {"name": h.listings[0].location, "slug": h.listings[0].location_slug, "count": h.count}
        for h in area_hubs
    ]

    ctx = base_context(areas, today.year)
    project_paths = {h.listings[0].project_slug for h in hubs if h.kind == "project"}

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # ---- assets ----
    (out / "assets").mkdir(parents=True, exist_ok=True)
    css = env.get_template("site.css.j2").render(palette=ctx["palette"], fonts=ctx["fonts"])
    (out / "assets" / "site.css").write_text(css, encoding="utf-8")
    js = env.get_template("site.js.j2").render()
    (out / "assets" / "site.js").write_text(js, encoding="utf-8")

    brand = root / "assets" / "brand"
    if brand.is_dir():
        shutil.copytree(brand, out / "assets" / "brand", dirs_exist_ok=True)

    photos = root / "assets" / "properties"
    hero_image = ""
    band_image = ""
    if photos.is_dir():
        shutil.copytree(photos, out / "assets" / "properties", dirs_exist_ok=True)
        first = sorted(p for p in photos.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
        if first:
            hero_image = f"/assets/properties/{first[0].name}"
        if len(first) > 2:
            band_image = f"/assets/properties/{first[2].name}"

    (out / ".nojekyll").write_text("", encoding="utf-8")
    # A CNAME claims the custom domain. A preview build must not, or Pages
    # serves it at a domain whose DNS does not point here yet.
    if not preview:
        (out / "CNAME").write_text("pattayahomepro.com\n", encoding="utf-8")

    pages: list[tuple[str, bool]] = []

    # ---- home ----
    featured = sort_for_display([l for l in listings if l.deal == "sale"])[:6]
    deals = {d: sum(1 for l in listings if l.deal == d) for d in ("sale", "rent", "business")}
    home_html = env.get_template("home.html.j2").render(**{
        **ctx,
        "page_title": "Pattaya Home Pro — Property for Sale & Rent in Pattaya, Thailand",
        "page_description": (
            f"{len(listings)} condos, houses, pool villas and businesses for sale and rent "
            "across Pattaya and the Eastern Seaboard. Straight answers on price, title and quota."
        ),
        "page_path": "/",
        "jsonld": jsonld(organization_ld()),
        "hero": content.HERO,
        "hero_image": hero_image,
        "band_image": band_image,
        "positioning": content.POSITIONING,
        "segments": content.SEGMENTS,
        "rules": content.RULES,
        "rules_intro": content.RULES_INTRO,
        "off_market": content.OFF_MARKET,
        "deals_intro": content.DEALS_INTRO,
        "contact": content.CONTACT,
        "trust": content.TRUST_STRIP,
        "interests": content.INTERESTS,
        "property_interests": content.PROPERTY_INTERESTS,
        "form_action": FORM_ACTION,
        "featured": featured,
        "areas": areas,
        "total": len(listings),
        "area_count": len(areas),
        "sale_count": deals["sale"],
        "rent_count": deals["rent"],
    })
    write(out, "/", home_html, base)
    pages.append(("/", True))

    # ---- hubs ----
    hub_tpl = env.get_template("hub.html.j2")
    hub_index = {h.path: h for h in hubs}
    for hub in sorted(hubs, key=lambda h: h.path):
        ordered = sort_for_display(hub.listings)
        summary = summarize(hub.listings, today)
        chunks = paginate(ordered, PAGE_SIZE)
        adjacent: list[tuple[str, str, int]] = []
        if hub.kind == "area":
            adjacent = area_siblings(hubs, content.AREA_ADJACENCY, hub.listings[0].location_slug)

        sibling_title = {
            "all": "Browse by status",
            "deal": "Browse by property type",
            "deal-type": "Browse by area",
            "deal-type-area": "Other areas",
            "area": "",
            "project": "",
        }.get(hub.kind, "More")

        related_hubs: list[tuple[str, str, int]] = []
        if hub.kind == "area":
            slug = hub.listings[0].location_slug
            for deal_seg in ("for-sale", "for-rent"):
                for tslug in ("condos", "houses", "pool-villas"):
                    candidate = hub_index.get(f"/{deal_seg}/{tslug}/{slug}/")
                    if candidate:
                        related_hubs.append((candidate.h1, candidate.path, candidate.count))
        elif hub.kind == "deal-type-area":
            # Same search, one area over — plus a way back up to the area itself.
            slug = hub.listings[0].location_slug
            prefix = hub.path.rsplit("/", 2)[0] + "/"
            for neighbour in content.AREA_ADJACENCY.get(slug, []):
                candidate = hub_index.get(f"{prefix}{neighbour}/")
                if candidate:
                    adjacent.append((candidate.listings[0].location, candidate.path, candidate.count))
            area_hub = hub_index.get(f"/areas/{slug}/")
            if area_hub:
                related_hubs.append((area_hub.h1, area_hub.path, area_hub.count))

        for index, chunk in enumerate(chunks, start=1):
            path = hub.path if index == 1 else f"{hub.path}page/{index}/"
            indexable = index == 1 and hub.count >= 5
            html = hub_tpl.render(**{
                **ctx,
                "nav_current": hub.nav_current,
                "page_title": hub.title if index == 1 else f"{hub.h1} — Page {index} | Pattaya Home Pro",
                "page_description": hub.description,
                "page_path": path,
                "page_indexable": indexable,
                "jsonld": jsonld(breadcrumb_ld(hub.crumbs, hub.h1, hub.path)) if index == 1 else "",
                "hub": hub,
                "summary": summary,
                "page_listings": chunk,
                "page": index,
                "pages": len(chunks),
                "kicker": f"{hub.count} listings",
                "sibling_title": sibling_title,
                "adjacent": adjacent,
                "related_hubs": related_hubs,
            })
            write(out, path, html, base)
            pages.append((path, indexable))

    # ---- listings ----
    listing_tpl = env.get_template("listing.html.j2")
    for l in sorted(listings, key=lambda x: x.reference):
        crumbs = [("Home", "/"), ("Properties", "/properties/")]
        if l.location:
            crumbs.append((l.location, f"/areas/{l.location_slug}/"))
        html = listing_tpl.render(**{
            **ctx,
            "nav_current": "properties",
            "body_attrs": f'data-listing="{escape(l.title[:70])}"',
            "page_title": f"{l.title} — {l.price_display} | Ref {l.reference}",
            "page_description": l.meta_description,
            "page_path": l.url,
            "page_indexable": l.indexable,
            "og_type": "article",
            "og_image": (l.hero_image if l.hero_image.startswith("http")
                         else SITE_URL + l.hero_image) if l.hero_image else ctx["og_image"],
            "jsonld": jsonld(listing_ld(l)),
            "l": l,
            "crumbs": crumbs,
            "gallery": l.images[1:GALLERY_LIMIT] if len(l.images) > 1 else [],
            "related": [by_ref[r] for r in related_index.get(l.reference, []) if r in by_ref],
            "context_note": comparison_note(l, listings),
            "area_note": content.AREA_COPY.get(l.location_slug, ""),
            "project_url": f"/projects/{l.project_slug}/" if l.project_slug in project_paths else "",
            # The export's `project` frequently restates the title verbatim;
            # showing it then adds a row that tells the reader nothing.
            "show_project": bool(l.project) and l.project.lower() not in l.title.lower(),
        })
        write(out, l.url, html, base)
        pages.append((l.url, l.indexable))

    # ---- core pages ----
    page_tpl = env.get_template("page.html.j2")
    core = [
        {
            "path": "/services/", "nav": "services", "kicker": "What we do",
            "h1": "Services",
            "title": "Services — Sales, Rentals, Business Sales & Valuation | Pattaya Home Pro",
            "description": "Property sales, long-stay rentals, business sales, valuation, rental "
                           "management and buyer representation across Pattaya and the Eastern Seaboard.",
            "intro": [
                "We are a full-service brokerage, which in Pattaya mostly means we do the parts "
                "other agents hand back to you: title checks, quota confirmation, fee negotiation "
                "and the awkward conversation with the juristic person.",
                "Everything below is done in-house. If something falls outside what we are good at, "
                "we will say so and point you at whoever is.",
            ],
            "blocks": content.SERVICES,
            "form": True,
        },
        {
            "path": "/meet-the-team/", "nav": "", "kicker": "Who you'll be dealing with",
            "h1": "Meet the team",
            "title": "Meet the Team | Pattaya Home Pro",
            "description": "The people behind Pattaya Home Pro — a working Pattaya brokerage "
                           "covering sales, rentals and business sales across the Eastern Seaboard.",
            "intro": [
                "Pattaya Home Pro is a small brokerage by design. You will deal with the same "
                "person from the first call to the transfer office, and that person will have "
                "actually stood in the property.",
                "We are based in Nongprue, Banglamung, and we cover everything from Naklua down "
                "to Bang Saray and east to Mabprachan.",
                "The fastest way to find out whether we are useful to you is to call and ask "
                "something specific. We do not run a call centre.",
            ],
            "blocks": [],
            "form": True,
        },
        {
            "path": "/done-deals/", "nav": "", "kicker": "Track record",
            "h1": "Done deals",
            "title": "Done Deals — Recent Sales & Lettings | Pattaya Home Pro",
            "description": "A sample of recent transactions across Pattaya — condos, houses, "
                           "pool villas and businesses, sold and let.",
            "intro": [
                "Client matters stay client matters, so this is a sample rather than a ledger. "
                "What it should tell you is the range: we are as comfortable with a ฿1.5M studio "
                "as with a beachfront villa, and we handle business sales that never reach a portal.",
                "If you want references for a specific type of deal, ask on the phone and we will "
                "put you in touch with someone who did one.",
            ],
            "blocks": [],
            "form": False,
            "cards": True,
        },
        {
            "path": "/get-in-touch/", "nav": "contact", "kicker": content.CONTACT["kicker"],
            "h1": "Get in touch",
            "title": "Get in Touch — Pattaya Home Pro | +66 95 348 3725",
            "description": "Call +66 95 348 3725 or send an enquiry. Pattaya Home Pro, "
                           "21/78 Moo.5 Nongprue, Banglamung, Chonburi 20180.",
            "intro": [
                "The phone is the fast route. We answer it, and if we cannot help we will "
                "tell you quickly rather than take a viewing you do not need.",
                "If you would rather write, the form works too — tell us the area, the budget "
                "and roughly when you want to move, and the reply will be specific instead of a brochure.",
            ],
            "blocks": [],
            "form": True,
        },
    ]

    deal_cards = sort_for_display(listings)[:6]
    for page in core:
        html = page_tpl.render(**{
            **ctx,
            "nav_current": page["nav"],
            "page_title": page["title"],
            "page_description": page["description"],
            "page_path": page["path"],
            "jsonld": jsonld(breadcrumb_ld([("Home", "/")], page["h1"], page["path"])),
            "kicker": page["kicker"],
            "page_h1": page["h1"],
            "intro": page["intro"],
            "blocks": page["blocks"],
            "cards": deal_cards if page.get("cards") else [],
            "cards_kicker": "On our books now",
            "cards_heading": "A sample of current stock",
            "show_form": page["form"],
            "contact": content.CONTACT,
            "interests": content.INTERESTS,
            "property_interests": content.PROPERTY_INTERESTS,
            "form_action": FORM_ACTION,
        })
        write(out, page["path"], html, base)
        pages.append((page["path"], True))

    return {
        "pages": pages,
        "listings": len(listings),
        "hubs": len(hubs),
        "enriched": enriched,
        "indexable": sum(1 for _, ok in pages if ok),
    }
