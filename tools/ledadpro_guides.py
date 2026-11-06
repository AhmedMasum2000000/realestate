"""LED AD PRO: search-led pages and the homepage FAQ.

Each page answers a search that Search Console shows ledadpro.com getting
impressions for without a page that fits (Nov 2026 audit, docs/seo-audit-2026-11-04.md):

  /pricing/                                  billboard advertising cost / price / rent in Bangladesh
  /led-screen-rental/                        LED screen rent, LED video wall rental, rental LED display
  /about/                                    advertising agency in Bangladesh (who we are, E-E-A-T)
  /guides/how-to-choose-a-billboard-location/  best / high-traffic / budget billboard location

Facts come only from data the site already publishes (screen counts, the indicative
rate ranges, clients, address). Called by ledadpro_build.main() with the build module.
"""
import re

# Indicative ranges already published on the area cost pages.
LED_RATE = '100 to 600 BDT per minute'
STATIC_RATE = '500 to 3,000 BDT per square foot'

HOME_FAQ = [
    ('How much does LED billboard advertising cost in Bangladesh?',
     f'LED billboard time is priced by screen, slots per hour and dates. LED AD PRO’s published guide puts it at about {LED_RATE}, with premium Dhaka junctions at the higher end. Static billboards are rented by size, at about {STATIC_RATE}. See the <a href="/pricing/">full pricing guide</a>.'),
    ('Where are your LED billboards?',
     'In {areas} areas: Dhaka (Gulshan, Banani, Dhanmondi, Mirpur, Mohakhali, Airport, Farmgate and more) and cities including Chattogram, Sylhet, Rajshahi, Cox’s Bazar, Bogura, Cumilla and Feni. Every screen is listed with a photo on the <a href="/locations/">locations page</a>.'),
    ('How quickly can my ad go live?',
     'Usually within days of confirming screens, dates and artwork in writing. There is nothing to print or install on an LED screen.'),
    ('What do I need to send for an LED billboard ad?',
     'A short video (MP4) or still image (JPG or PNG) made to each screen’s pixel size. We send the exact size, orientation and ad length with your quote. We can also design the ad for you.'),
    ('Do you rent LED screens for events?',
     'Yes: LED screens and video walls for events, launches and concerts, and an <a href="/services/led-caravan/">LED caravan</a> that takes a screen on the road. See <a href="/led-screen-rental/">LED screen rental</a>.'),
    ('How do I book?',
     'Call +880 1958-503753 or email info@ledadpro.com with your brand, areas, dates and budget. You get a shortlist of screens, availability and a written quote.'),
]


def plain(x):
    return re.sub('<[^>]+>', '', x)


def home_faq(b):
    """HTML section + FAQPage schema for the homepage (its own styles: the home uses style.css)."""
    n = len(b.LOCS)
    qas = [(q, a.replace('{areas}', str(n))) for q, a in HOME_FAQ]
    items = ''.join(f'<details class="hf-q"><summary>{b.e(q)}</summary><p>{a}</p></details>' for q, a in qas)
    css = ('<style>.hfaq{background:#fff;color:var(--ink);padding:clamp(60px,9vh,110px) 0}'
           '.hfaq h2{color:var(--pink);font-size:clamp(40px,6vw,96px);margin-bottom:28px}'
           '.hf-q{border-bottom:1px solid #dde3ee;padding:18px 0;max-width:980px}'
           '.hf-q summary{cursor:pointer;font:800 clamp(17px,1.5vw,21px)/1.35 var(--body);list-style:none}'
           '.hf-q summary::-webkit-details-marker{display:none}.hf-q summary::after{content:" +";color:var(--pink)}'
           '.hf-q[open] summary::after{content:" \\2013"}.hf-q p{margin-top:10px;color:#45516b;line-height:1.6;max-width:820px}'
           '.hf-q a{color:var(--pink-2);text-decoration:underline}</style>')
    html = (f'{css}<section class="hfaq" id="faq"><div class="wrap"><h2 class="display">Questions, answered</h2>{items}'
            f'<p style="margin-top:26px"><a class="more-link" href="/pricing/">Pricing guide <i>&#9656;</i></a></p></div></section>')
    return html, b.faq_ld(qas)


def faq_block(b, qas):
    return ''.join(f'<h2 class="q">{b.e(q)}</h2><p>{a}</p>' for q, a in qas)


