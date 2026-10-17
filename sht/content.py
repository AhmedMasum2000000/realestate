"""Second Home Thailand: the concierge pages. Guide and visa copy is shared with Move In Thailand (mit/content.py)."""

PHILOSOPHY = [
    ('01', 'One plan', 'Your residency route, your home and your budget are decided together, so the lease, the visa and the arrival date belong to the same move.'),
    ('02', 'In writing', 'Before any paid work starts you receive the scope, the fee and what is not included. Official fees stay separate and are set by the authorities.'),
    ('03', 'After arrival', 'The work does not end at the airport. Reports, extensions, re-entry and renewals go on one calendar, with a reminder before each date.'),
]

SERVICES = [
    {'index': '01', 'title': 'Residency strategy', 'text': 'A written comparison of the routes that fit your age, income, work and family, with the evidence each one asks for.', 'href': 'visas/', 'link': 'Compare routes'},
    {'index': '02', 'title': 'Application coordination', 'text': 'Document lists, translations, appointments and submissions, kept in order and checked against the current official guidance.', 'href': 'start-here/', 'link': 'See the steps'},
    {'index': '03', 'title': 'Home & property', 'text': 'Long-term rentals and condo purchases, with the ownership, lease and land office questions asked before you sign.', 'href': 'homes/', 'link': 'Homes guide'},
    {'index': '04', 'title': 'Arrival & settling', 'text': 'Bank account, health insurance, driving licence, TM30 and the first month, sequenced so one step unlocks the next.', 'href': 'living/', 'link': 'Living guide'},
    {'index': '05', 'title': 'Residency care', 'text': '90-day reports, yearly extensions and re-entry permits, tracked for you, so a date never becomes an overstay.', 'href': 'stay-legal/', 'link': 'Stay legal'},
]

PROCESS = [
    ('01', 'Consultation', 'A first conversation about why Thailand, who is moving, your timeline and what has to be true for the move to work.'),
    ('02', 'Route & plan', 'A written plan: the routes worth pursuing, the document list, the order of steps and an honest budget for the first year.'),
    ('03', 'Coordination', 'Documents prepared, appointments booked and the home search run in parallel, so nothing waits on anything it does not need to.'),
    ('04', 'Arrival & care', 'Bank, insurance, licence and reporting set up after landing, then renewals kept on a calendar for as long as you stay.'),
]

# The four long-stay routes shown in the showcase, keyed to Move In Thailand's ROUTE_SPECS.
SHOWCASE = {
    'thailand-privilege': ('Membership', 'Pay once, stay long. A membership route for people who would rather not prove an income.'),
    'ltr': ('Ten years', 'For high earners, pensioners, investors and skilled professionals who meet a BOI category.'),
    'retirement': ('Age 50+', 'The classic route for a slower life, renewed one year at a time from inside Thailand.'),
    'dtv': ('Remote work', 'Five years of entries for people working for employers or clients outside Thailand.'),
}

ENGAGEMENTS = [
    {'name': 'Route Review', 'for': 'You are still deciding.', 'items': ['A consultation about your goals and circumstances', 'A written comparison of the routes that fit', 'The document list for your preferred route', 'An honest first-year budget'], 'note': 'Ends with a plan you can follow yourself or hand to us.'},
    {'name': 'Residency Programme', 'for': 'You want it handled.', 'items': ['Everything in the Route Review', 'Application coordination from documents to decision', 'Home search or purchase questions run alongside', 'Arrival set-up: bank, insurance, licence, TM30'], 'note': 'One desk from the first call to your first month.', 'lead': True},
    {'name': 'Residency Care', 'for': 'You already live here.', 'items': ['90-day reports tracked and prepared', 'Yearly extensions and re-entry permits', 'Address and document changes kept current', 'A reminder before every date'], 'note': 'Ongoing, for as long as you stay.'},
]

FAQ = [
    ('How is Second Home Thailand different from Move In Thailand?', 'Move In Thailand is our free guide library and planning tools. Second Home Thailand is the private service: one desk that plans and coordinates your residency route, your home and your arrival with you.'),
    ('What does it cost?', 'Every engagement has a fixed scope and fee, quoted in writing before any paid work starts. Official visa, membership and government fees are separate and set by the responsible authorities.'),
    ('Can you guarantee my visa?', 'No one honestly can. Approval is decided by the responsible authority. What we can do is choose a route that fits your real circumstances and present complete, accurate documents.'),
    ('I am still researching. Is it too early to talk?', 'It is the best time. A first conversation often removes routes that do not fit and saves months of reading. You do not need a chosen visa or a property shortlist.'),
    ('I already live in Thailand. Can you still help?', 'Yes. Many people come to us for a route change, a first yearly extension, a property purchase or simply to hand over their reporting dates.'),
    ('Should I send my documents with the first message?', 'Please do not. Keep passports, bank statements and other sensitive records out of the first enquiry. We will tell you exactly what is needed, and how to share it, once there is a plan.'),
]

PRINCIPLES = [
    ('Fit before speed', 'We recommend the route your circumstances support, even when a faster or more expensive one is available.'),
    ('Written scope', 'What we do, what it costs and what is not included, agreed in writing before work begins.'),
    ('Official sources', 'Every guide links the authority that decides. Rules change; the source is where we check first.'),
    ('No promises we cannot keep', 'Authorities decide approvals. We say so plainly, and we tell you what could slow a case down.'),
    ('Private by default', 'No tracking cookies, no advertising scripts and no documents in a first enquiry.'),
]

PRIVACY = [
    ('What the consultation form collects', 'Your name, email, an optional contact number, your selected interest, move timeline, optional budget and your message. We record your permission to contact you, the submission time and the page you sent it from. A hashed network identifier is used briefly to limit repeated submissions.'),
    ('Why we use it', 'To answer your enquiry, prepare the consultation you asked for and coordinate the services you request. Marketing permission is optional and separate.'),
    ('Where it is kept', 'Enquiries are stored in this website’s private administration area, and a notification can be sent to the configured administrative inbox. Access is limited to authorised staff. The form does not take card details or document uploads.'),
    ('Your choices', 'You can ask for access, correction or deletion, or withdraw marketing permission, through the consultation form. Choose “A privacy request” and give enough detail to identify your enquiry. We may need to verify the request first.'),
    ('How long we keep it', 'Initial enquiries are kept for 180 days unless they become an ongoing requested service or must be kept for a legal obligation. Any later identity checks or professional work get their own explanation.'),
    ('Cookies', 'This website sets no analytics or advertising cookies. The Visa Finder runs in your browser and needs no account.'),
]
