"""Hand-written editorial copy.

The reference site's *layout* is the model; its text is its own and is not
reused. Everything here is written for Pattaya, and the specifics — quota,
title classes, transfer tax, lease structure — are the point: concrete
knowledge is what separates an agency page from a portal page, both for a
reader deciding whom to trust and for a search engine deciding what the page
is actually about.
"""

HERO = {
    "kicker": "Condos · Houses · Pool Villas · Businesses",
    "headline": "Pattaya Home Pro knows Pattaya",
    "sub": (
        "We sell, rent and value property across Pattaya and the Eastern Seaboard — "
        "from a ฿1.5M studio in Jomtien to a beachfront villa in Na Jomtien. "
        "Straight answers on price, title and what a place is really worth."
    ),
}

POSITIONING = {
    "kicker": "Start here",
    "headline": "You're probably here to find out whether we're worth a phone call",
    "body": (
        "Fair. So here it is. We are a working Pattaya brokerage, not a listings portal. "
        "We hold stock across every area from Naklua down to Bang Saray, we know which "
        "buildings still have foreign freehold quota left, and we will tell you when a "
        "property is priced wrong — including when it is ours."
    ),
    "body_2": (
        "Most of what matters in a Thai property deal is not in the photographs. "
        "It is in the title deed, the quota, the lease structure and who pays the "
        "transfer fee. That is the part we are actually useful for."
    ),
}

SEGMENTS = [
    {
        "title": "Buyers",
        "text": "You need to know the title is clean, the quota is available, and the price "
                "matches what the building actually sells for — not what it is asking.",
        "cta": "Browse properties for sale",
        "href": "/for-sale/",
    },
    {
        "title": "Sellers",
        "text": "You need a price that moves and a buyer who completes. Most Pattaya "
                "listings fail at the transfer office, not at the viewing.",
        "cta": "Talk about listing",
        "href": "/get-in-touch/",
    },
    {
        "title": "Tenants",
        "text": "You need a place that is actually available, at the rent that was quoted, "
                "on a lease you can read. Long stay or short, furnished or bare.",
        "cta": "Browse rentals",
        "href": "/for-rent/",
    },
    {
        "title": "Landlords",
        "text": "You need tenants who pay and a unit that does not sit empty for the "
                "low season. Occupancy beats headline rent, every time.",
        "cta": "Talk about letting",
        "href": "/get-in-touch/",
    },
]

# Original aphorisms. The structure mirrors the reference's "laws" section; the
# content is Thai-market specific and written here.
RULES_INTRO = {
    "kicker": "What the brochures leave out",
    "headline": "Do enough deals in Pattaya and the same things keep going wrong",
}

RULES = [
    {
        "law": "Foreign freehold is a quota, not a right.",
        "note": "Only 49% of a building's saleable area can be foreign-owned freehold. "
                "Ask whether the quota is free on that unit before you fall in love with the view.",
    },
    {
        "law": "A chanote is not the same as a Nor Sor 3 Gor.",
        "note": "Both get called a title deed. Only one is fully surveyed and GPS-marked. "
                "The difference shows up when you try to sell, not when you buy.",
    },
    {
        "law": "A foreigner cannot own land. Anyone who says otherwise is selling you a problem.",
        "note": "Leasehold and company structures are legitimate and common. Nominee "
                "shareholders are not. That distinction is worth understanding before you sign.",
    },
    {
        "law": "Thirty years is the lease. The renewal is a promise.",
        "note": "A 30+30+30 lease is 30 years registered and 60 years of goodwill. "
                "Price it as thirty and treat the rest as upside.",
    },
    {
        "law": "Ask who pays the transfer fee before you agree the price.",
        "note": "Transfer fee, specific business tax and withholding tax can move the real "
                "number by six figures. 'Split 50/50' means nothing until it is written down.",
    },
    {
        "law": "A sea view from the bathroom is not a sea view.",
        "note": "If you have to lean out to see it, the next buyer will notice too. "
                "View premiums are the first thing to evaporate on resale.",
    },
    {
        "law": "A guaranteed rental return is a discount you have already paid for.",
        "note": "The guarantee is usually priced into the purchase. Work out the yield "
                "on the unit without the scheme, then decide.",
    },
    {
        "law": "Check the sinking fund before you check the gym.",
        "note": "A building with no reserves is a building with a special assessment coming. "
                "Ask for the juristic person's accounts. A good one will hand them over.",
    },
    {
        "law": "Low season is the honest season.",
        "note": "Anything will rent in January. If a landlord shows you occupancy figures, "
                "ask for May through September.",
    },
    {
        "law": "The cheapest unit in a good building beats the best unit in a bad one.",
        "note": "You can renovate a kitchen. You cannot renovate a juristic person, "
                "a car park ratio or a neighbouring construction site.",
    },
    {
        "law": "Off-plan is a bet on the developer, not on the building.",
        "note": "Look at what they finished five years ago and whether they finished it on time. "
                "The show unit tells you nothing.",
    },
    {
        "law": "If the price has not moved in a year, the price is not the problem.",
        "note": "It is usually the title, the quota, the access or the neighbour. "
                "Find out which before you negotiate.",
    },
]

