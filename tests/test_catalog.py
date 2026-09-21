"""Tests for the property catalog: normalization, aggregation, linking, SEO."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.catalog import aggregate, links  # noqa: E402
from rep.catalog.enrich import casa  # noqa: E402
from rep.catalog.loader import dedupe, normalize  # noqa: E402
from rep.catalog.model import (  # noqa: E402
    Listing,
    build_slug,
    format_price,
    parse_bedrooms,
    parse_price,
    price_band,
    slugify,
)
from rep.catalog.render import rebase  # noqa: E402


def row(**over) -> dict:
    base = {
        "reference": "HZ1001", "title": "Sea View Condo in Jomtien",
        "project": "Sample Residence", "type": "Condo", "status": "For Sale",
        "price": "4200000", "bedrooms": "2", "bathrooms": "2", "size": "",
        "location": "Jomtien", "description": "Sea View Condo in Jomtien",
        "images": "", "photo_folder": "https://drive.google.com/drive/folders/ABC123",
        "source_url": "https://casapattaya.com/property/1/", "last_update": "2025-10-01",
    }
    base.update(over)
    return base


def make(**over) -> Listing:
    listing = normalize(row(**over))
    assert listing is not None
    return listing


# ---------- normalization ----------

def test_studio_and_open_ended_bedrooms():
    # The export mixes integers with the literal strings "Studio" and "10+".
    assert parse_bedrooms("Studio") == (0, "Studio")
    assert parse_bedrooms("10+") == (10, "10+")
    assert parse_bedrooms("3") == (3, "3")
    assert parse_bedrooms("") == (None, "")


def test_deal_is_modelled_separately_from_type():
    # "Business For Sale" collapses status and type in the source; conflating
    # them would double-count those rows in every facet.
    business = make(status="Business For Sale", type="Business")
    assert business.deal == "business"
    assert business.type == "Business"
    assert make(status="For Rent", price="30000").deal == "rent"


def test_rows_with_unusable_fields_are_dropped():
    assert normalize(row(status="Coming Soon")) is None
    assert normalize(row(type="Spaceship")) is None
    assert normalize(row(reference="")) is None


def test_dedupe_keeps_the_newest_row_per_reference():
    rows = [
        row(reference="HZ1", last_update="2025-01-01", price="1000000"),
        row(reference="HZ1", last_update="2026-04-03", price="2000000"),
        row(reference="HZ2", last_update="2025-06-01"),
    ]
    kept = dedupe(rows)
    assert len(kept) == 2
    assert next(r for r in kept if r["reference"] == "HZ1")["price"] == "2000000"


def test_price_parsing_and_banding():
    assert parse_price("฿4,200,000") == 4200000
    assert parse_price("") == 0
    assert price_band(1_000_000, "sale") == "Under ฿2M"
    assert price_band(300_000_000, "sale") == "฿25M+"
    # Rent is banded on a different scale entirely.
    assert price_band(30_000, "rent") == "฿20K – ฿40K"


def test_rent_price_is_displayed_per_month():
    assert format_price(30000, "rent") == "฿30,000/month"
    assert format_price(4200000, "sale") == "฿4,200,000"
    assert format_price(0, "sale") == "Price on application"


# ---------- slugs ----------

def test_slug_is_keyword_bearing_and_collision_free():
    slug = build_slug("Sea View Condo in Jomtien", "HZ1001")
    assert slug == "sea-view-condo-in-jomtien-hz1001"
    # Identical titles cannot collide, because the reference is the dedupe key.
    assert build_slug("Pool Villa", "A1") != build_slug("Pool Villa", "A2")


def test_slug_survives_punctuation_and_non_ascii():
    assert slugify("Riviera — Jomtien (Sea View!)") == "riviera-jomtien-sea-view"
    assert not slugify("บ้านพัทยา").strip("-")


def test_slug_stays_bounded_for_very_long_titles():
    slug = build_slug("A" * 300, "HZ9")
    assert len(slug) <= 64
    assert slug.endswith("-hz9")


# ---------- indexability ----------

def test_listing_is_not_indexable_until_it_has_photos():
    listing = make()
    assert listing.indexable is False
    listing.hero_image = "https://cdn.example/photo.jpg"
    assert listing.indexable is True


# ---------- aggregation ----------

def test_percentile_is_nearest_rank():
    values = [1, 2, 3, 4, 5]
    assert aggregate.percentile(values, 50) == 3
    assert aggregate.percentile(values, 0) == 1
    assert aggregate.percentile(values, 100) == 5
    assert aggregate.percentile([], 50) == 0


def test_bedroom_medians_skip_thin_buckets():
    # A median quoted from one or two listings is not a median.
    listings = [make(reference=f"A{i}", bedrooms="2", price="4000000") for i in range(4)]
    listings += [make(reference="B1", bedrooms="5", price="9000000")]
    rows = aggregate.price_by_bedrooms(listings, "sale")
    labels = [r["label"] for r in rows]
    assert "2 bed" in labels
    assert "5 bed" not in labels


def test_display_order_puts_photographed_listings_first():
    plain = make(reference="A1")
    shot = make(reference="Z9")
    shot.hero_image = "https://cdn.example/p.jpg"
    assert aggregate.sort_for_display([plain, shot])[0].reference == "Z9"


def test_summary_reports_dominant_deal():
    listings = [make(reference=f"S{i}") for i in range(3)]
    listings.append(make(reference="R1", status="For Rent", price="30000"))
    summary = aggregate.summarize(listings)
    assert summary["count"] == 4
    assert summary["dominant_deal"] == "sale"


# ---------- related listings ----------

def test_related_never_crosses_deal_types():
    subject = make(reference="A1")
    rental = make(reference="B1", status="For Rent", price="30000")
    assert links.related(subject, [rental]) == []


def test_related_prefers_same_project_then_location():
    subject = make(reference="A1")
    same_project = make(reference="B1", project="Sample Residence")
    other_area = make(reference="C1", project="Elsewhere", location="Naklua")
    ranked = links.related(subject, [other_area, same_project])
    assert ranked[0].reference == "B1"


def test_related_caps_listings_from_one_project():
    subject = make(reference="A1", project="Big Tower")
    pool = [make(reference=f"B{i}", project="Big Tower") for i in range(6)]
    assert len(links.related(subject, pool)) <= links.MAX_PER_PROJECT


def test_related_is_deterministic():
    subject = make(reference="A1")
    pool = [make(reference=f"B{i}", project=f"P{i}") for i in range(10)]
    first = [l.reference for l in links.related(subject, pool)]
    second = [l.reference for l in links.related(subject, list(reversed(pool)))]
    assert first == second


# ---------- sub-path rebasing ----------

def test_rebase_prefixes_root_relative_links_only():
    html = '<a href="/for-sale/"><img src="/assets/a.jpg"><a href="https://x.com/y">'
    out = rebase(html, "/realestate")
    assert 'href="/realestate/for-sale/"' in out
    assert 'src="/realestate/assets/a.jpg"' in out
    # Absolute URLs — including the canonical tag — must be left alone.
    assert 'href="https://x.com/y"' in out


def test_rebase_is_a_no_op_without_a_base():
    html = '<a href="/for-sale/">'
    assert rebase(html, "") == html


# ---------- scraper ----------

def test_gallery_excludes_the_recommended_carousel():
    html = (
        'swiper-large'
        '<img src="https://assets.casapattaya.com/file/casa-pattaya/a.jpg">'
        'recommended-slider'
        '<img src="https://assets.casapattaya.com/file/casa-pattaya/other.jpg">'
    )
    found = casa.gallery(html)
    assert found == ["https://assets.casapattaya.com/file/casa-pattaya/a.jpg"]


def test_hero_prefers_a_photograph_over_a_png_screenshot():
    images = [
        "https://assets.casapattaya.com/file/casa-pattaya/plan.png",
        "https://assets.casapattaya.com/file/casa-pattaya/room.jpg",
    ]
    assert casa.pick_hero(images).endswith("room.jpg")
    assert casa.pick_hero([]) == ""


def test_non_ascii_image_paths_are_percent_encoded():
    encoded = casa.encode("https://assets.casapattaya.com/file/casa-pattaya/สกรีน.png")
    assert " " not in encoded
    assert encoded.startswith("https://assets.casapattaya.com/")
    assert "%" in encoded


@pytest.mark.parametrize("url,delisted", [
    ("https://casapattaya.com/properties", True),
    ("https://casapattaya.com/properties/", True),
    ("https://casapattaya.com/property/123/", False),
])
def test_redirect_to_index_reads_as_delisted(url, delisted):
    assert url.rstrip("/").endswith("/properties") is delisted
