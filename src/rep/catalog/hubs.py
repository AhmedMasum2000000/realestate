"""Hub page enumeration.

Deal-first hierarchy (`/for-sale/condos/jomtien/`) because search intent is
deal+type dominant, with `/areas/<location>/` giving every area a second,
non-competing entry point. Every ancestor is a real generated page, so a
breadcrumb can never point at a 404.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .aggregate import MIN_HUB_LISTINGS
from .content import AREA_COPY, TYPE_COPY
from .model import DEAL_SEGMENTS, TYPE_LABELS_PLURAL, Listing

MIN_PROJECT_LISTINGS = 3

DEAL_HUB_TITLES = {
    "sale": ("Property for Sale in Pattaya", "for sale"),
    "rent": ("Property for Rent in Pattaya", "for rent"),
    "business": ("Businesses for Sale in Pattaya", "for sale"),
}


@dataclass
class Hub:
    path: str
    kind: str                 # all | deal | deal-type | deal-type-area | area | project
    h1: str
    title: str
    description: str
    listings: list[Listing]
    crumbs: list[tuple[str, str]] = field(default_factory=list)
    intro: str = ""
    parent: str = ""
    siblings: list[tuple[str, str, int]] = field(default_factory=list)
    nav_current: str = ""

    @property
    def count(self) -> int:
        return len(self.listings)


def _by(listings: list[Listing], **filters) -> list[Listing]:
    out = listings
    for key, value in filters.items():
        out = [l for l in out if getattr(l, key) == value]
    return out


def build_hubs(listings: list[Listing]) -> list[Hub]:
    hubs: list[Hub] = []

    hubs.append(Hub(
        path="/properties/",
        kind="all",
        h1="Every property on our books",
        title=f"All Properties in Pattaya — {len(listings)} Listings | Pattaya Home Pro",
        description=(
            f"Browse all {len(listings)} properties across Pattaya and the Eastern "
            "Seaboard — condos, houses, pool villas, land and businesses, for sale and rent."
        ),
        listings=listings,
        crumbs=[("Home", "/")],
        nav_current="properties",
    ))

    for deal, segment in DEAL_SEGMENTS.items():
        deal_listings = _by(listings, deal=deal)
        if not deal_listings:
            continue
        label, phrase = DEAL_HUB_TITLES[deal]
        deal_path = f"/{segment}/"
        hubs.append(Hub(
            path=deal_path,
            kind="deal",
            h1=label,
            title=f"{label} — {len(deal_listings)} Listings | Pattaya Home Pro",
            description=(
                f"{len(deal_listings)} properties {phrase} across Pattaya, Jomtien, "
                "Pratumnak and the Eastern Seaboard. Priced against real transfers."
            ),
            listings=deal_listings,
            crumbs=[("Home", "/")],
            nav_current=segment if segment != "businesses-for-sale" else "business",
        ))

        # deal x type
        types = sorted({l.type for l in deal_listings})
        type_hubs = []
        for ptype in types:
            typed = _by(deal_listings, type=ptype)
            if len(typed) < MIN_HUB_LISTINGS:
                continue
            type_slug = typed[0].type_slug
            plural = TYPE_LABELS_PLURAL.get(ptype, ptype)
            h1 = f"{plural} {phrase.title()} in Pattaya"
            path = f"{deal_path}{type_slug}/"
            type_hubs.append((plural, path, len(typed)))
            hubs.append(Hub(
                path=path,
                kind="deal-type",
                h1=h1,
                title=f"{h1} — {len(typed)} Listings | Pattaya Home Pro",
                description=(
                    f"{len(typed)} {plural.lower()} {phrase} in Pattaya. "
                    f"Compare prices by bedroom count and area."
                ),
                listings=typed,
                crumbs=[("Home", "/"), (label, deal_path)],
                intro=TYPE_COPY.get(type_slug, ""),
                parent=deal_path,
                nav_current=segment if segment != "businesses-for-sale" else "business",
            ))

            # deal x type x area
            areas = sorted({l.location for l in typed if l.location})
            area_hubs = []
            made: list[Hub] = []
            for area in areas:
                scoped = _by(typed, location=area)
                if len(scoped) < MIN_HUB_LISTINGS:
                    continue
                area_slug = scoped[0].location_slug
                area_h1 = f"{plural} {phrase.title()} in {area}"
                area_path = f"{path}{area_slug}/"
                area_hubs.append((area, area_path, len(scoped)))
                made.append(Hub(
                    path=area_path,
                    kind="deal-type-area",
                    h1=area_h1,
                    title=f"{area_h1} — {len(scoped)} Listings | Pattaya Home Pro",
                    description=(
                        f"{len(scoped)} {plural.lower()} {phrase} in {area}, Pattaya. "
                        "Median prices by bedroom count and what the area is actually like."
                    ),
                    listings=scoped,
                    crumbs=[("Home", "/"), (label, deal_path), (plural, path)],
                    intro=AREA_COPY.get(area_slug, ""),
                    parent=path,
                    nav_current=segment if segment != "businesses-for-sale" else "business",
                ))

            # Each area hub links sideways to its peers under the same
            # deal+type parent — the "condos for sale, but somewhere else"
            # move a visitor actually makes.
            for made_hub in made:
                made_hub.siblings = [s for s in area_hubs if s[1] != made_hub.path]
            hubs.extend(made)

            for hub in hubs:
                if hub.path == path:
                    hub.siblings = area_hubs

        for hub in hubs:
            if hub.path == deal_path:
                hub.siblings = type_hubs

    # area hubs — every area with any inventory, not just >= MIN
    areas = sorted({l.location for l in listings if l.location})
    for area in areas:
        scoped = _by(listings, location=area)
        area_slug = scoped[0].location_slug
        h1 = f"Property in {area}"
        hubs.append(Hub(
            path=f"/areas/{area_slug}/",
            kind="area",
            h1=h1,
            title=f"{h1}, Pattaya — {len(scoped)} Listings | Pattaya Home Pro",
            description=(
                f"{len(scoped)} properties in {area}, Pattaya — for sale and rent. "
                "What the area is like, what it costs, and what is available now."
            ),
            listings=scoped,
            crumbs=[("Home", "/"), ("Areas", "/properties/")],
            intro=AREA_COPY.get(area_slug, ""),
            nav_current="properties",
        ))

    # project hubs — a weak taxonomy (901 projects across 983 rows), so only the
    # handful with real depth get a page.
    projects: dict[str, list[Listing]] = {}
    for l in listings:
        if l.project_slug:
            projects.setdefault(l.project_slug, []).append(l)
    for slug, scoped in sorted(projects.items()):
        if len(scoped) < MIN_PROJECT_LISTINGS:
            continue
        name = scoped[0].project
        h1 = f"{name} — Pattaya"
        hubs.append(Hub(
            path=f"/projects/{slug}/",
            kind="project",
            h1=name,
            title=f"{name} — {len(scoped)} Units Available | Pattaya Home Pro",
            description=(
                f"{len(scoped)} units available at {name}, Pattaya. "
                "Current prices, layouts and availability."
            ),
            listings=scoped,
            crumbs=[("Home", "/"), ("Properties", "/properties/")],
            nav_current="properties",
        ))

    return hubs


def area_siblings(hubs: list[Hub], adjacency: dict[str, list[str]], slug: str) -> list[tuple[str, str, int]]:
    """Adjacent areas, for sideways linking. Hand-mapped rather than derived —
    geographic adjacency is not in the data."""
    index = {h.path: h for h in hubs if h.kind == "area"}
    out = []
    for neighbour in adjacency.get(slug, []):
        hub = index.get(f"/areas/{neighbour}/")
        if hub:
            out.append((hub.listings[0].location, hub.path, hub.count))
    return out
