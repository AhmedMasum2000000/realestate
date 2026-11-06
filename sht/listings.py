"""Property listings for Second Home Thailand.

Listings come from the shared catalogue (data/catalog.json, the Casa Pattaya export also used by
Pattaya Home Pro) and the photo enrichment (data/enrichment.json). Only residential homes for sale
or rent that have a photograph get a page. Every sentence is written here from the listing's own
facts, its area and its type; no marketing copy is taken from the source listing.
"""
from __future__ import annotations

import glob
import hashlib
import json
import re
import statistics
import subprocess
from datetime import date
from pathlib import Path

TYPES = {  # catalogue type -> (singular, plural, schema.org type)
    'Condo': ('condo', 'condos', 'Apartment'),
    'Apartment': ('apartment', 'apartments', 'Apartment'),
    'House': ('house', 'houses', 'SingleFamilyResidence'),
    'Pool Villa': ('pool villa', 'pool villas', 'SingleFamilyResidence'),
    'Townhouse': ('townhouse', 'townhouses', 'House'),
}
DEALS = {'sale': 'for sale', 'rent': 'for rent'}

# Neighbourhoods, in plain words. Where it is, what it is like, who tends to choose it.
AREAS = {
    'jomtien': ('Jomtien', 'Jomtien runs along a long, straight beach just south of Pattaya city. It is mostly condominiums along and behind Beach Road, with a slower pace than central Pattaya, plenty of everyday restaurants and a large long-stay community.'),
    'east-pattaya': ('East Pattaya', 'East Pattaya is the inland side of Sukhumvit Road. It is where most houses and pool villas are, often in gated estates with more space and lower prices than the coast, a short drive from the beaches, international schools and hospitals.'),
    'pratumnak': ('Pratumnak', 'Pratumnak is the green hill between Pattaya and Jomtien. Quieter streets, small beaches such as Cosy Beach and some of the area’s better-regarded condominiums make it popular with people who want calm within minutes of the city.'),
    'north-pattaya': ('North Pattaya', 'North Pattaya covers Naklua and Wongamat, where high-rise beachfront condominiums face a quieter bay. It is close to the city, shopping and the main hospitals, with a more residential feel than the centre.'),
    'central-pattaya': ('Central Pattaya', 'Central Pattaya is the city centre around Beach Road, Second Road and the large shopping malls. Everything is walkable, which suits people who want shops, restaurants and transport on the doorstep rather than space.'),
    'south-pattaya': ('South Pattaya', 'South Pattaya is the busy end of the city near Bali Hai pier and Walking Street. Condominiums here suit people who want city life and easy ferries to Koh Larn more than quiet evenings.'),
    'na-jomtien': ('Na Jomtien', 'Na Jomtien continues south from Jomtien along a quieter coastline, with low-density beachfront condominiums, resorts and a marina. It suits people who want the sea with fewer crowds, a short drive from Jomtien.'),
    'huay-yai': ('Huay Yai', 'Huay Yai lies south-east of Pattaya, inland and rural in feel. Large plots, newer pool-villa estates and lower prices attract buyers who want space and are happy to drive.'),
    'mabprachan': ('Mabprachan', 'Mabprachan surrounds the reservoir east of Pattaya. Detached houses and pool villas on larger plots, lake views and quiet roads make it a long-standing choice for families and retirees.'),
    'thepprasit': ('Thepprasit', 'Thepprasit is the road linking Sukhumvit with Jomtien, known for its weekend night market. Homes here are between the beach and the inland estates, convenient for both.'),
    'nong-pla-lai': ('Nong Pla Lai', 'Nong Pla Lai is an inland district east of Pattaya with houses on bigger plots and a local Thai neighbourhood feel, further from the beach and lower in price.'),
    'bang-saray': ('Bang Saray', 'Bang Saray is a former fishing village south of Pattaya, with a quiet seafront, seafood restaurants and a relaxed pace about 25 minutes from the city.'),
    'sattahip': ('Sattahip', 'Sattahip is the coastal district at the southern end of the Pattaya area, with quiet beaches and a naval town feel, suited to people who want distance from the city.'),
}
DEFAULT_AREA = 'Pattaya, on Thailand’s eastern seaboard, mixes beach condominiums near the coast with houses and pool villas inland, about 90 minutes from Bangkok’s Suvarnabhumi airport.'

