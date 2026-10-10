"""Hub statistics.

A hub page that only lists cards is thin. These stats come from the fields that
are actually well populated — price (100%), bedrooms (93%), type, last_update —
and give each hub something true and specific to say. `size` is deliberately
unused: at 2% coverage any per-square-metre figure would be a fabrication.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime

from .model import Listing, format_price

MIN_HUB_LISTINGS = 5


def percentile(values: list[int], pct: float) -> int:
    """Nearest-rank percentile. Exact and stable for small samples, which
    matters more here than interpolation."""
    if not values:
        return 0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, round(pct / 100 * (len(ordered) - 1))))
    return ordered[idx]


def _parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def price_stats(listings: list[Listing]) -> dict:
    """Priced separately per deal — a rent median and a sale median cannot
    share a scale."""
    out = {}
    for deal in ("sale", "rent", "business"):
        prices = [l.price_thb for l in listings if l.deal == deal and l.price_thb > 0]
        if not prices:
            continue
        out[deal] = {
            "count": len(prices),
            "low": percentile(prices, 10),
            "median": percentile(prices, 50),
            "high": percentile(prices, 90),
            "low_display": format_price(percentile(prices, 10), deal),
            "median_display": format_price(percentile(prices, 50), deal),
            "high_display": format_price(percentile(prices, 90), deal),
        }
    return out


def price_by_bedrooms(listings: list[Listing], deal: str) -> list[dict]:
    """Median price per bedroom count — the single most useful table on a hub,
    because it is the comparison a buyer is actually trying to make."""
    buckets: dict[int, list[int]] = {}
    labels: dict[int, str] = {}
    for l in listings:
        if l.deal != deal or l.bedrooms is None or l.price_thb <= 0:
            continue
        buckets.setdefault(l.bedrooms, []).append(l.price_thb)
        labels.setdefault(l.bedrooms, l.bedrooms_label)

    rows = []
    for beds in sorted(buckets):
        prices = buckets[beds]
        if len(prices) < 3:  # too few to quote a median honestly
            continue
        rows.append({
            "label": labels[beds] if beds == 0 else f"{labels[beds]} bed",
            "count": len(prices),
            "median": percentile(prices, 50),
            "median_display": format_price(percentile(prices, 50), deal),
            "low_display": format_price(percentile(prices, 10), deal),
            "high_display": format_price(percentile(prices, 90), deal),
        })
    return rows


def bedroom_mix(listings: list[Listing]) -> list[dict]:
    counts = Counter(l.bedrooms_label for l in listings if l.bedrooms_label)
    total = sum(counts.values())
    if not total:
        return []
    ordered = sorted(
        counts.items(),
        key=lambda kv: (kv[0] != "Studio", len(kv[0]), kv[0]),
    )
    return [
        {"label": k, "count": v, "pct": round(100 * v / total)}
        for k, v in ordered
    ]


def freshness(listings: list[Listing], today: date) -> dict:
    dates = [d for d in (_parse_date(l.last_update) for l in listings) if d]
    if not dates:
        return {"recent": 0, "newest": "", "line": f"{len(listings)} listings."}
    recent = sum(1 for d in dates if (today - d).days <= 90)
    newest = max(dates)
    line = f"{len(listings)} listings on our books"
    if recent:
        line += f", {recent} updated in the last 90 days"
    return {"recent": recent, "newest": newest.isoformat(), "line": line + "."}


def top_projects(listings: list[Listing], limit: int = 5) -> list[dict]:
    counts = Counter(l.project for l in listings if l.project.strip())
    return [
        {"name": name, "count": n}
        for name, n in counts.most_common(limit)
        if n >= 2
    ]


def newest(listings: list[Listing], limit: int = 6) -> list[Listing]:
    return sorted(
        listings,
        key=lambda l: (l.last_update, l.reference),
        reverse=True,
    )[:limit]


def summarize(listings: list[Listing], today: date | None = None) -> dict:
    """Everything a hub template needs to render substantive content."""
    today = today or date.today()
    deals = Counter(l.deal for l in listings)
    types = Counter(l.type for l in listings)
    locations = Counter(l.location for l in listings if l.location)

    dominant = "sale"
    if deals:
        dominant = deals.most_common(1)[0][0]

    return {
        "count": len(listings),
        "deals": dict(deals),
        "dominant_deal": dominant,
        "types": types.most_common(),
        "locations": locations.most_common(),
        "prices": price_stats(listings),
        "by_bedrooms": price_by_bedrooms(listings, dominant),
        "bedroom_mix": bedroom_mix(listings),
        "projects": top_projects(listings),
        "freshness": freshness(listings, today),
        "indexable_count": sum(1 for l in listings if l.indexable),
    }


def sort_for_display(listings: list[Listing]) -> list[Listing]:
    """Listings with photos first, then newest, then reference.

    Reference is the final tie-break so the ordering is fully deterministic —
    otherwise every rebuild reshuffles pages and the diff is unreadable.
    """
    return sorted(
        listings,
        key=lambda l: (not bool(l.hero_image), _neg_date(l.last_update), l.reference),
    )


def _neg_date(value: str) -> str:
    """Invert an ISO date so it sorts newest-first inside an ascending sort."""
    d = _parse_date(value)
    if not d:
        return "9999"
    return str(99999999 - int(d.strftime("%Y%m%d")))