def build_pricing(b):
    rows = ''.join(
        f'<tr><td><a href="/locations/{a["id"]}/advertising-cost/">{b.e(a["name"])}</a></td><td>{len(a["p"])}</td>'
        f'<td>{"Dhaka" if a["kind"] == "dhaka" else b.e(a["short"])}</td></tr>' for a in b.LOCS)
    total = sum(len(a['p']) for a in b.LOCS)
    qas = [
        ('How much does billboard advertising cost in Bangladesh?',
         f'An LED billboard costs about {LED_RATE} of airtime, depending on the screen, slots per hour and dates. A printed static billboard is rented at about {STATIC_RATE}, plus printing and installation. Your written quote confirms the current rate.'),
        ('What is the billboard rent in Dhaka?',
         f'Dhaka is the most expensive market, because its junctions carry the most traffic. Gulshan, Banani, Airport Road and Mohakhali sit at the top of the {LED_RATE} LED range; quieter roads cost less. Compare the <a href="/locations/">Dhaka locations</a>.'),
        ('Is an LED billboard cheaper than a static billboard?',
         'For a short campaign, usually yes: there is no printing or installation, you can start within days and change the ad mid-campaign. For a long booking on one site, a static billboard can cost less per day, but you share no time with other advertisers.'),
        ('What is the cheapest way to start?',
         'Book one well-placed LED screen for a short burst, or a few slots per hour across two or three screens in the same area. Ask for a package: several screens in one area are priced better than single bookings.'),
        ('Do prices include the design of the ad?',
         'Airtime and design are quoted separately. Sending a finished video or image costs nothing extra; we can also make it for you.'),
        ('Is VAT included?',
         'Your written quote states the taxes that apply. Ask for the total including VAT when you compare offers.'),
    ]
    body = f'''<section class="wrap prose"><p class="answer">Billboard advertising in Bangladesh costs about <strong>{LED_RATE}</strong> on an LED billboard, or about <strong>{STATIC_RATE}</strong> to rent a printed static billboard. The final price depends on the location, how often your ad plays, the campaign length and how many screens you book.</p>
<table class="facts wide"><tr><th>Format</th><th>How it is priced</th><th>Indicative range</th></tr>
<tr><td>LED billboard</td><td>Airtime: slots per hour × days, per screen</td><td>{LED_RATE}</td></tr>
<tr><td>Static billboard</td><td>Rent per square foot per month, plus printing and installation</td><td>{STATIC_RATE}</td></tr>
<tr><td>Metro Rail LED</td><td>Screens inside Dhaka Metro coaches, by package</td><td>On request · <a href="/services/metro-rail-led-advertising/">details</a></td></tr>
<tr><td>LED caravan / LED van</td><td>Per day, with route and driver</td><td>On request · <a href="/services/led-caravan/">details</a></td></tr>
<tr><td>LED screen rental (events)</td><td>Per day, by screen size, with setup</td><td>On request · <a href="/led-screen-rental/">details</a></td></tr></table>
<h2 class="display">What changes the price</h2>
<ul><li><b>Location:</b> busy Dhaka junctions such as Gulshan, Banani and Airport Road cost the most.</li>
<li><b>Slots per hour:</b> LED screens share time between advertisers; more plays means more people see you.</li>
<li><b>Length:</b> a month is priced better per day than a one-week burst.</li>
<li><b>Number of screens:</b> packages across one area or several cities are priced as a package.</li>
<li><b>Creative:</b> bringing a finished file costs nothing; design and animation are quoted separately.</li></ul>
<h2 class="display">Cost by area</h2><p>{total} LED screens in {len(b.LOCS)} areas. Each area has its own cost guide.</p>
<table class="facts wide"><tr><th>Area</th><th>LED screens</th><th>City</th></tr>{rows}</table>
<h2 class="display">Questions about price</h2>{faq_block(b, qas)}</section>'''
    offer = {'@type': 'Service', 'name': 'LED billboard advertising in Bangladesh', 'serviceType': 'Digital out-of-home advertising',
             'provider': {'@id': b.SITE + '/#business'}, 'areaServed': {'@type': 'Country', 'name': 'Bangladesh'},
             'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'BDT', 'lowPrice': 100, 'highPrice': 600,
                        'description': 'Indicative LED billboard airtime per minute; the written quote confirms the rate.'}}
    b.page('/pricing/', 'Billboard Advertising Cost in Bangladesh (2026 Price Guide) | LED AD PRO',
           f'Billboard advertising cost in Bangladesh: LED billboards from about {LED_RATE}, static billboard rent {STATIC_RATE}. Prices by area, what changes them, and how to get a quote.',
           'Billboard advertising cost in Bangladesh', body, [('Home', '/'), ('Pricing', '/pricing/')],
           (b.org(), offer, b.faq_ld([(q, plain(a)) for q, a in qas])))