MIN_HUB = 5  # a hub page is only built when it has at least this many homes


def money(value, deal):
    text = '฿{:,.0f}'.format(value)
    return text + ' a month' if deal == 'rent' else text


def short_money(value):
    if value >= 1_000_000:
        return '฿{:.1f}M'.format(value / 1_000_000).replace('.0M', 'M')
    if value >= 1_000:
        return '฿{:.0f}K'.format(value / 1_000)
    return '฿{:,.0f}'.format(value)


def clean_project(project, area_name):
    """The building or estate name, or nothing. Sales phrases in the source field are dropped."""
    name = re.sub(r'\s*\(.*?\)', '', project or '')
    if re.search(r'(?i)\bfor (sale|rent)\b', name):
        name = re.split(r'(?i)\bfor (?:sale|rent)\b\s*(?:at|in|[-—–])?\s*', name)[-1]
    name = re.sub(r'(?i)\s*[-—–]?\s*\d+\s*bedrooms?.*$', '', name).strip(' -—–,.')
    words = name.split()
    if (not name or len(name) > 48 or len(words) > 6 or ',' in name or not name[0].isupper()
            or name.lower() == area_name.lower() or re.search(r'(?i)\b(luxury|renovated|tenant|pet-friendly|sea view|brand new|cheap|bargain)\b', name)):
        return ''
    return name


def beds_label(beds):
    if beds is None:
        return ''
    return 'studio' if beds == 0 else f'{beds}-bedroom'


def months_between(day, today):
    return (today.year - day.year) * 12 + today.month - day.month


def load(root: Path, today: date):
    catalog = json.loads((root/'data'/'catalog.json').read_text())['listings']
    enrichment = json.loads((root/'data'/'enrichment.json').read_text())['listings']
    homes = []
    for row in catalog:
        if row['type'] not in TYPES or row['deal'] not in DEALS or row['reference'] not in enrichment:
            continue
        source = sorted(glob.glob(str(root/'assets'/'properties'/row['reference']/'hero.*')))
        if not source or not row.get('price_thb'):
            continue
        singular, plural, schema_type = TYPES[row['type']]
        area_slug = row['location_slug']
        area_name = AREAS.get(area_slug, (row['location'], ''))[0]
        beds = row['bedrooms']
        ref = row['reference']
        project = clean_project(row['project'], area_name)
        bed = beds_label(beds)
        headline = ' '.join(x for x in (bed, singular) if x)
        slug = '-'.join(x for x in (bed.replace('studio', 'studio'), singular.replace(' ', '-'), DEALS[row['deal']].replace(' ', '-'), area_slug, ref.lower()) if x)
        updated = date.fromisoformat(row['last_update'])
        homes.append({
            'ref': ref, 'slug': 'properties/' + slug, 'deal': row['deal'], 'deal_label': DEALS[row['deal']], 'type': row['type'],
            'singular': singular, 'plural': plural, 'schema_type': schema_type, 'type_slug': plural.replace(' ', '-'),
            'area': area_name, 'area_slug': area_slug, 'beds': beds, 'baths': row['bathrooms'], 'bed_label': bed,
            'price': row['price_thb'], 'price_text': money(row['price_thb'], row['deal']), 'price_short': short_money(row['price_thb']),
            'project': project, 'headline': headline, 'source_title': row['title'], 'updated': updated, 'stale': months_between(updated, today) >= 9,
            'image_source': source[0],
        })
    homes.sort(key=lambda h: (h['updated'], h['ref']), reverse=True)
    seen = set()
    for home in homes:
        if home['slug'] in seen:
            raise SystemExit('Duplicate listing slug ' + home['slug'])
        seen.add(home['slug'])
        write_copy(home)
    return homes


def persona(home):
    beds, kind = home['beds'] or 0, home['type']
    if home['deal'] == 'rent':
        base = 'a first year in the area before you decide where to buy'
    elif kind in ('Condo', 'Apartment'):
        base = 'a lock-up-and-leave base for part-year living'
    else:
        base = 'full-time living with room for visiting family'
    if kind in ('Condo', 'Apartment'):
        who = 'one person or a couple' if beds <= 1 else 'a couple who want a guest room or a home office' if beds == 2 else 'a family, or friends sharing'
    elif kind == 'Pool Villa':
        who = 'people who want private outdoor living and a pool of their own'
    else:
        who = 'a family or long-stay retirees who want space' if beds >= 3 else 'a couple who want a house rather than a condominium'
    return f'It suits {who}, and works well as {base}.'


