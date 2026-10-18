"""CSV -> deduped, normalized catalog.

The raw export is gitignored (`data/*.csv`), so the committed artifact is the
normalized snapshot this module writes. Every later stage reads that JSON, which
keeps the build reproducible in CI without the source file or network access.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .model import (
    DEAL_FROM_STATUS,
    TYPE_SLUGS,
    Listing,
    build_slug,
    drive_folder_id,
    format_price,
    parse_bedrooms,
    parse_int,
    parse_price,
    price_band,
    slugify,
)


def _generated_description(listing: Listing) -> str:
    """Meta description from structured facts. The source `description` column
    repeats the title for ~99% of rows, so it is deliberately not used."""
    bits = []
    label = listing.bedrooms_label
    if label:
        if label == "Studio":
            bits.append("Studio")
        elif label.endswith("+"):
            bits.append(f"{label} bedroom")
        else:
            bits.append(f"{label}-bedroom")
    bits.append(listing.type.lower())

    verb = {
        "sale": "for sale in",
        "rent": "for rent in",
        "business": "business for sale in",
    }[listing.deal]

    head = " ".join(bits).capitalize()
    where = listing.location or "Pattaya"
    price = format_price(listing.price_thb, listing.deal)
    return f"{head} {verb} {where}, {price}. Ref {listing.reference}. Call +66 95 348 3725."[:158]


def dedupe(rows: list[dict]) -> list[dict]:
    """Keep the newest row per reference. 1,033 raw rows carry 50 duplicates."""
    best: dict[str, dict] = {}
    for row in rows:
        ref = (row.get("reference") or "").strip()
        if not ref:
            continue
        current = best.get(ref)
        if current is None or (row.get("last_update") or "") > (current.get("last_update") or ""):
            best[ref] = row
    return [best[k] for k in sorted(best)]


def normalize(row: dict) -> Listing | None:
    reference = (row.get("reference") or "").strip()
    title = (row.get("title") or "").strip()
    status = (row.get("status") or "").strip()
    ptype = (row.get("type") or "").strip()

    deal = DEAL_FROM_STATUS.get(status)
    if not reference or not title or deal is None or ptype not in TYPE_SLUGS:
        return None

    location = (row.get("location") or "").strip()
    project = (row.get("project") or "").strip()
    price = parse_price(row.get("price", ""))
    bedrooms, bedrooms_label = parse_bedrooms(row.get("bedrooms", ""))

    listing = Listing(
        reference=reference,
        slug=build_slug(title, reference),
        title=title,
        project=project,
        project_slug=slugify(project),
        type=ptype,
        type_slug=TYPE_SLUGS[ptype],
        deal=deal,
        price_thb=price,
        price_band=price_band(price, deal),
        bedrooms=bedrooms,
        bedrooms_label=bedrooms_label,
        bathrooms=parse_int(row.get("bathrooms", "")),
        location=location,
        location_slug=slugify(location),
        source_url=(row.get("source_url") or "").strip(),
        drive_folder_id=drive_folder_id(row.get("photo_folder", "")),
        last_update=(row.get("last_update") or "").strip(),
    )
    listing.meta_description = _generated_description(listing)
    return listing


def load_csv(path: Path) -> list[Listing]:
    # utf-8-sig: the export carries a BOM that otherwise corrupts the first header.
    with open(path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    listings = [l for l in (normalize(r) for r in dedupe(rows)) if l is not None]
    listings.sort(key=lambda l: l.reference)

    slugs = [l.slug for l in listings]
    if len(set(slugs)) != len(slugs):
        dupes = {s for s in slugs if slugs.count(s) > 1}
        raise ValueError(f"slug collision: {sorted(dupes)[:5]}")

    return listings


def write_catalog(listings: list[Listing], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "count": len(listings),
        "listings": [l.to_dict() for l in listings],
    }
    # sort_keys + trailing newline keeps rebuild diffs empty when nothing changed.
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_catalog(path: Path) -> list[Listing]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Listing.from_dict(d) for d in data["listings"]]
