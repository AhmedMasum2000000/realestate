"""Read a property-listing CSV export and normalise it.

The exports we get vary: different agents, different tools, different column
names, sometimes Thai text and baht symbols. So rather than hard-coding one
schema we score each CSV header against a set of aliases and report what we
could not place, so a human can map the leftovers in sites.yml.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

# Canonical field -> header aliases (lowercased, non-alphanumerics stripped).
ALIASES: dict[str, tuple[str, ...]] = {
    "reference": ("ref", "refno", "reference", "referenceno", "id", "listingid",
                  "propertyid", "code", "propertycode", "sku"),
    "title": ("title", "name", "propertyname", "listingtitle", "posttitle", "heading"),
    "description": ("description", "desc", "details", "content", "body", "notes",
                    "propertydescription", "longdescription"),
    "price": ("price", "saleprice", "askingprice", "amount", "cost", "pricethb",
              "sellingprice"),
    "rent_price": ("rent", "rentprice", "rentalprice", "monthlyrent", "pricerent",
                   "rentmonthly", "rentpermonth"),
    "currency": ("currency", "cur", "ccy"),
    "deal_type": ("dealtype", "listingtype", "saleorrent", "offertype",
                  "transactiontype", "forsalerent", "salerent", "status"),
    "property_type": ("propertytype", "type", "categorytype", "category",
                      "buildingtype", "hometype", "unittype"),
    "bedrooms": ("bedrooms", "beds", "bed", "noofbedrooms", "bedroom", "br"),
    "bathrooms": ("bathrooms", "baths", "bath", "noofbathrooms", "bathroom", "ba"),
    "size_sqm": ("size", "sqm", "area", "areasqm", "livingarea", "interiorsize",
                 "usablearea", "sizesqm", "builtuparea"),
    "land_sqm": ("landsize", "landarea", "plotsize", "landsqm", "plotarea", "landsqw"),
    "floor": ("floor", "floorno", "level", "storey"),
    "location": ("location", "area", "district", "zone", "neighbourhood",
                 "neighborhood", "city", "town", "subdistrict"),
    "address": ("address", "streetaddress", "fulladdress", "addr"),
    "latitude": ("lat", "latitude", "googlemaplat"),
    "longitude": ("lng", "long", "longitude", "googlemaplng"),
    "images": ("images", "image", "photos", "photo", "pictures", "imageurls",
               "gallery", "featuredimage", "imageurl", "thumbnail"),
    "features": ("features", "amenities", "facilities", "tags", "keywords"),
    "project": ("project", "development", "condoname", "building", "projectname"),
    "status": ("availability", "available", "propertystatus", "listingstatus"),
    "url": ("url", "link", "permalink", "sourceurl", "weburl"),
}

# Which canonical fields, if present, indicate this really is a listings CSV.
SIGNAL_FIELDS = {"price", "rent_price", "bedrooms", "bathrooms", "size_sqm",
                 "property_type", "title"}

# Fuzzy-matching guards, tuned against real agency exports:
#   _MIN_COVERAGE 0.45 keeps "Number of Bedrooms" (bedrooms = 0.50) while
#   rejecting "Brochure Link" (link = 0.33) and "Agent Name" (name = 0.44).
_MIN_COVERAGE = 0.45
_MIN_FUZZY_ALIAS = 4

_NUM_RE = re.compile(r"-?\d+(?:[.,]\d+)*")
_NONALNUM_RE = re.compile(r"[^a-z0-9]+")

SALE_WORDS = ("sale", "sell", "buy", "purchase", "ขาย")
RENT_WORDS = ("rent", "rental", "lease", "monthly", "เช่า")


def normalise_header(raw: str) -> str:
    """`Price (THB) ` -> `pricethb`, so aliases match despite formatting."""
    return _NONALNUM_RE.sub("", (raw or "").strip().lower())


@dataclass
class Listing:
    reference: str = ""
    title: str = ""
    description: str = ""
    price: float | None = None
    rent_price: float | None = None
    currency: str = "THB"
    deal_type: str = ""
    property_type: str = ""
    bedrooms: int | None = None
    bathrooms: float | None = None
    size_sqm: float | None = None
    land_sqm: float | None = None
    floor: str = ""
    location: str = ""
    address: str = ""
    latitude: float | None = None
    longitude: float | None = None
    images: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    project: str = ""
    status: str = ""
    url: str = ""
    extra: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_empty(self) -> bool:
        """A row with no title and no price is padding, not a property."""
        return not self.title.strip() and self.price is None and self.rent_price is None


@dataclass
class MappingReport:
    """What we made of the file's headers. Printed by `bin/inspect-csv`."""

    path: Path
    delimiter: str
    encoding: str
    row_count: int
    mapped: dict[str, str]          # canonical field -> original header
    unmapped: list[str]             # original headers we could not place
    missing_signals: list[str]      # canonical fields we'd have liked to find

    @property
    def looks_like_listings(self) -> bool:
        return len(SIGNAL_FIELDS & set(self.mapped)) >= 2