def ownership(home):
    if home['deal'] == 'rent':
        return ('Renting needs no ownership checks. Agree the deposit, the electricity and water rates and the notice period in writing, '
                'and make sure your landlord files the TM30 notification of your address with immigration, which you will need for visa extensions.')
    if home['type'] in ('Condo', 'Apartment'):
        return ('A foreigner can own a condominium unit freehold in their own name, provided the building’s foreign quota (up to 49% of the total floor area of all units) still has room '
                'and the purchase money arrives from abroad in foreign currency, documented by the receiving bank. We confirm the quota for this building before you reserve.')
    return ('Foreigners generally cannot own land in their own name in Thailand. Common lawful routes for a house are a registered lease of the land (up to 30 years) '
            'while owning the building itself, or a purchase by a Thai spouse. Avoid nominee company structures, and take independent legal advice before you sign.')


def costs(home):
    if home['deal'] == 'rent':
        return ('Long-term leases in Pattaya commonly ask for a two-month security deposit plus the first month’s rent in advance. '
                'Electricity is usually billed by the landlord or the building, so ask for the unit rate before you sign.')
    return ('Budget for transfer costs at the Land Office: the transfer fee and, depending on the seller and how long they have owned the property, '
            'specific business tax or stamp duty and withholding tax. Who pays which is agreed in the sale contract, so read it before paying a deposit.')


def write_copy(home):
    area_name, deal = home['area'], home['deal']
    at = f" at {home['project']}" if home['project'] else ''
    where = area_name if home['project'] and area_name.lower() in home['project'].lower() else f'{area_name}, Pattaya'
    h1 = f"{home['headline'].capitalize()} {home['deal_label']} in {area_name}"
    home['h1'] = h1
    baths = f", {home['baths']} {'bathroom' if home['baths'] == 1 else 'bathrooms'}" if home['baths'] else ''
    title_core = f"{home['bed_label'].replace('-bedroom', '-Bed').title() + ' ' if home['bed_label'] else ''}{home['singular'].title()} {home['deal_label']}"
    price = home['price_text'].replace(' a month', '/mo')
    place = home['project'] if home['project'] and area_name.lower() in home['project'].lower() else ', '.join(x for x in (home['project'], area_name) if x)
    title = f"{title_core}, {place} – {price}"
    home['title'] = title + f" | {home['ref']}" if len(title) <= 62 else title
    home['description'] = (f"{home['headline'].capitalize()}{baths} {home['deal_label']}{at} in {area_name}, Pattaya: {home['price_text']}. "
                           f"Ref {home['ref']}. What foreigners can own, the visa side and a viewing, arranged by Second Home Thailand.")[:300]
    home['summary'] = (f"{home['ref']} is a {home['headline']}{baths} {home['deal_label']}{at} in {where}, listed at {home['price_text']}. "
                       f"{persona(home)} The listing was last updated by the agent on {home['updated'].strftime('%-d %B %Y')}; "
                       'we confirm availability and price with the agent before any viewing.')
    home['ownership'] = ownership(home)
    home['costs'] = costs(home)
    home['area_text'] = AREAS.get(home['area_slug'], ('', DEFAULT_AREA))[1] or DEFAULT_AREA
    noun = 'buy' if deal == 'sale' else 'rent'
    home['faqs'] = [
        (f"Is {home['ref']} still available?", 'Availability and price change often. Ask about this home and we check with the listing agent first, then suggest similar homes if it has gone.'),
        (f"Can a foreigner {noun} this {home['singular']}?", home['ownership']),
        ('Does owning or renting a home in Thailand give me a visa?', 'No. A home does not come with a visa. Long-stay residents usually pair their home with a retirement visa (age 50+), the Long-Term Resident visa, Thailand Privilege membership or the Destination Thailand Visa.'),
        ('Can I arrange a viewing from abroad?', 'Yes. Tell us your dates and we arrange an in-person viewing, or a video walk-through where the agent can offer one, so you only travel for homes worth seeing.'),
    ]
    home['message'] = f"I would like details and a viewing for {home['ref']}: the {home['headline']} {home['deal_label']} in {area_name}{at} ({home['price_text']})."


