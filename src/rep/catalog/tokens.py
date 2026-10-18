"""Brand tokens for Pattaya Home Pro.

The reference site's design language is kept intact — oversized uppercase
display type, hard-edged full-bleed colour blocks, flat cards, wide gutters.
Only the palette changes: its violet/lavender becomes the logo's navy/gold.
"""

BRAND = {
    "name": "Pattaya Home Pro",
    "tagline": "Tropical Living & Investment",
    "domain": "pattayahomepro.com",
    "phone_display": "+66 95 348 3725",
    "phone_href": "+66953483725",
    "email": "hello@pattayahomepro.com",
    "address_street": "21/78 Moo.5 Nongprue",
    "address_locality": "Banglamung",
    "address_region": "Chonburi",
    "address_postal": "20180",
    "address_country": "TH",
}

PALETTE = {
    # Navy carries the role the reference gives its violet: full-bleed blocks,
    # display headings, footer ground.
    "navy": "#16244C",
    "navy_2": "#1E3266",
    "navy_3": "#0E1734",
    # Gold carries the role of its yellow: the oversized footer CTA and accents.
    "gold": "#C9A86E",
    "gold_2": "#DCC08E",
    "gold_3": "#A8874D",
    "ink": "#0E1526",
    "ink_2": "#3A4560",
    "muted": "#6B7590",
    "paper": "#FFFFFF",
    "paper_2": "#F4F2ED",
    "paper_3": "#E8E4DA",
    "rule": "#D8D3C7",
}

FONTS = {
    # Archivo stands in for the reference's Blauer Nue: a wide grotesque that
    # holds up at display sizes. Rubik is what the reference itself uses.
    "display": "Archivo",
    "body": "Rubik",
    "display_stack": "'Archivo', 'Helvetica Neue', Arial, sans-serif",
    "body_stack": "'Rubik', system-ui, -apple-system, sans-serif",
    "google_href": (
        "https://fonts.googleapis.com/css2"
        "?family=Archivo:wght@500;600;700;800"
        "&family=Rubik:wght@300;400;500;600"
        "&display=swap"
    ),
}


def context() -> dict:
    return {"brand": BRAND, "palette": PALETTE, "fonts": FONTS}