OFF_MARKET = {
    "kicker": "One more thing",
    "headline": "What you see here isn't everything",
    "body": (
        "Everything in our public catalogue is real and current. But a good portion of "
        "Pattaya stock never reaches a website — owners who do not want their neighbours "
        "to know, pre-launch allocations, distressed sales handled quietly, and businesses "
        "sold without the staff finding out."
    ),
    "body_2": (
        "Those come out in a phone call, not a search filter. Tell us what you are actually "
        "looking for and we will tell you what is not on the page."
    ),
}

DEALS_INTRO = {
    "kicker": "Live inventory",
    "headline": "Here's a sample of what's on our books right now",
}

CONTACT = {
    "kicker": "Get in touch",
    "headline": "Let's talk",
    "sub": "Tell us what you're looking for. Or skip the form and call — it's faster.",
}

INTERESTS = [
    "I'm looking…",
    "To buy a property",
    "To rent long term",
    "To buy a business",
    "To sell or let my property",
    "For a valuation",
]

PROPERTY_INTERESTS = ["Condo", "House", "Pool Villa", "Land", "Business"]

TRUST_STRIP = {
    "title": "Areas we cover across Pattaya and the Eastern Seaboard",
}

# One paragraph per area. Written, not generated — this is what keeps the area
# hubs from reading as templated filler.
AREA_COPY = {
    "jomtien": "Jomtien is the default answer for most buyers, and usually the right one. "
               "A long flat beach road, the densest condo stock in Pattaya, and enough "
               "competition between buildings that prices stay honest. Foreign freehold "
               "quota is easier to find here than on Pratumnak.",
    "east-pattaya": "East Pattaya is where the space is. Houses and pool villas on real plots, "
                    "priced at a fraction of anything within sight of the water, at the cost "
                    "of needing a car for everything. Check flood history on anything low-lying.",
    "north-pattaya": "North Pattaya and Wongamat hold the quieter beachfront. Older low-rise "
                     "stock sits beside newer towers, and the gap between a sea view and a "
                     "partial sea view is priced sharply here. Walkable, and calmer after dark.",
    "pratumnak": "Pratumnak Hill sits between Pattaya and Jomtien, and trades on exactly that. "
                 "Low-rise, leafy, small beaches, and consistently tight foreign quota because "
                 "the buildings are smaller. Good resale, limited supply.",
    "central-pattaya": "Central Pattaya is convenience priced as convenience. You are walking to "
                       "everything, in a building with a car park ratio that assumes you are not "
                       "driving. Strong short-term rental demand, more noise than most buyers expect.",
    "south-pattaya": "South Pattaya covers the stretch down to Walking Street and the Rama 9 area. "
                     "Mixed stock, strong rental yields, and the highest variance in building "
                     "quality anywhere in the city. Worth viewing in person.",
    "na-jomtien": "Na Jomtien is the quiet continuation of Jomtien beach south towards Bang Saray. "
                  "Newer beachfront projects, genuinely swimmable water, and a car is assumed. "
                  "This is where the larger villas and the better sea views are.",
    "huay-yai": "Huay Yai is villa country. Large plots, private pools, and new-build houses at "
                "prices that would buy a two-bed condo nearer the beach. Fifteen minutes from "
                "Jomtien if the traffic behaves.",
    "mabprachan": "Mabprachan, around the reservoir, is the established expat house area east of "
                  "the city. Mature villages, big gardens, and a settled long-term community. "
                  "Quiet in the way that some buyers love and others find dull.",
    "thepprasit": "Thepprasit runs inland from Jomtien and works as a compromise: walkable to the "
                  "night market and the beach road, with condo prices below beachfront. Popular "
                  "with long-stay renters for exactly that reason.",
    "nong-pla-lai": "Nong Pla Lai sits north-east of the city near the new developments around "
                    "Highway 36. Newer houses, better roads than the older east-side villages, "
                    "and prices that still reflect the distance from the water.",
    "sattahip": "Sattahip is the naval town at the southern end of the coast. Quieter, cheaper, "
                "and genuinely Thai in a way central Pattaya no longer is. Worth considering "
                "if you do not need Pattaya itself every day.",
    "bang-saray": "Bang Saray is a working fishing village that has become a serious address. "
                  "Seafront restaurants, a calm bay, and new villa projects arriving quickly. "
                  "Thirty minutes south of Pattaya and a different pace entirely.",
    "laem-chabang": "Laem Chabang is port and industry, and the property market reflects that: "
                    "practical housing for people who work there, priced accordingly. "
                    "Rarely a lifestyle purchase, often a sound rental one.",
    "rayong": "Rayong province stretches east past Ban Chang towards Mae Ramphueng. Longer, "
              "emptier beaches and considerably more land for the money. A drive from Pattaya, "
              "but the EEC development corridor runs straight through it.",
}