def hub_key(area=None, type_slug=None, deal=None):
    parts = ['properties']
    if area:
        parts.append(area)
    if type_slug and deal:
        parts.append(f"{type_slug}-{DEALS[deal].replace(' ', '-')}")
    elif deal:
        parts.append(DEALS[deal].replace(' ', '-'))
    return '/'.join(parts)


def price_stats(homes, deal):
    prices = sorted(h['price'] for h in homes if h['deal'] == deal)
    if not prices:
        return None
    return {'count': len(prices), 'low': prices[0], 'high': prices[-1], 'median': statistics.median(prices), 'deal': deal}


def stats_sentence(homes, label, deal, when):
    s = price_stats(homes, deal)
    if not s:
        return ''
    unit = ' a month' if deal == 'rent' else ''
    return (f"Across the {s['count']} {label} {DEALS[deal]} on this page, asking prices run from {money(s['low'], 'sale')} to {money(s['high'], 'sale')}{unit}, "
            f"with a median of {money(s['median'], 'sale')}{unit} (listing data updated {when}).")


def build_hubs(homes, when):
    """Every hub with at least MIN_HUB homes: all homes, deal, type×deal, area, area×type×deal."""
    groups = {}
    def add(key, **meta):
        groups.setdefault(key, {'key': key, 'homes': [], **meta})
    for h in homes:
        for key, meta in (
            (hub_key(), {'kind': 'all'}),
            (hub_key(deal=h['deal']), {'kind': 'deal', 'deal': h['deal']}),
            (hub_key(type_slug=h['type_slug'], deal=h['deal']), {'kind': 'type', 'deal': h['deal'], 'type_slug': h['type_slug'], 'plural': h['plural']}),
            (hub_key(area=h['area_slug']), {'kind': 'area', 'area': h['area'], 'area_slug': h['area_slug']}),
            (hub_key(area=h['area_slug'], type_slug=h['type_slug'], deal=h['deal']), {'kind': 'area-type', 'area': h['area'], 'area_slug': h['area_slug'], 'deal': h['deal'], 'type_slug': h['type_slug'], 'plural': h['plural']}),
        ):
            add(key, **meta)
            groups[key]['homes'].append(h)
    hubs = {k: g for k, g in groups.items() if len(g['homes']) >= MIN_HUB or g['kind'] == 'all'}
    for hub in hubs.values():
        write_hub(hub, when)
    for h in homes:
        h['hubs'] = [k for k in (hub_key(area=h['area_slug'], type_slug=h['type_slug'], deal=h['deal']), hub_key(area=h['area_slug']), hub_key(type_slug=h['type_slug'], deal=h['deal']), hub_key(deal=h['deal'])) if k in hubs]
        h['area_hub'] = hub_key(area=h['area_slug']) if hub_key(area=h['area_slug']) in hubs else 'properties'
        h['crumb'] = next((k for k in (hub_key(area=h['area_slug']), hub_key(deal=h['deal'])) if k in hubs), 'properties')
        h['similar'] = similar(h, homes)
    return hubs


def similar(home, homes):
    def score(other):
        return (other['area_slug'] != home['area_slug']) * 2 + (other['type'] != home['type']) + abs(other['price'] - home['price']) / max(home['price'], 1)
    pool = [o for o in homes if o is not home and o['deal'] == home['deal']]
    return sorted(pool, key=score)[:6]