def build_rental(b):
    steps = [('Tell us the event', 'Date, venue, indoor or outdoor, audience size and what will play on the screen.'),
             ('Get a screen proposal', 'We suggest the screen size and layout for the venue and viewing distance, with a written quote.'),
             ('Setup and testing', 'Our crew delivers, builds and tests the screen before your event starts.'),
             ('Run the show', 'An operator plays your content during the event and handles changes on the day.'),
             ('Take-down', 'We dismantle and remove the screen after the event.')]
    qas = [('How much does it cost to rent an LED screen in Bangladesh?',
            'LED screen rental is priced per day by screen size, indoor or outdoor use, setup and the operator. Send the date, venue and the size you have in mind for a written quote.'),
           ('What size LED screen do I need?',
            'It depends on how far the audience sits from the screen and the size of the venue. Tell us the venue and audience size and we propose a size and layout.'),
           ('Do you provide outdoor LED screens?',
            'Yes: outdoor screens for concerts, fairs and launches, and the LED caravan, a vehicle with a large screen that can move between locations.'),
           ('Is an operator included?', 'Yes. Delivery, setup, testing, an operator during the event and take-down are part of the rental.'),
           ('Can you rent a screen outside Dhaka?', 'Yes. Tell us the city and venue; transport is included in the quote.')]
    body = f'''<section class="wrap prose"><p class="answer">LED AD PRO rents <strong>LED screens and LED video walls</strong> for events, product launches, concerts, conferences and fairs in Dhaka and across Bangladesh. The rental includes delivery, setup, testing, an operator during the event and take-down. For a screen that moves between locations, see the <a href="/services/led-caravan/">LED caravan</a>.</p>
<h2 class="display">What you can rent</h2><ul class="ticks"><li>Indoor LED video walls for stages, conferences and exhibitions</li><li>Outdoor LED screens for concerts, fairs and launches</li><li>LED caravan: a mobile LED screen van for roadshows and district tours</li><li>Custom LED displays for shops and showrooms</li></ul>
<h2 class="display">How it works</h2><ol class="steps">{''.join(f'<li><b>{b.e(t)}</b><p>{b.e(d)}</p></li>' for t, d in steps)}</ol>
<h2 class="display">Questions answered</h2>{faq_block(b, qas)}
<p>Also see: <a href="/pricing/">advertising prices</a> · <a href="/services/led-caravan/">LED caravan</a> · <a href="/clients/">our clients</a></p></section>'''
    svc = {'@type': 'Service', 'name': 'LED screen rental', 'serviceType': 'LED screen and video wall rental',
           'provider': {'@id': b.SITE + '/#business'}, 'areaServed': {'@type': 'Country', 'name': 'Bangladesh'}}
    howto = {'@type': 'HowTo', 'name': 'How to rent an LED screen for an event', 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': t, 'text': d} for i, (t, d) in enumerate(steps)]}
    b.page('/led-screen-rental/', 'LED Screen Rental in Bangladesh: LED Video Walls for Events | LED AD PRO',
           'Rent an LED screen or LED video wall for events, launches and concerts in Dhaka and across Bangladesh. Delivery, setup, operator and take-down included.',
           'LED screen rental in Bangladesh', body, [('Home', '/'), ('LED screen rental', '/led-screen-rental/')], (b.org(), svc, howto, b.faq_ld(qas)))


def build_about(b):
    total = sum(len(a['p']) for a in b.LOCS)
    cities = sorted({('Dhaka' if a['kind'] == 'dhaka' else a['short']) for a in b.LOCS})
    body = f'''<section class="wrap prose"><p class="answer">LED AD PRO is a <strong>digital out-of-home advertising company in Bangladesh</strong>, based in Gulshan 1, Dhaka. We sell airtime on <strong>{total} LED billboard screens in {len(b.LOCS)} areas</strong>, rent LED screens for events, run the LED caravan and sell Metro Rail LED advertising. LED AD PRO is the official LED partner to AD Pro, whose team has delivered campaigns for 400+ brands.</p>
<div class="stats"><div><b>{total}</b><span>LED screens</span></div><div><b>{len(b.LOCS)}</b><span>areas</span></div><div><b>{len(cities)}</b><span>cities</span></div><div><b>400+</b><span>brands served by our team</span></div></div>
<h2 class="display">What we do</h2><ul class="ticks"><li><a href="/locations/">LED billboards</a> in {b.e(", ".join(cities))}</li><li><a href="/services/metro-rail-led-advertising/">Metro Rail LED</a> screens inside Dhaka Metro coaches</li><li><a href="/services/led-caravan/">LED caravan</a> mobile screens for roadshows</li><li><a href="/led-screen-rental/">LED screen rental</a> for events</li><li>Static billboards, custom LED displays and store-launch branding</li></ul>
<h2 class="display">How we work</h2><ul><li><b>Real photos of every screen:</b> each location page shows the screen and the road it faces, so you know what you are buying.</li><li><b>Written quotes:</b> screens, slots, dates and total in writing before anything runs.</li><li><b>Proof of display:</b> photos or video of your ad running on each screen.</li><li><b>One team, end to end:</b> planning, creative specification, booking and reporting.</li></ul>
<h2 class="display">Brands our team has delivered for</h2>{b.client_wall()}
<h2 class="display">Visit or call</h2><p>{b.e(b.ADDRESS)}<br>Sales and marketing <a href="tel:{b.PHONE}">{b.PHONE_TXT}</a> · Office <a href="tel:{b.OFFICE}">{b.OFFICE_TXT}</a> · <a href="mailto:{b.EMAIL}">{b.EMAIL}</a><br>Saturday to Thursday 9am–8pm · Friday 10am–12pm</p></section>'''
    about = {'@type': 'AboutPage', 'name': 'About LED AD PRO', 'url': b.SITE + '/about/', 'mainEntity': {'@id': b.SITE + '/#business'}}
    b.page('/about/', 'About LED AD PRO: LED & Outdoor Advertising Company in Bangladesh',
           f'LED AD PRO is a digital out-of-home advertising company in Dhaka: {total} LED screens in {len(b.LOCS)} areas, event LED rental, LED caravan and Metro Rail LED. Official LED partner to AD Pro.',
           'About LED AD PRO', body, [('Home', '/'), ('About', '/about/')], (b.org(), about))


def build_location_guide(b):
    path = '/guides/how-to-choose-a-billboard-location/'
    steps = [('Start from your customer’s journey', 'List the roads your customers use to reach you or your shops. A screen only works for traffic coming towards it, so the facing matters more than the area name.'),
             ('Pick the junction type', 'Signals and slow junctions give people longer to read; fast flyovers suit a logo and one word.'),
             ('Check the audience', 'Office districts (Gulshan, Banani, Motijheel) reach professionals on weekdays; shopping areas (Dhanmondi, New Market) reach families and students; airports and highways reach travellers.'),
             ('Match the budget', 'For a small budget, choose one screen on the right road and run it longer, rather than many screens for a few days.'),
             ('Ask for a current photo', 'Surroundings change: trees, new buildings or other billboards can block a view. Ask for a recent photo or video before you book.'),
             ('Measure the result', 'Use a dedicated phone number, a short web address or an offer code on the ad, so you can count the response.')]
    qas = [('What is the best location for a billboard in Dhaka?',
            'The one on the road your customers use, facing their direction of travel. For broad reach, the busiest junctions in Gulshan, Banani, Airport Road, Mohakhali and Farmgate carry the most traffic.'),
           ('What makes a high-traffic billboard location?',
            'Daily vehicle and foot traffic, slow-moving or stopped traffic at signals, a clear line of sight from far away, and few competing signs nearby.'),
           ('What are budget-friendly billboard options?',
            'An LED screen with fewer slots per hour, one well-placed screen for a longer period, a package in one area, or a city outside Dhaka where rates are lower.'),
           ('LED or static billboard?',
            'LED suits short campaigns, launches and changing offers, with no printing. Static suits long, single-site campaigns where you want the full face to yourself.')]
    howto = {'@type': 'HowTo', 'name': 'How to choose a billboard location', 'step': [{'@type': 'HowToStep', 'position': i + 1, 'name': t, 'text': d} for i, (t, d) in enumerate(steps)]}
    article = {'@type': 'Article', 'headline': 'How to choose the best billboard location', 'author': {'@id': b.SITE + '/#business'},
               'publisher': {'@id': b.SITE + '/#business'}, 'datePublished': b.TODAY, 'dateModified': b.TODAY, 'mainEntityOfPage': b.SITE + path}
    body = f'''<section class="wrap prose"><p class="answer">The best billboard location is the one your customers pass on their way to you, <strong>facing their direction of travel</strong>, at a junction slow enough to read the ad. Check the audience, match the screen to your budget and ask for a current photo before you book.</p>
<ol class="steps">{''.join(f'<li><b>{b.e(t)}</b><p>{b.e(d)}</p></li>' for t, d in steps)}</ol>
<h2 class="display">Questions answered</h2>{faq_block(b, qas)}
<p>Next: <a href="/locations/">browse every location with photos</a> · <a href="/pricing/">see prices</a></p></section>'''
    b.page(path, 'How to Choose the Best Billboard Location (Bangladesh Guide) | LED AD PRO',
           'How to pick a high-traffic, budget-friendly billboard location in Dhaka and Bangladesh: journeys, facing, junctions, audience, budget and measuring results.',
           'How to choose the best billboard location', body, [('Home', '/'), ('Choosing a billboard location', path)], (b.org(), article, howto, b.faq_ld(qas)))


def build(b):
    build_pricing(b)
    build_rental(b)
    build_about(b)
    build_location_guide(b)