# One paragraph per property type.
TYPE_COPY = {
    "condos": "Condominiums are the only property class a foreigner can own outright in Thailand, "
              "within the building's 49% foreign quota. That single fact drives most of the "
              "Pattaya market. Check the quota, the juristic person's reserves, and the car "
              "park ratio before the finishes.",
    "houses": "Houses give you space and a garden at prices the beachfront cannot match, with the "
              "caveat that the land underneath must be held on a lease or through a properly "
              "constituted company. Most sit east of Sukhumvit, where a car stops being optional.",
    "pool-villas": "Pool villas are Pattaya's strongest rental category and its most variable "
                   "purchase. Build quality between projects differs enormously. Look at the pool "
                   "plant, the roof and the boundary wall, in that order.",
    "townhouses": "Townhouses are the practical middle: more room than a condo, less maintenance "
                  "and less land cost than a house. Usually in gated villages east of the city, "
                  "usually the best value per square metre in Pattaya.",
    "land": "Land is the purest play on Pattaya's growth and the one with the most legal structure "
            "around it. Foreigners cannot hold it directly. Confirm the title class, the access "
            "rights and whether services actually reach the boundary.",
    "businesses": "Businesses for sale here are mostly bars, restaurants and guesthouses. The "
                  "building is rarely the asset — the lease, the licence and the trading history "
                  "are. Ask for books, and be sceptical if there are none.",
    "commercial": "Commercial stock covers shophouses, small office space and mixed-use buildings. "
                  "Yields beat residential and liquidity does not. Location on a main road with "
                  "genuine frontage is most of the value.",
    "apartments": "Apartments, as distinct from condominiums, are buildings without a registered "
                  "condominium licence. That means leasehold rather than freehold ownership. "
                  "Often cheaper, always harder to resell.",
    "hotels": "Hotel and resort assets trade on trading history and licence status rather than "
              "square metres. Occupancy through low season is the number that matters.",
}

# Adjacency for hub cross-linking. Hand-written: geographic neighbours a buyer
# would plausibly also consider, which is not something you can derive from data.
AREA_ADJACENCY = {
    "jomtien": ["na-jomtien", "pratumnak", "thepprasit"],
    "east-pattaya": ["mabprachan", "nong-pla-lai", "huay-yai"],
    "north-pattaya": ["central-pattaya", "pratumnak", "east-pattaya"],
    "pratumnak": ["jomtien", "south-pattaya", "central-pattaya"],
    "central-pattaya": ["north-pattaya", "south-pattaya", "pratumnak"],
    "south-pattaya": ["central-pattaya", "pratumnak", "thepprasit"],
    "na-jomtien": ["jomtien", "bang-saray", "huay-yai"],
    "huay-yai": ["na-jomtien", "east-pattaya", "bang-saray"],
    "mabprachan": ["east-pattaya", "nong-pla-lai", "huay-yai"],
    "thepprasit": ["jomtien", "south-pattaya", "east-pattaya"],
    "nong-pla-lai": ["east-pattaya", "mabprachan", "north-pattaya"],
    "sattahip": ["bang-saray", "na-jomtien", "huay-yai"],
    "bang-saray": ["na-jomtien", "sattahip", "huay-yai"],
    "laem-chabang": ["north-pattaya", "nong-pla-lai", "east-pattaya"],
    "rayong": ["sattahip", "bang-saray", "na-jomtien"],
}

SERVICES = [
    {
        "title": "Sales",
        "text": "Condos, houses, villas and land across Pattaya and the Eastern Seaboard. "
                "We price against what actually transferred, not what is still on the portals.",
    },
    {
        "title": "Rentals",
        "text": "Long-stay and seasonal lets, furnished or bare. We screen tenants properly "
                "because a bad tenant costs more than an empty month.",
    },
    {
        "title": "Business sales",
        "text": "Bars, restaurants, guesthouses and shops. Handled discreetly, because staff "
                "and suppliers finding out early kills the value.",
    },
    {
        "title": "Valuation",
        "text": "An honest number for a sale, a purchase, a bank or a divorce. "
                "Based on comparable transfers, with the reasoning shown.",
    },
    {
        "title": "Rental management",
        "text": "Listing, screening, check-in, maintenance and the low-season problem. "
                "For owners who are not in Thailand most of the year.",
    },
    {
        "title": "Buyer representation",
        "text": "Title checks, quota confirmation, developer due diligence and fee negotiation "
                "before you commit. Especially for a first purchase in Thailand.",
    },
]