def write_hub(hub, when):
    kind, homes = hub['kind'], hub['homes']
    area, deal = hub.get('area'), hub.get('deal')
    plural = hub.get('plural', 'homes')
    if kind == 'all':
        heading, title = 'Homes for your second life in Thailand', 'Pattaya Homes for Sale & Rent for Long-Stay Foreigners | Second Home Thailand'
        lead = 'Condominiums, houses and pool villas in and around Pattaya, chosen for people making Thailand a second home. Each listing explains what a foreigner can own, the visa side and the next step.'
    elif kind == 'deal':
        heading = f"Homes {DEALS[deal]} in Pattaya"
        title = f"Pattaya Homes {DEALS[deal].title()}: Condos, Houses & Pool Villas | Second Home Thailand"
        lead = ('Buy with the ownership questions answered first: condominium quotas, land leases and the transfer costs at the Land Office.' if deal == 'sale'
                else 'Rent first and learn the area before you buy. Long-term leases with the TM30, deposit and notice terms explained.')
    elif kind == 'type':
        heading = f"{plural.capitalize()} {DEALS[deal]} in Pattaya"
        title = f"{plural.title()} {DEALS[deal].title()} in Pattaya for Foreigners | Second Home Thailand"
        lead = f"{plural.capitalize()} {DEALS[deal]} across Pattaya, Jomtien and the inland estates, with what a foreigner can own and what it costs to move in."
    elif kind == 'area':
        heading = f"Homes in {area}"
        title = f"{area} Property for Sale & Rent: Condos, Houses, Villas | Second Home Thailand"
        lead = AREAS.get(hub['area_slug'], ('', DEFAULT_AREA))[1] or DEFAULT_AREA
    else:
        heading = f"{plural.capitalize()} {DEALS[deal]} in {area}"
        title = f"{area} {plural.title()} {DEALS[deal].title()} | Prices & Foreign Ownership | Second Home Thailand"
        lead = AREAS.get(hub['area_slug'], ('', DEFAULT_AREA))[1] or DEFAULT_AREA
    hub['crumb'] = {'all': 'Properties', 'deal': DEALS.get(deal, '').capitalize(), 'type': heading.replace(' in Pattaya', ''), 'area': area}.get(kind) or f"{plural.capitalize()} {DEALS[deal]}"
    label = plural if kind in ('type', 'area-type') else 'homes'
    place = f' in {area}' if area else ' in Pattaya'
    facts = [stats_sentence(homes, label, d, when) for d in (('sale', 'rent') if not deal else (deal,))]
    facts = [f for f in facts if f]
    hub.update(heading=heading, title=title, lead=lead, facts=facts,
               description=(f"{len(homes)} {label} {DEALS[deal] if deal else 'for sale and rent'}{place}. " + (facts[0] if facts else ''))[:300])
    faqs = []
    for d in (('sale', 'rent') if not deal else (deal,)):
        s = price_stats(homes, d)
        if s:
            faqs.append((f"How much does a {plural[:-1] if plural.endswith('s') else plural} {DEALS[d]}{place} cost?", stats_sentence(homes, label, d, when) + ' Asking prices are a starting point, not a valuation.'))
    if deal != 'rent':
        faqs.append((f"Can foreigners buy property{place}?", 'Yes, a condominium unit can be owned freehold in a foreigner’s own name within the building’s 49% foreign quota, with the money sent from abroad. Land cannot generally be owned by a foreigner, so houses are usually held through a registered land lease of up to 30 years or bought by a Thai spouse.'))
    if deal != 'sale':
        faqs.append((f"What do I need to rent long term{place}?", 'Your passport, a deposit (often two months) and the first month’s rent. Your landlord should file the TM30 notification of your address, which immigration asks for at extensions and 90-day reports.'))
    faqs.append(('Does buying a home in Thailand give me a visa?', 'No. Owning or renting a home does not come with a visa. Most long-stay owners pair their home with a retirement visa, the Long-Term Resident visa, Thailand Privilege or the Destination Thailand Visa.'))
    faqs.append(('Can you help me view homes from abroad?', 'Yes. We check availability with the listing agent, arrange in-person viewings around your dates, or a video walk-through where possible, and coordinate the visa and arrival around the move.'))
    hub['faqs'] = faqs


def prepare_images(homes, out: Path, cache: Path):
    """Two sizes per photo, made once and cached: 1000px for the listing page, 480px for cards."""
    out.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    for home in homes:
        src = Path(home['image_source'])
        digest = hashlib.sha1(src.read_bytes()).hexdigest()[:12]
        for width in (1000, 480):
            name = f"{home['ref'].lower()}-{width}.webp"
            cached = cache/f"{digest}-{width}.webp"
            if not cached.is_file():
                subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(src), '-vf', f"scale='min({width},iw)':-2:flags=lanczos", '-quality', '74', '-compression_level', '6', str(cached)], check=True)
            (out/name).write_bytes(cached.read_bytes())
        probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(out/f"{home['ref'].lower()}-1000.webp")], capture_output=True, text=True, check=True).stdout.strip().split(',')
        home['img_w'], home['img_h'] = int(probe[0]), int(probe[1])
        home['image'] = f"listings/{home['ref'].lower()}-1000.webp"
        home['thumb'] = f"listings/{home['ref'].lower()}-480.webp"
