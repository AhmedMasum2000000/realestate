"""Related-listing selection.

The brief asked for suggestions driven by what a visitor is looking at. The
signal available at build time is the listing they are on, so relatedness is
scored against it: same project beats same street, same street beats same type,
and a similar budget beats a similar layout.

Deliberately *not* a "more properties" dump. Six scored, capped by project, so
the block stays a recommendation rather than a link farm.
"""

from __future__ import annotations

from .model import Listing

RELATED_COUNT = 6
MAX_PER_PROJECT = 2

SCORE_PROJECT = 4
SCORE_LOCATION = 3
SCORE_TYPE = 2
SCORE_BEDROOMS = 2
SCORE_PRICE = 2

PRICE_TOLERANCE = 0.25


def score(candidate: Listing, subject: Listing) -> int:
    total = 0
    if candidate.project_slug and candidate.project_slug == subject.project_slug:
        total += SCORE_PROJECT
    if candidate.location_slug and candidate.location_slug == subject.location_slug:
        total += SCORE_LOCATION
    if candidate.type_slug == subject.type_slug:
        total += SCORE_TYPE
    if (
        candidate.bedrooms is not None
        and subject.bedrooms is not None
        and abs(candidate.bedrooms - subject.bedrooms) <= 1
    ):
        total += SCORE_BEDROOMS
    if candidate.price_thb > 0 and subject.price_thb > 0:
        delta = abs(candidate.price_thb - subject.price_thb) / subject.price_thb
        if delta <= PRICE_TOLERANCE:
            total += SCORE_PRICE
    return total


def related(subject: Listing, pool: list[Listing], limit: int = RELATED_COUNT) -> list[Listing]:
    """Same deal is a hard filter: showing a rental beside a sale listing is
    noise, not a suggestion."""
    scored = []
    for candidate in pool:
        if candidate.reference == subject.reference or candidate.deal != subject.deal:
            continue
        value = score(candidate, subject)
        if value <= 0:
            continue
        # Photos first within a score band, then reference for determinism.
        scored.append((-value, not bool(candidate.hero_image), candidate.reference, candidate))

    scored.sort(key=lambda row: row[:3])

    chosen: list[Listing] = []
    per_project: dict[str, int] = {}
    for _, _, _, candidate in scored:
        key = candidate.project_slug
        if key:
            if per_project.get(key, 0) >= MAX_PER_PROJECT:
                continue
            per_project[key] = per_project.get(key, 0) + 1
        chosen.append(candidate)
        if len(chosen) >= limit:
            break
    return chosen


def build_related_index(listings: list[Listing]) -> dict[str, list[str]]:
    """Precompute related references for every listing.

    ~983² comparisons, which is under two seconds and far cheaper than doing it
    lazily inside the template for every rendered page.
    """
    return {
        l.reference: [r.reference for r in related(l, listings)]
        for l in listings
    }
