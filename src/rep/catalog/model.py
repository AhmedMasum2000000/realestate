"""Normalized listing model for the Pattaya Home Pro catalog.

The raw export is structurally rich but editorially empty: price, type,
location and bedrooms are well populated, while `images` is entirely empty and
`description` repeats `title` for ~99% of rows. Everything here is derived from
the fields that are actually reliable.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field, asdict

# Raw `type` values -> URL segment. Plural reads naturally in a path
# ("/for-sale/condos/jomtien/") and matches how people search.
TYPE_SLUGS = {
    "Condo": "condos",
    "House": "houses",
    "Pool Villa": "pool-villas",
    "Business": "businesses",
    "Townhouse": "townhouses",
    "Land": "land",
    "Commercial": "commercial",
    "Apartment": "apartments",
    "Hotel": "hotels",
}

TYPE_LABELS_PLURAL = {
    "Condo": "Condos",
    "House": "Houses",
    "Pool Villa": "Pool Villas",
    "Business": "Businesses",
    "Townhouse": "Townhouses",
    "Land": "Land",
    "Commercial": "Commercial Property",
    "Apartment": "Apartments",
    "Hotel": "Hotels",
}

# `Business For Sale` collapses status and type in the source data. Keeping
# `deal` separate from `type` stops those 53 rows double-counting in facets.
DEAL_FROM_STATUS = {
    "For Sale": "sale",
    "For Rent": "rent",
    "Business For Sale": "business",
}

DEAL_SEGMENTS = {
    "sale": "for-sale",
    "rent": "for-rent",
    "business": "businesses-for-sale",
}

DEAL_LABELS = {
    "sale": "For Sale",
    "rent": "For Rent",
    "business": "Business For Sale",
}

LOCATIONS = [
    "Jomtien", "East Pattaya", "North Pattaya", "Huay Yai", "Pratumnak",
    "Central Pattaya", "South Pattaya", "Na Jomtien", "Mabprachan",
    "Thepprasit", "Nong Pla Lai", "Sattahip", "Bang Saray", "Laem Chabang",
    "Rayong",
]

SALE_BANDS = [
    (2_000_000, "Under ฿2M"),
    (5_000_000, "฿2M – ฿5M"),
    (10_000_000, "฿5M – ฿10M"),
    (25_000_000, "฿10M – ฿25M"),
    (None, "฿25M+"),
]

RENT_BANDS = [
    (20_000, "Under ฿20K"),
    (40_000, "฿20K – ฿40K"),
    (80_000, "฿40K – ฿80K"),
    (None, "฿80K+"),
]


def slugify(value: str) -> str:
    """Lowercase ASCII slug. Thai and accented characters are transliterated
    away rather than percent-encoded, keeping URLs readable and typeable."""
    value = unicodedata.normalize("NFKD", value or "")
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return re.sub(r"-{2,}", "-", value)


def parse_price(raw: str) -> int:
    digits = re.sub(r"[^0-9]", "", raw or "")
    return int(digits) if digits else 0


def parse_bedrooms(raw: str) -> tuple[int | None, str]:
    """Return (sortable int, display label). The source uses literal 'Studio'
    and '10+' alongside plain integers."""
    raw = (raw or "").strip()
    if not raw:
        return None, ""
    if raw.lower() == "studio":
        return 0, "Studio"
    if raw.endswith("+"):
        digits = re.sub(r"[^0-9]", "", raw)
        return (int(digits), raw) if digits else (None, raw)
    if raw.isdigit():
        return int(raw), raw
    return None, raw


def parse_int(raw: str) -> int | None:
    raw = (raw or "").strip()
    return int(raw) if raw.isdigit() else None


def price_band(price: int, deal: str) -> str:
    bands = RENT_BANDS if deal == "rent" else SALE_BANDS
    for ceiling, label in bands:
        if ceiling is None or price < ceiling:
            return label
    return bands[-1][1]


def format_price(price: int, deal: str) -> str:
    if not price:
        return "Price on application"
    if deal == "rent":
        return f"฿{price:,}/month"
    return f"฿{price:,}"


def drive_folder_id(url: str) -> str:
    match = re.search(r"/folders/([A-Za-z0-9_-]+)", url or "")
    return match.group(1) if match else ""


@dataclass
class Listing:
    reference: str
    slug: str
    title: str
    project: str
    project_slug: str
    type: str
    type_slug: str
    deal: str
    price_thb: int
    price_band: str
    bedrooms: int | None
    bedrooms_label: str
    bathrooms: int | None
    location: str
    location_slug: str
    source_url: str
    drive_folder_id: str
    last_update: str
    images: list[str] = field(default_factory=list)
    hero_image: str = ""
    meta_description: str = ""
    copy_source: str = "generated"

    @property
    def indexable(self) -> bool:
        """Data-driven, so a listing starts earning indexation the moment
        enrichment gives it a photo or real copy — no manual flag flipping."""
        return bool(self.hero_image) or self.copy_source == "scraped"

    @property
    def url(self) -> str:
        return f"/property/{self.slug}/"

    @property
    def price_display(self) -> str:
        return format_price(self.price_thb, self.deal)

    @property
    def deal_label(self) -> str:
        return DEAL_LABELS[self.deal]

    @property
    def type_label_plural(self) -> str:
        return TYPE_LABELS_PLURAL.get(self.type, self.type)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["indexable"] = self.indexable
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Listing":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


def build_slug(title: str, reference: str) -> str:
    """Keyword-bearing but collision-free: the reference is the dedupe key, so
    appending it guarantees uniqueness without depending on title text."""
    stem = slugify(title)[:60].strip("-")
    return f"{stem}-{reference.lower()}" if stem else reference.lower()