# -- parsing helpers --------------------------------------------------------

def parse_number(value: str | None) -> float | None:
    """`฿ 4,500,000` -> 4500000.0. Returns None when there is no number."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    match = _NUM_RE.search(text.replace(" ", ""))
    if not match:
        return None
    token = match.group(0)
    # Thousands separators vs decimal comma: if the last comma is followed by
    # exactly 3 digits and there is no dot, treat commas as separators.
    if "," in token and "." not in token:
        head, _, tail = token.rpartition(",")
        token = token.replace(",", "") if len(tail) == 3 else token.replace(",", ".")
    else:
        token = token.replace(",", "")
    try:
        return float(token)
    except ValueError:
        return None


def parse_int(value: str | None) -> int | None:
    num = parse_number(value)
    return int(num) if num is not None else None


def split_multi(value: str | None) -> list[str]:
    """Split an images/features cell on the separators exports actually use."""
    if not value:
        return []
    parts = re.split(r"[|;,\n]+", str(value))
    return [p.strip() for p in parts if p and p.strip()]


def classify_deal(*values: str | None) -> str:
    """Decide sale vs rent from whatever text fields hint at it."""
    blob = " ".join(str(v or "") for v in values).lower()
    has_sale = any(w in blob for w in SALE_WORDS)
    has_rent = any(w in blob for w in RENT_WORDS)
    if has_sale and has_rent:
        return "both"
    if has_rent:
        return "rent"
    if has_sale:
        return "sale"
    return ""


def build_mapping(headers: Iterable[str]) -> tuple[dict[str, str], list[str]]:
    """Match CSV headers to canonical fields.

    Exact alias match wins; then a prefix/substring match, so `Bedrooms (no.)`
    still lands on `bedrooms`. Each canonical field is claimed at most once --
    first column wins, which matches how exports order their columns.
    """
    mapped: dict[str, str] = {}
    unmapped: list[str] = []

    headers = list(headers)
    normalised = [(h, normalise_header(h)) for h in headers]

    for original, norm in normalised:
        if not norm:
            continue
        hit = next(
            (field_ for field_, aliases in ALIASES.items()
             if norm in aliases and field_ not in mapped),
            None,
        )
        if hit:
            mapped[hit] = original

    for original, norm in normalised:
        if not norm or original in mapped.values():
            continue
        # Score candidates by how much of the header the alias accounts for,
        # and take the best. Coverage matters more than raw length: for
        # "areadistrict", location's "district" (0.67) beats size_sqm's
        # "area" (0.33). The floor rejects incidental substrings -- "link"
        # inside "Brochure Link" is only 0.33, so it is not the listing URL.
        # Aliases under 4 chars are exact-match only; "br" and "ba" would
        # otherwise match half the file.
        best_field, best_score = None, 0.0
        for field_, aliases in ALIASES.items():
            if field_ in mapped:
                continue
            for alias in aliases:
                if len(alias) < _MIN_FUZZY_ALIAS or alias not in norm:
                    continue
                score = len(alias) / len(norm)
                if score >= _MIN_COVERAGE and score > best_score:
                    best_field, best_score = field_, score
        if best_field:
            mapped[best_field] = original
        else:
            unmapped.append(original)

    return mapped, unmapped


def _read_text(path: Path) -> tuple[str, str]:
    """Read the file, trying the encodings these exports actually come in."""
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp874", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace"), "utf-8 (with replacements)"


def sniff_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        # Fall back to whichever candidate appears most in the header line.
        head = sample.splitlines()[0] if sample.splitlines() else ""
        return max(",;\t|", key=head.count)


def load_csv(
    path: Path, overrides: dict[str, str] | None = None
) -> tuple[list[Listing], MappingReport]:
    """Parse a listings CSV into Listing objects plus a mapping report.

    `overrides` maps canonical field -> exact CSV header, for the columns the
    auto-matcher gets wrong. Put them in sites.yml under listings.columns.
    """
    text, encoding = _read_text(path)
    if not text.strip():
        raise ValueError(f"{path} is empty")

    delimiter = sniff_delimiter(text[:8192])
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    headers = [h for h in (reader.fieldnames or []) if h is not None]
    if not headers:
        raise ValueError(f"{path} has no header row")

    mapped, unmapped = build_mapping(headers)
    for canonical, header in (overrides or {}).items():
        if header in headers:
            mapped[canonical] = header
            if header in unmapped:
                unmapped.remove(header)

    listings: list[Listing] = []
    for row in reader:
        listing = _row_to_listing(row, mapped, unmapped)
        if not listing.is_empty():
            listings.append(listing)

    report = MappingReport(
        path=path,
        delimiter=delimiter,
        encoding=encoding,
        row_count=len(listings),
        mapped=mapped,
        unmapped=unmapped,
        missing_signals=sorted(SIGNAL_FIELDS - set(mapped)),
    )
    return listings, report


def _get(row: dict[str, str], mapped: dict[str, str], key: str) -> str:
    header = mapped.get(key)
    if not header:
        return ""
    return (row.get(header) or "").strip()


def _row_to_listing(
    row: dict[str, str], mapped: dict[str, str], unmapped: list[str]
) -> Listing:
    g = lambda k: _get(row, mapped, k)  # noqa: E731 - local shorthand, reads better

    deal = classify_deal(g("deal_type"), g("status"), g("title"))
    price = parse_number(g("price"))
    rent = parse_number(g("rent_price"))
    if not deal:
        deal = "rent" if (rent and not price) else "sale" if price else ""

    listing = Listing(
        reference=g("reference"),
        title=g("title"),
        description=g("description"),
        price=price,
        rent_price=rent,
        currency=g("currency") or "THB",
        deal_type=deal,
        property_type=g("property_type"),
        bedrooms=parse_int(g("bedrooms")),
        bathrooms=parse_number(g("bathrooms")),
        size_sqm=parse_number(g("size_sqm")),
        land_sqm=parse_number(g("land_sqm")),
        floor=g("floor"),
        location=g("location"),
        address=g("address"),
        latitude=parse_number(g("latitude")),
        longitude=parse_number(g("longitude")),
        images=split_multi(g("images")),
        features=split_multi(g("features")),
        project=g("project"),
        status=g("status"),
        url=g("url"),
        extra={h: (row.get(h) or "").strip() for h in unmapped if (row.get(h) or "").strip()},
    )

    if not listing.title:
        # Build something usable rather than importing an untitled post.
        bits = [listing.property_type, listing.project or listing.location]
        if listing.bedrooms:
            bits.append(f"{listing.bedrooms} bed")
        listing.title = " ".join(b for b in bits if b).strip() or listing.reference

    return listing


def apply_filter(listings: list[Listing], rules: dict[str, str]) -> list[Listing]:
    """Keep listings whose field contains the given value (case-insensitive).

    Used so one shared export can feed several sites -- e.g. only Pattaya rows
    go to the Pattaya site.
    """
    if not rules:
        return listings
    out = []
    for item in listings:
        data = item.to_dict()
        if all(
            str(want).lower() in str(data.get(key, "")).lower()
            for key, want in rules.items()
        ):
            out.append(item)
    return out
