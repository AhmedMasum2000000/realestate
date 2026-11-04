"""Extra LED AD PRO pages: services (Metro Rail LED, LED Caravan) and Our Clients.
Client names come from the founder's own client history (AD Pro / LED AD PRO campaigns);
campaign photos are from the APCL client footage folder."""

CLIENTS = ['BMW', 'Emirates', 'Malaysia Airlines', 'Aarong', 'Royal Enfield', 'Bangladesh Armed Forces', 'Haier',
           'Singer Beko', 'ACI', 'New Zealand Dairy', 'Mediacom', 'Paramount', 'Aziz & Company', 'Mega Builders',
           'IFY Shop', 'Sencillo', 'Study in Bangladesh']

CASES = [  # (image under img/work, brand, what we did, where)
    ('royal-enfield-gulshan-2.jpg', 'Royal Enfield', 'Bullet 350 launch on LED billboards, 7 boards', 'Gulshan Circle-2, Dhaka'),
    ('haier-gulshan-2.jpg', 'Haier', 'LED billboard campaign', 'Gulshan-2, Dhaka'),
    ('aarong-noakhali.jpg', 'Aarong', 'Store launch branding and illuminated signage', 'Noakhali'),
    ('aarong-kushtia.jpg', 'Aarong', 'Billboard campaign', 'Kushtia'),
]

SERVICES = {
 'metro-rail-led-advertising': dict(
    name='Metro Rail LED Advertising', short='Metro Rail LED', img='img/svc/metro-train-interior.webp', img2='img/svc/metro-line-1200.webp',
    title='Metro Rail LED Advertising in Dhaka (In-Coach Screens) | LED AD PRO',
    desc='Advertise on digital screens inside Dhaka Metro Rail coaches. Reach daily commuters on MRT Line-6 with short video ads. Plan, specs and booking with LED AD PRO.',
    answer='Metro Rail LED advertising puts your video ad on the <strong>digital screens inside Dhaka Metro Rail coaches</strong>, where commuters ride the same route every day. It suits brands that want repeated, seated attention from office workers, students and families travelling between Uttara and Motijheel.',
    who=['Office workers commuting to Motijheel, Karwan Bazar and Farmgate', 'University students along the line', 'Shoppers and families travelling across the city'],
    how=[('Pick dates and coverage', 'Choose the campaign weeks and how many coaches or plays you need.'),
         ('Get the specification', 'Confirm screen size, ad length, file format and play frequency in writing.'),
         ('Make the creative', 'Short, silent-friendly video: brand in the first second, large text, one message.'),
         ('Go live and get proof', 'Approve the schedule; receive photos or video of your ad running in the coaches.')],
    faq=[('What is metro rail LED advertising?', 'Video ads played on the digital screens inside metro coaches in Dhaka, seen by passengers during their ride.'),
         ('Which metro line can I advertise on?', 'Dhaka Metro Rail MRT Line-6, which runs between Uttara and Motijheel. Current screen coverage is confirmed when you enquire.'),
         ('How long should a metro ad be?', 'Keep it short, usually 10 to 15 seconds, and make it work without sound: passengers often watch without audio.'),
         ('Can I combine metro with LED billboards?', 'Yes. Pairing in-coach screens with roadside LED billboards near stations such as Farmgate, Karwan Bazar and Mirpur-10 repeats your message on the same journey.'),
         ('How do I book?', 'Call +880 1316-743003 or email info@ledadpro.com with your dates and budget for availability and a written quote.')]),
 'led-caravan': dict(
    name='LED Caravan (Mobile LED Screen Van)', short='LED Caravan', img='img/event-stage-night-2400.webp', img2=None,
    title='LED Caravan Advertising in Bangladesh (Mobile LED Screen Van) | LED AD PRO',
    desc='Take your ad to the people with an LED caravan: a vehicle with a large LED screen for roadshows, launches, events and district tours across Bangladesh. LED AD PRO.',
    answer='An LED caravan is a <strong>vehicle carrying a large LED screen</strong> that brings your ad to the audience: it drives planned routes, parks at markets, campuses and events, and plays video with sound. It reaches places fixed billboards cannot, from Dhaka neighbourhoods to district towns.',
    who=['Shoppers at markets and bazaars', 'Students at campuses and colleges', 'Crowds at fairs, events and product launches', 'Towns and districts without LED billboards'],
    how=[('Plan the route', 'Choose the areas, stops and hours that match your audience.'),
         ('Confirm permissions and timing', 'We plan stops, timings and any local permissions needed for the route.'),
         ('Prepare the content', 'Video with sound works well; add a clear offer and where to buy.'),
         ('Run and report', 'The caravan tours the route; you receive photos, video and a route log.')],
    faq=[('What is an LED caravan?', 'A van or truck fitted with a large outdoor LED screen and sound, used to show ads on the move or at parked stops.'),
         ('Where can an LED caravan go?', 'Anywhere the vehicle can drive and park: Dhaka areas, markets, campuses, event grounds and district towns, subject to local rules.'),
         ('Can it play sound?', 'Yes. Unlike most roadside billboards, a caravan can play video with sound at stops.'),
         ('What is it best for?', 'Launches, roadshows, sales campaigns, activations and reaching towns without fixed LED screens.'),
         ('How do I book?', 'Call +880 1316-743003 or email info@ledadpro.com with your route idea and dates for a plan and written quote.')]),
}
