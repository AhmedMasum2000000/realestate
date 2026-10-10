"""Guides added in the October 2026 content expansion.

Original writing, organised as a five-step journey (visa, area, home, set up,
stay legal). Competitor sites were reviewed for the list of topics people ask
about; none of their text is used. Facts were checked on GUIDE_CHECKED and need
the same review as content.py whenever rules change.

content.py applies these: new pages are appended, and existing pages and visa
routes gain the expanded sections, questions, sources and next steps while
keeping their own headings, introductions and checklists.
"""

GUIDE_CHECKED = "10 October 2026"

GUIDE_SOURCES = {'g_boi_long_term_resident_visa_po': ('BOI Long-Term Resident Visa portal', 'https://ltr.boi.go.th/'),
 'g_department_of_business_develop': ('Department of Business Development', 'https://www.dbd.go.th/en'),
 'g_royal_thai_embassy_information': ('Royal Thai Embassy information on the DTV',
                                      'https://budapest.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv'),
 'g_thai_e_visa_official_website': ('Thai e-Visa official website', 'https://www.thaievisa.go.th/'),
 'g_thai_immigration_bureau': ('Thai Immigration Bureau', 'https://www.immigration.go.th/'),
 'g_thailand_board_of_investment': ('Thailand Board of Investment', 'https://www.boi.go.th/'),
 'g_thailand_privilege_card_co_off': ('Thailand Privilege Card Co. (official)',
                                      'https://www.thailandprivilege.co.th/')}

GUIDES = [{'slug': 'start-here',
  'title': 'How to Move to Thailand: Step-by-Step Guide (2026) | Move In Thailand',
  'description': 'The complete order for moving to Thailand: choose a visa, budget, pick an area, find a '
                 'home, land and set up, then stay legal. Timelines and checklists.',
  'template': 'editorial',
  'eyebrow': 'THE WHOLE MOVE, IN ORDER',
  'heading': 'How to move to Thailand, step by step',
  'short': 'Start here',
  'intro': 'Moving here is easier than it looks, as long as you do things in the right order. The visa '
           'decides everything else, so it comes first. Here is the sequence, with a guide for every step.',
  'image': 'coast',
  'cards': [],
  'checklist': ['Typical planning time: 3 to 6 months', 'Five steps, taken in order', 'First decision: your visa'],
  'sections': [('Step 1: choose your visa (3 to 6 months before)',
                'Your visa sets how long you can stay, whether you can work, how much money you need to '
                'show, and what reporting you face. Settle it before you sign a lease or ship anything.',
                {'paras': ['Most people fit one of four routes: the [DTV](/visas/dtv/) for remote workers, '
                           'the [retirement visa](/visas/retirement/) for people 50 and over, the [marriage '
                           'visa](/visas/marriage/) for spouses of Thai nationals, or [Thailand '
                           "Privilege](/visas/thailand-privilege/) if you'd rather pay to skip the "
                           'paperwork. Higher earners should also check the [LTR](/visas/ltr/).'],
                 'note': 'Not sure? The [Visa Finder](/tools/visa-finder/) gives you a shortlist in two '
                         'minutes.'}),
               ('Step 2: budget and pick your area (2 to 4 months before)',
                'Thailand is affordable, but Bangkok, Phuket and Pattaya cost very different amounts. Use '
                'the [cost calculator](/tools/cost-calculator/) to see a monthly figure for your household, '
                'then read the [cost of living guide](/living/cost-of-living/).',
                {'paras': ['Choose the area for daily life, not holidays. Think about hospitals, schools, '
                           "noise, flooding and how you'll get around. Our [Pattaya neighbourhood "
                           'guide](/living/pattaya/) compares the main areas side by side.']}),
               ('Step 3: arrange a home (1 to 2 months before)',
                "Rent first, for 6 to 12 months. You'll learn the area, the building and the neighbours "
                'before committing. Our [renting guide](/homes/rent-in-pattaya/) explains deposits, '
                'contracts and what is normal.',
                {'paras': ['If you plan to buy, learn [what foreigners can own](/homes/foreign-ownership/) '
                           "now, so you don't fall for a structure that isn't legal."]}),
               ('Step 4: pack the paperwork (1 month before)',
                '',
                {'list': ['Passport with at least 18 months left and several blank pages.',
                          'Your visa approval, printed, plus the documents used to get it.',
                          'Bank statements for the last 3 to 6 months, and pension or salary proof.',
                          'Marriage and birth certificates, translated and legalised if family members are '
                          'joining you. See [documents and legal help](/living/wills-and-documents/).',
                          'Your driving licence and an International Driving Permit, if you plan to convert '
                          'to a Thai licence.',
                          'Health records and prescriptions, plus [health '
                          'insurance](/living/health-insurance/) that starts the day you land.']}),
               ('Step 5: land and set up (first 30 days)',
                '',
                {'steps': ['Day 1: get a Thai SIM at the airport. Bring your passport.',
                           'Within 24 hours: your landlord files your [TM30 address '
                           'report](/stay-legal/tm30/). Ask for the receipt.',
                           'Week 1 to 2: open a [Thai bank account](/living/bank-account/). Most retirement '
                           'and marriage visas need one.',
                           'Week 2 to 4: get a [residence certificate](/stay-legal/residence-certificate/), '
                           'then convert your [driving licence](/living/driving-licence/).'],
                 'after': ['The [first-month checklist](/living/moving-checklist/) lists every task, with '
                           'the office and the documents for each one.']}),
               ('Step 6: stay legal, then build your life',
                'Long stays come with routine paperwork: a [90-day report](/stay-legal/90-day-report/), a '
                'yearly [extension of stay](/stay-legal/extension-of-stay/), and a [re-entry '
                'permit](/stay-legal/re-entry-permit/) whenever you travel. Miss one and the fines start; '
                'miss an extension and you are [overstaying](/stay-legal/overstay/).',
                {'paras': ["Once you're settled, you might [buy a condo](/homes/buy-condo-thailand/), [set "
                           "up a company](/business/company-setup/) or [invest](/invest/). We'll handle the "
                           "reminders for you through [Residency Care](/residency-care/) if you'd rather not "
                           'track the dates.']})],
  'faqs': [('How long does the whole move take?',
            'Three to six months is comfortable. Visa approvals typically take 1 to 6 weeks depending on the '
            'route and the embassy, and good rentals are usually booked 4 to 8 weeks ahead.'),
           ('Can I come on a visa exemption and sort things out later?',
            'Sometimes. Several long-stay visas can be applied for from inside Thailand, but not all, and '
            'the rules depend on your nationality. Check first in the [visa exemption '
            'guide](/visas/tourist-and-visa-exemption/).'),
           ('Do I need to speak Thai?',
            'No. Pattaya, Bangkok, Phuket and Chiang Mai run comfortably in English for daily life. '
            'Government offices are easier with a Thai speaker, which is part of what we do.')],
  'sources': [],
  'related': [('Cost of living',
               'Monthly budgets for singles, couples and families, line by line, by city.',
               'living/cost-of-living/'),
              ('Moving checklist',
               'Documents to pack, the first week and the first 30 days, in order.',
               'living/moving-checklist/')],
  'next': ('Compare every visa route', 'visas/')},
 {'slug': 'visas/family',
  'title': 'Thailand Family Visas: Thai Child, Dependent & Guardian Visa Guide',
  'description': 'Non-O visas for parents of Thai children, dependants of work permit or LTR holders, and '
                 'guardians of students in Thailand. Who qualifies, money rules and renewals.',
  'template': 'editorial',
  'eyebrow': 'VISA GUIDE',
  'heading': 'Family visas: Thai children, dependants and guardians',
  'short': 'Family visas',
  'intro': 'Thailand has a family visa for almost every situation. Each one is a Non-O, renewed yearly at '
           'immigration, and each one is tied to the person you are joining.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('The three family routes',
                '',
                {'table': {'head': ['Route', "Who it's for", 'Money rule (usual)'],
                           'rows': [['Thai child visa',
                                     'Parent of a child with Thai nationality, who supports the child in '
                                     'Thailand',
                                     '400,000 THB in a Thai bank, or 40,000 THB a month'],
                                    ['Dependant visa',
                                     'Spouse or child under 20 of someone working here on a work permit, or '
                                     'of an LTR or DTV holder',
                                     "Usually covered by the main holder's status; proof of the relationship "
                                     'is the key document'],
                                    ['Guardian visa',
                                     'Parent of a child studying at a Thai school on an education visa',
                                     'Commonly 500,000 THB per child in a Thai bank']]}}),
               ("Documents you'll be asked for",
                '',
                {'list': ['Birth certificate showing the parent, translated and legalised if issued abroad.',
                          'Marriage certificate for spouses, registered in Thailand if possible.',
                          "The main holder's passport, visa and work permit or school letter.",
                          'Bank letter and book for the money rule, and photos of family life.'],
                 'note': 'Foreign certificates usually need translation and legalisation before immigration '
                         'accepts them. See [documents and legal help](/living/wills-and-documents/).'}),
               ('Renewal and travel',
                'Family extensions run for one year and are renewed at your local immigration office, like '
                "the [marriage visa](/visas/marriage/). The dependant's extension usually can't run longer "
                "than the main holder's. Get a [re-entry permit](/stay-legal/re-entry-permit/) before any "
                'trip abroad.')],
  'faqs': [('Can a dependant work?',
            'Only with their own work permit. Some LTR dependants can apply for one more easily; check your '
            'own case.'),
           ("My child is Thai but I'm not married to their mother. Can I still get a visa?",
            "Often yes, if you're named on the birth certificate and you support the child. Expect closer "
            'questioning and a home visit.')],
  'sources': [],
  'related': [('Marriage visa',
               'Married to a Thai? 400,000 THB in the bank or 40,000 THB a month, renewed yearly.',
               'visas/marriage/'),
              ('Education visa',
               'For enrolled students. Often the DTV is better for Muay Thai and cooking courses.',
               'visas/education/'),
              ('Extensions and renewals',
               'How yearly extensions work for retirement, marriage, business, family and student visas.',
               'stay-legal/extension-of-stay/')],
  'next': ('Living in Pattaya', 'living/pattaya/')},
 {'slug': 'visas/work-permit',
  'title': 'Thailand Work Permit 2026: Requirements, Renewal & Digital Permit',
  'description': 'How Thai work permits work in 2026: company rules, documents, the digital work permit, '
                 'renewals, job changes and what happens if you work without one.',
  'template': 'editorial',
  'eyebrow': 'WORK GUIDE',
  'heading': 'Thai work permits explained',
  'short': 'Work permit',
  'intro': 'Any work in Thailand needs a work permit, including running your own company. The permit is '
           'issued by the Department of Employment and names your employer, your job and where you do it.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('What counts as work',
                'Thai law defines work broadly: any physical or mental effort, paid or not. Remote work for '
                'clients abroad on a [DTV](/visas/dtv/) is allowed by that visa. Working for a Thai '
                'business, or serving Thai customers, needs a permit.',
                {'warn': 'Working without a permit can mean a fine, deportation and a ban, for you and a '
                         'fine for the employer. Some jobs are reserved for Thai nationals altogether.'}),
               ('How to get a work permit',
                '',
                {'steps': ['Enter on a [Non-B visa](/visas/business/) (or another visa that allows a permit, '
                           'such as some LTR and family visas).',
                           'The employer files the application with company documents: registration, '
                           'shareholder list, VAT and social security records, financial statements, an '
                           'office map and photos.',
                           'You supply your passport, degree certificates, CV, a medical certificate and '
                           'photos.',
                           'The permit is issued, increasingly as a digital work permit you can show on your '
                           'phone.']}),
               ('Renewals and changes',
                '',
                {'list': ['Renew before expiry; the permit and your extension of stay usually run on the '
                          'same yearly cycle.',
                          'Changing employer means a new permit and usually a new visa process. Cancel the '
                          'old permit when you leave.',
                          'Adding a new job title or work location needs the permit amended first.']})],
  'faqs': [],
  'sources': [],
  'related': [('Business visa',
               'For employees and company owners. Comes with a work permit and yearly renewals.',
               'visas/business/'),
              ('Company setup',
               'Name, shareholders, capital, registration, tax and bank, in the order it happens.',
               'business/company-setup/'),
              ('Business ownership rules',
               'The 49% rule, the four lawful ways past it, and why nominees are now a serious risk.',
               'business/foreign-ownership/')],
  'next': ('Business & invest', 'business/')},
 {'slug': 'visas/tourist-and-visa-exemption',
  'title': 'Thailand Visa Exemption & Tourist Visa 2026: Stays, Extensions, Border Runs',
  'description': 'Short stays in Thailand: visa-exempt entry, the tourist visa, 30-day extensions, why '
                 'border runs are now risky, and when to switch to a long-stay visa.',
  'template': 'editorial',
  'eyebrow': 'SHORT STAYS',
  'heading': 'Visa exemption, tourist visas and border runs',
  'short': 'Short stays',
  'intro': "Most visitors arrive visa-free. That's perfect for a scouting trip to view areas and homes. It "
           'is not a way to live here: repeated entries get noticed, and from 2026 officers are refusing '
           "people who look like they're living on tourist stays.",
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('Visa-exempt entry',
                'Citizens of many countries can enter without a visa. Since July 2024 the standard exempt '
                'stay for most Western nationalities has been 60 days, and the government has discussed '
                'shortening it. Check the current figure for your passport before you book.',
                {'paras': ['You can usually extend a visa-exempt stay once, by 30 days, at an immigration '
                           'office for 1,900 THB.']}),
               ('Tourist visa',
                "A single-entry tourist visa (TR) gives 60 days, plus one 30-day extension. It's useful if "
                'your nationality gets a short exempt stay, or if you want certainty before flying.'),
               ('Border runs and visa runs',
                'A border run means leaving Thailand briefly to get a new entry stamp. Land-border entries '
                'for visa-exempt travellers are limited each year, and airport officers can refuse entry to '
                'people who have spent most of the past year here on exempt stays. They may ask for onward '
                'tickets, accommodation and money.',
                {'warn': "If you're living here, a border run is a gamble with your plans. A long-stay visa "
                         'such as the [DTV](/visas/dtv/) costs less than a few runs and removes the risk.'}),
               ('Turning a scouting trip into a move',
                '',
                {'steps': ['Use the trip to choose an area and view homes. See [living in '
                           'Pattaya](/living/pattaya/).',
                           'Check whether your target visa can be converted in Thailand or must be applied '
                           'for abroad.',
                           'Leave before your stay ends. Even one day over is an '
                           '[overstay](/stay-legal/overstay/).']})],
  'faqs': [],
  'sources': [],
  'related': [('DTV visa',
               '5 years, 180 days per entry, for remote workers and Muay Thai, cooking or culture students.',
               'visas/dtv/'),
              ('Overstay',
               "500 THB a day, bans from 1 to 10 years. Turn yourself in before you're caught.",
               'stay-legal/overstay/'),
              ('Extensions and renewals',
               'How yearly extensions work for retirement, marriage, business, family and student visas.',
               'stay-legal/extension-of-stay/')],
  'next': ('Compare every visa route', 'visas/')},
 {'slug': 'visas/permanent-residence',
  'title': 'Thailand Permanent Residence 2026: Eligibility, Quota & Fees',
  'description': 'Permanent residence in Thailand: who can apply after 3 years of extensions, the yearly '
                 'quota, application window, fees, and what PR changes for you.',
  'template': 'editorial',
  'eyebrow': 'VISA GUIDE',
  'heading': 'Permanent residence in Thailand',
  'short': 'Permanent residence',
  'intro': "Permanent residence ends visa renewals for good. It's harder to get than most visas: a small "
           'quota per nationality, a once-a-year application window, and a process that can take a year or '
           'more.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('Who can apply',
                '',
                {'list': ["You've held a non-immigrant visa with yearly extensions for at least 3 "
                          'consecutive years.',
                          'You fit a category: employment (with a qualifying salary and tax history), '
                          'investment in Thailand, family (married to a Thai, or parent of a Thai child), or '
                          'expert.',
                          'Retirement extensions do not count towards permanent residence.']}),
               ('The process and costs',
                '',
                {'steps': ['Apply in the yearly window, usually at the end of the year, at Immigration '
                           'Bureau headquarters in Bangkok.',
                           'Pay the application fee (7,600 THB at the last published rate).',
                           'Attend an interview, which includes basic Thai.',
                           'On approval, pay the approval fee (191,400 THB, or about half for spouses and '
                           'children of Thai nationals, at the last published rate).'],
                 'note': 'Fees and the application window are set each year. We confirm the current figures '
                         'before you file.'}),
               ('What PR changes',
                '',
                {'list': ['No more yearly extensions or 90-day reports.',
                          'You still need a re-entry permit for travel, and an endorsement of your residence '
                          'book.',
                          'It can lead to Thai citizenship after several more years.']})],
  'faqs': [],
  'sources': [],
  'related': [('LTR visa',
               '10 years, a digital work permit and one yearly report, for higher earners and wealthy '
               'retirees.',
               'visas/ltr/'),
              ('Extensions and renewals',
               'How yearly extensions work for retirement, marriage, business, family and student visas.',
               'stay-legal/extension-of-stay/'),
              ('Marriage visa',
               'Married to a Thai? 400,000 THB in the bank or 40,000 THB a month, renewed yearly.',
               'visas/marriage/')],
  'next': ('Stay legal', 'stay-legal/')},
 {'slug': 'stay-legal',
  'title': 'Staying Legal in Thailand: 90-Day Reports, TM30, Extensions & More',
  'description': 'Every report, form and deadline that keeps a foreign resident legal in Thailand: 90-day '
                 'reports, TM30, yearly extensions, re-entry permits and overstays.',
  'template': 'editorial',
  'eyebrow': 'STAY LEGAL',
  'heading': 'Stay legal, without the stress',
  'short': 'Stay legal',
  'intro': 'Long-stay visas come with routine paperwork. None of it is hard, but the deadlines are strict '
           "and the fines are real. Here's every task, when it's due and how to do it.",
  'image': 'coast',
  'cards': [('90-day report',
             'Due every 90 days of continuous stay. File online, in person or through an agent.',
             'stay-legal/90-day-report/'),
            ('Extensions and renewals',
             'How yearly extensions work for retirement, marriage, business, family and student visas.',
             'stay-legal/extension-of-stay/'),
            ('TM30 notification',
             'Your landlord tells immigration where you live within 24 hours. Keep the receipt.',
             'stay-legal/tm30/'),
            ('Re-entry permit',
             'Leaving Thailand on an extension? Without this permit, the extension ends at the border.',
             'stay-legal/re-entry-permit/'),
            ('Residence certificate',
             "Immigration's letter confirming your address. Needed for a driving licence and more.",
             'stay-legal/residence-certificate/'),
            ('Pattaya immigration',
             "Where it is, when it's open, and how to get through it quickly.",
             'stay-legal/pattaya-immigration-office/'),
            ('Overstay',
             "500 THB a day, bans from 1 to 10 years. Turn yourself in before you're caught.",
             'stay-legal/overstay/')],
  'checklist': [],
  'sections': [('Your year at a glance',
                '',
                {'table': {'head': ['Task', 'How often', 'Penalty if missed'],
                           'rows': [['[90-day report](/stay-legal/90-day-report/)',
                                     'Every 90 days of continuous stay',
                                     "2,000 THB fine; more if you're caught"],
                                    ['[Extension of stay](/stay-legal/extension-of-stay/)',
                                     'Once a year',
                                     'You start overstaying the next day'],
                                    ['[TM30 address report](/stay-legal/tm30/)',
                                     'Each time you move or return from abroad',
                                     'A fine for the landlord or for you; problems at your next extension'],
                                    ['[Re-entry permit](/stay-legal/re-entry-permit/)',
                                     'Before every trip abroad',
                                     'Your extension is cancelled when you leave']]}})],
  'faqs': [],
  'sources': [],
  'related': [],
  'next': ('Residency Care', 'residency-care/')},
 {'slug': 'stay-legal/90-day-report',
  'title': 'Thailand 90-Day Report 2026: Online, In Person, Deadlines & Fines',
  'description': "How to file Thailand's 90-day report online, by post or at immigration: the 15-day window, "
                 'documents, the 2,000 THB fine for late reports, and who is exempt.',
  'template': 'editorial',
  'eyebrow': 'STAY LEGAL',
  'heading': 'The 90-day report',
  'short': '90-day report',
  'intro': 'If you stay in Thailand for more than 90 days without leaving, you must confirm your address '
           "with immigration every 90 days. It's free, takes minutes, and is the most commonly missed "
           'deadline in Thailand.',
  'image': 'coast',
  'cards': [],
  'checklist': ['Cost: free',
                'Filing opens 15 days before the due date',
                'Grace period: 7 days after it',
                'Late fine: 2,000 THB'],
  'sections': [("When it's due",
                'The count starts on your arrival date, or on your last 90-day report. You can file from 15 '
                'days before the due date until 7 days after it. Leaving Thailand resets the count: your '
                'first report is due 90 days after you come back.'),
               ('Four ways to file',
                '',
                {'table': {'head': ['Method', 'How', 'Good for'],
                           'rows': [['Online',
                                     "Immigration's online 90-day system, using your passport and address",
                                     'Second and later reports, once your first report is on file'],
                                    ['In person',
                                     'At your local immigration office with passport, TM.47 form and copies',
                                     'Your first report, or if the online system rejects you'],
                                    ['By post',
                                     'Registered mail with the TM.47 form and copies, sent early',
                                     'People far from an office'],
                                    ['Through someone else',
                                     'A representative with a signed authorisation',
                                     'Busy people, or our [Residency Care](/residency-care/) clients']]}}),
               ('What to bring in person',
                '',
                {'list': ['Passport, with copies of the photo page, current visa or extension, and latest '
                          'entry stamp.',
                          'Form TM.47, filled in and signed.',
                          'Your previous 90-day receipt, if you have one.',
                          'Your [TM30](/stay-legal/tm30/) receipt, which many offices check.'],
                 'note': 'LTR visa holders report once a year instead. Thailand Privilege members can have '
                         'reports handled through their membership.'})],
  'faqs': [("I'm going abroad before my report is due. Do I still file?",
            'No. Leaving resets the 90-day count. Just get a [re-entry permit](/stay-legal/re-entry-permit/) '
            'if you hold an extension.'),
           ("What if I'm late?",
            "Go to immigration and pay the fine, 2,000 THB if you come in yourself. If you're stopped and "
            "found to be late, it is higher. It won't cost you your visa, but don't make it a habit.")],
  'sources': ['g_thai_immigration_bureau'],
  'related': [('TM30 notification',
               'Your landlord tells immigration where you live within 24 hours. Keep the receipt.',
               'stay-legal/tm30/'),
              ('Extensions and renewals',
               'How yearly extensions work for retirement, marriage, business, family and student visas.',
               'stay-legal/extension-of-stay/')],
  'next': ('Extensions and renewals', 'stay-legal/extension-of-stay/')},
 {'slug': 'stay-legal/extension-of-stay',
  'title': 'Thailand Visa Extension 2026: Yearly Extensions, Renewals & 30-Day Extensions',
  'description': 'How to extend your stay in Thailand: yearly extensions for retirement, marriage, family, '
                 'business and education visas, plus 30-day tourist extensions. Fees, steps.',
  'template': 'editorial',
  'eyebrow': 'STAY LEGAL',
  'heading': 'Extensions of stay: renewing every year',
  'short': 'Extensions and renewals',
  'intro': 'Most long-stay visas only get you in the door. What keeps you here is a yearly extension of stay '
           'at your local immigration office. Same office, same month, every year.',
  'image': 'coast',
  'cards': [],
  'checklist': ['Fee: 1,900 THB per extension',
                'Apply 30 to 45 days before expiry, depending on the office',
                'Usual length: 1 year'],
  'sections': [('Which extension you need',
                '',
                {'table': {'head': ['Based on', 'Main test', 'Guide'],
                           'rows': [['Retirement',
                                     '800,000 THB or 65,000 THB a month',
                                     '[Retirement visa](/visas/retirement/)'],
                                    ['Marriage to a Thai',
                                     '400,000 THB or 40,000 THB a month, plus a home visit',
                                     '[Marriage visa](/visas/marriage/)'],
                                    ['Thai child or dependant',
                                     'Relationship documents and support',
                                     '[Family visas](/visas/family/)'],
                                    ['Employment',
                                     'Work permit and company documents',
                                     '[Business visa](/visas/business/)'],
                                    ['Study',
                                     'School letter and attendance',
                                     '[Education visa](/visas/education/)'],
                                    ['Tourist or visa exemption',
                                     'One 30-day extension',
                                     '[Short stays](/visas/tourist-and-visa-exemption/)']]}}),
               ('The yearly routine',
                '',
                {'steps': ['Two months before: check the money rule or company documents are in order.',
                           'One month before: book a slot if your office uses appointments, and gather '
                           'documents.',
                           'Apply with passport, TM.7 form, photo, fee, supporting documents and copies of '
                           "every passport page you've used.",
                           "Collect your 'under consideration' stamp if one is issued, then the full "
                           'extension.',
                           'Diary the next date, and your next [90-day report](/stay-legal/90-day-report/).'],
                 'warn': 'Never let the current extension lapse while you wait. If an application is '
                         'refused, you usually get 7 days to leave. Apply early enough to fix problems.'})],
  'faqs': [('Do I need to leave Thailand to renew?',
            'No. Extensions are done in Thailand at immigration, as long as you apply before the current '
            'permission ends.'),
           ('Can I change from one type of extension to another?',
            'Often, yes. For example, from marriage to retirement once you turn 50. Changes take more '
            'paperwork, so plan them ahead.')],
  'sources': [],
  'related': [('90-day report',
               'Due every 90 days of continuous stay. File online, in person or through an agent.',
               'stay-legal/90-day-report/'),
              ('Re-entry permit',
               'Leaving Thailand on an extension? Without this permit, the extension ends at the border.',
               'stay-legal/re-entry-permit/'),
              ('Pattaya immigration',
               "Where it is, when it's open, and how to get through it quickly.",
               'stay-legal/pattaya-immigration-office/')],
  'next': ('Re-entry permit', 'stay-legal/re-entry-permit/')},
 {'slug': 'stay-legal/tm30',
  'title': 'TM30 Form Thailand 2026: Notification of Residence Explained',
  'description': 'The TM30 notification of residence: who files it (usually your landlord), the 24-hour '
                 'deadline, how to file online, fines, and why you need the receipt.',
  'template': 'editorial',
  'eyebrow': 'STAY LEGAL',
  'heading': 'TM30: the address report',
  'short': 'TM30 notification',
  'intro': 'The TM30 is how immigration knows where foreigners stay. The duty falls on the owner or manager '
           'of the place you stay, within 24 hours of your arrival. Hotels do it automatically; private '
           'landlords often forget.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('Who must file, and when',
                '',
                {'list': ['**The house owner, landlord or condo manager** files it within 24 hours of a '
                          'foreigner arriving to stay.',
                          '**You file it yourself** if you own the home you live in.',
                          "It's needed again when you move, and in many offices after every return from "
                          'abroad.']}),
               ('Why you need the receipt',
                "Immigration offices increasingly ask for the TM30 receipt before they'll process an "
                '[extension](/stay-legal/extension-of-stay/), a [90-day report](/stay-legal/90-day-report/) '
                'or a [residence certificate](/stay-legal/residence-certificate/). No receipt, no service, '
                "even though the duty was your landlord's.",
                {'note': 'Ask for the TM30 receipt when you sign a lease. A good landlord or agent files it '
                         'online the same day.'}),
               ("How it's filed",
                '',
                {'steps': ["Online, through immigration's TM30 system, after the owner registers once.",
                           "In person at immigration, with the owner's ID, title deed or house book, your "
                           'passport copy and the lease.',
                           'The receipt slip is printed or downloaded. Keep a copy with your passport.']})],
  'faqs': [("My landlord won't file it. What now?",
            "You can file it yourself at immigration with the lease and the owner's documents. If they "
            "refuse to provide them, it's a sign to find another landlord."),
           ("What's the fine?",
            'Fines are charged to the person responsible, usually the landlord, and run into the low '
            'thousands of baht. The bigger cost is a delayed extension.')],
  'sources': [],
  'related': [('90-day report',
               'Due every 90 days of continuous stay. File online, in person or through an agent.',
               'stay-legal/90-day-report/'),
              ('Renting in Pattaya',
               'Typical rents, deposits, contracts and the questions to ask before you sign.',
               'homes/rent-in-pattaya/'),
              ('Residence certificate',
               "Immigration's letter confirming your address. Needed for a driving licence and more.",
               'stay-legal/residence-certificate/')],
  'next': ('Residence certificate', 'stay-legal/residence-certificate/')},
 {'slug': 'stay-legal/re-entry-permit',
  'title': 'Thailand Re-Entry Permit 2026: Single, Multiple, Cost & Where',
  'description': 'Why you need a re-entry permit before leaving Thailand on an extension of stay: single '
                 '(1,000 THB) or multiple (3,800 THB), where to get one, and what happens without.',
  'template': 'editorial',
  'eyebrow': 'STAY LEGAL',
  'heading': "Re-entry permits: don't lose your visa at the airport",
  'short': 'Re-entry permit',
  'intro': 'An extension of stay is cancelled the moment you leave Thailand, unless you have a re-entry '
           "permit. It's the cheapest insurance in Thai immigration, and the most painful to forget.",
  'image': 'coast',
  'cards': [],
  'checklist': ['Single re-entry permit: 1,000 THB', 'Multiple re-entry permit: 3,800 THB'],
  'sections': [('Who needs one',
                'Anyone holding a yearly extension (retirement, marriage, family, business, education) or a '
                'single-entry visa they want to keep. Multiple-entry visas such as the DTV and Thailand '
                "Privilege don't need one for their own entries."),
               ('Where to get it',
                '',
                {'list': ['At your local immigration office, any time before you travel. Best for '
                          'multiple-entry permits.',
                          'At the airport immigration counter before departure (single entry). Allow extra '
                          'time.'],
                 'steps': ['Fill in form TM.8, add a photo and passport copies.',
                           'Pay the fee: 1,000 THB single, 3,800 THB multiple.',
                           'The permit is stamped into your passport and lasts until your current extension '
                           'ends.']})],
  'faqs': [('I forgot and already left. Is my visa gone?',
            "Yes, the extension is cancelled. You'll need to re-enter on a new visa or exemption and start "
            'the process again. Plan the quickest route before you fly back.')],
  'sources': [],
  'related': [('Extensions and renewals',
               'How yearly extensions work for retirement, marriage, business, family and student visas.',
               'stay-legal/extension-of-stay/'),
              ('90-day report',
               'Due every 90 days of continuous stay. File online, in person or through an agent.',
               'stay-legal/90-day-report/'),
              ('Retirement visa',
               'Age 50+? 800,000 THB in a Thai bank, or 65,000 THB a month, renewed every year.',
               'visas/retirement/')],
  'next': ('TM30 notification', 'stay-legal/tm30/')},
 {'slug': 'stay-legal/residence-certificate',
  'title': "Thai Residence Certificate 2026: What It's For & How to Get One",
  'description': 'The certificate of residence from Thai immigration: why banks, the driving licence office '
                 'and car dealers ask for it, the documents, and how long it takes.',
  'template': 'editorial',
  'eyebrow': 'STAY LEGAL',
  'heading': 'The residence certificate',
  'short': 'Residence certificate',
  'intro': "A residence certificate is a letter from immigration confirming where you live. You'll need one "
           'to get a Thai driving licence, register a car or motorbike, and sometimes to open a bank account '
           'or connect utilities.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [("What you'll need",
                '',
                {'list': ['Passport, with copies of the photo page, visa, latest entry stamp and departure '
                          'card or e-record.',
                          'Your [TM30](/stay-legal/tm30/) receipt.',
                          "Lease or title deed, and the owner's ID card copy if you rent.",
                          'Two passport photos and the application form from the office.']}),
               ('How long it takes',
                'Some offices issue it the same day; others take a few working days. A small fee applies. '
                'The certificate is usually accepted for 30 to 60 days, so get it just before you need it.')],
  'faqs': [],
  'sources': [],
  'related': [('Driving licence',
               'Convert your licence, sit the test, or renew: car and motorbike, all in one guide.',
               'living/driving-licence/'),
              ('Bank account',
               'Which visa you need, which banks to try, and the documents to bring.',
               'living/bank-account/'),
              ('Pattaya immigration',
               "Where it is, when it's open, and how to get through it quickly.",
               'stay-legal/pattaya-immigration-office/')],
  'next': ('Driving licence', 'living/driving-licence/')},
 {'slug': 'stay-legal/overstay',
  'title': 'Overstay in Thailand: Fines, Bans and What to Do Now',
  'description': 'Overstayed in Thailand? The 500 THB a day fine, the 20,000 THB cap, entry bans of 1 to 10 '
                 "years, and how to leave with the least damage. Act before you're caught.",
  'template': 'editorial',
  'eyebrow': 'WHEN THINGS GO WRONG',
  'heading': 'Overstayed? What happens, and what to do',
  'short': 'Overstay',
  'intro': 'An overstay starts the day after your permission to stay ends. A day or two costs a fine at the '
           'airport. Longer overstays bring bans, and being caught is far worse than coming forward.',
  'image': 'coast',
  'cards': [],
  'checklist': ['Fine: 500 THB per day', 'Maximum fine: 20,000 THB', 'Possible re-entry ban: 1 to 10 years'],
  'sections': [('Fines and bans',
                '',
                {'table': {'head': ['Situation', 'What usually happens'],
                           'rows': [['Overstay under 90 days, you leave voluntarily',
                                     'Fine of 500 THB a day, paid at departure. No ban.'],
                                    ['Over 90 days, you surrender',
                                     'Fine plus a 1-year ban (longer overstays: 3, 5 or 10 years)'],
                                    ['Caught overstaying, under 1 year',
                                     'Arrest, detention, deportation and a 5-year ban'],
                                    ['Caught overstaying, over 1 year',
                                     'Arrest, deportation and a 10-year ban']]}}),
               ('What to do now',
                '',
                {'steps': ["Don't travel around the country. Checkpoints are where most overstayers are "
                           'caught.',
                           'Book a flight out, and go to the airport early to pay the fine at immigration.',
                           'If your overstay is long, talk to a lawyer first about surrendering at an '
                           'immigration office.'],
                 'warn': "You can't extend or convert a visa while overstaying. The only safe step is to "
                         'regularise by leaving or surrendering.'})],
  'faqs': [],
  'sources': [],
  'related': [('Extensions and renewals',
               'How yearly extensions work for retirement, marriage, business, family and student visas.',
               'stay-legal/extension-of-stay/'),
              ('Short stays',
               'Scouting trip? How long you can stay, how to extend once, and why border runs are risky.',
               'visas/tourist-and-visa-exemption/'),
              ('Pattaya immigration',
               "Where it is, when it's open, and how to get through it quickly.",
               'stay-legal/pattaya-immigration-office/')],
  'next': ('Stay legal', 'stay-legal/')},
 {'slug': 'stay-legal/pattaya-immigration-office',
  'title': 'Pattaya Immigration Office (Jomtien) 2026: Location, Hours & Tips',
  'description': 'The immigration office serving Pattaya, in Jomtien: where it is, opening hours, which '
                 'services are handled there, what to bring and how to avoid the queues.',
  'template': 'editorial',
  'eyebrow': 'OFFICE GUIDE',
  'heading': 'The Pattaya immigration office, Jomtien',
  'short': 'Pattaya immigration',
  'intro': 'Foreign residents of Pattaya are served by the Chonburi immigration office in Jomtien, on Soi 5 '
           'off Jomtien Beach Road. It handles extensions, 90-day reports, re-entry permits, TM30 and '
           'residence certificates.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('The basics',
                '',
                {'table': {'head': ['What', 'Detail'],
                           'rows': [['Location', 'Jomtien Soi 5, off Jomtien Beach Road, Pattaya'],
                                    ['Hours',
                                     'Monday to Friday, about 8:30 to 16:30; closed weekends and public '
                                     'holidays'],
                                    ['Services',
                                     'Extensions, 90-day reports, re-entry permits, TM30, residence '
                                     'certificates, change of visa type'],
                                    ['Queues',
                                     'Longest on Mondays, after holidays and from November to March']]}}),
               ('How to make it painless',
                '',
                {'list': ['Arrive before opening for extensions; queue numbers can run out by late morning '
                          'in high season.',
                          "Bring copies of every passport page you've used, signed. Copy shops nearby charge "
                          'a few baht a page.',
                          'Dress respectfully: long trousers or a skirt, covered shoulders.',
                          'Check whether the office is using appointments for your service; this changes.'],
                 'note': 'Hours and procedures change. Confirm before you go.'})],
  'faqs': [],
  'sources': [],
  'related': [('Extensions and renewals',
               'How yearly extensions work for retirement, marriage, business, family and student visas.',
               'stay-legal/extension-of-stay/'),
              ('90-day report',
               'Due every 90 days of continuous stay. File online, in person or through an agent.',
               'stay-legal/90-day-report/')],
  'next': ('Stay legal', 'stay-legal/')},
 {'slug': 'homes/foreign-ownership',
  'title': 'What Foreigners Can Own in Thailand (2026): Condos, Houses, Land, Leases',
  'description': 'Clear rules on property ownership for foreigners in Thailand: condo freehold under the 49% '
                 'quota, leasehold land, owning the house but not the land, and nominee risks.',
  'template': 'editorial',
  'eyebrow': 'HOMES GUIDE',
  'heading': 'What foreigners can own in Thailand',
  'short': 'What foreigners can own',
  'intro': 'The rules are simpler than the sales pitches. A foreigner can own a condo unit outright. A '
           'foreigner cannot own land. Everything else is a legal structure around that line, and some '
           'structures are illegal.',
  'image': 'home',
  'cards': [],
  'checklist': [],
  'sections': [('The four options at a glance',
                '',
                {'table': {'head': ['Option', 'Legal?', 'What you actually own'],
                           'rows': [['Condo in your own name',
                                     'Yes',
                                     "Freehold title to the unit, within the building's 49% foreign quota"],
                                    ['House on leased land',
                                     'Yes',
                                     'The house itself, plus a registered lease of the land for up to 30 '
                                     'years'],
                                    ['Property through a Thai spouse',
                                     'Yes',
                                     "Nothing: it is your spouse's. You sign that the money is theirs"],
                                    ['Land through a Thai company with nominee shareholders',
                                     'No',
                                     'A criminal risk, and property that can be seized']]}}),
               ('Condos',
                "Up to 49% of a building's sellable floor area can be owned by foreigners. Your money must "
                "come into Thailand from abroad in foreign currency; the bank's record of that transfer is "
                'what the Land Office checks. See [buying a condo](/homes/buy-condo-thailand/).'),
               ('Houses and land',
                'You can own a building separately from the land under it. The usual route is to own the '
                'house and take a 30-year lease of the land, registered at the Land Office. Promises of '
                "'automatic renewal' for a further 30 years are not reliably enforceable; price the deal on "
                'the first term.',
                {'paras': ['In 2025 the government discussed 99-year leases and a higher condo quota in some '
                           "zones. As of our last check, neither is law. Don't pay a premium for a promise "
                           'that depends on them.']}),
               ('Companies and nominees',
                '',
                {'after': ['There are lawful company routes for real businesses, such as BOI promotion. See '
                           '[foreign business ownership](/business/foreign-ownership/).'],
                 'warn': 'A Thai company can own land only if Thai shareholders genuinely own the majority '
                         'with their own money. Using Thais who just lend their names is a crime under the '
                         'Foreign Business Act and the Land Code. Since January 2026 the authorities have '
                         'tightened company registration and are investigating thousands of companies in '
                         'property and tourism.'})],
  'faqs': [('Can my children inherit my condo?',
            'Yes. A condo can pass to foreign heirs, subject to the quota and the inheritance process. Make '
            'a [Thai will](/living/wills-and-documents/) to keep it simple.'),
           ('Does a long-stay visa change these rules?',
            'No. Ownership rules are the same whatever your visa.')],
  'sources': [],
  'related': [('Buying a condo',
               'Quota, money transfer, due diligence, contract and transfer day, in order.',
               'homes/buy-condo-thailand/'),
              ('Business ownership rules',
               'The 49% rule, the four lawful ways past it, and why nominees are now a serious risk.',
               'business/foreign-ownership/')],
  'next': ('Buying a condo', 'homes/buy-condo-thailand/')},
 {'slug': 'homes/property-transfer',
  'title': 'Property Transfer at the Land Office, Pattaya (2026): Fees, Taxes, Documents',
  'description': 'What happens on transfer day at the Banglamung Land Office: documents, title deed types '
                 'and checks, transfer fees and taxes, and how to transfer through a representative.',
  'template': 'editorial',
  'eyebrow': 'HOMES GUIDE',
  'heading': 'Transfer day at the Land Office',
  'short': 'Land Office transfer',
  'intro': 'Ownership changes hands only when the transfer is registered at the Land Office. For Pattaya, '
           "that's the Banglamung Land Office. It's a half-day process when the paperwork is right.",
  'image': 'home',
  'cards': [],
  'checklist': [],
  'sections': [("Title deeds you'll meet",
                '',
                {'table': {'head': ['Deed', 'What it means'],
                           'rows': [['Chanote (Nor Sor 4 Jor)',
                                     'Full title, surveyed with GPS markers. The one you want.'],
                                    ['Nor Sor 3 Gor',
                                     'Confirmed use rights, surveyed. Can usually be sold and upgraded.'],
                                    ['Condo title (Or Chor 2)', 'Title to a condo unit.'],
                                    ['Sor Kor 1, Por Bor Tor 5',
                                     'Possession or tax records, not ownership. Avoid.']]}}),
               ('What to bring',
                '',
                {'list': ["Buyer: passport, and for condos, the bank's foreign-exchange record for the "
                          'purchase money.',
                          'Seller: original title deed, ID card and house registration, or company '
                          'documents.',
                          "For condos: the juristic office's letter confirming no unpaid fees, and the "
                          'foreign-quota letter.',
                          'If someone acts for you: a Land Office power of attorney form, signed and '
                          'witnessed, with copies of your passport.']}),
               ('Fees and taxes',
                'The Land Office calculates the transfer fee (2%) on its own appraised value, which can '
                "differ from your price. Taxes on the seller's side depend on how long they owned it and "
                "whether it's a company. The table in [buying a condo](/homes/buy-condo-thailand/) shows the "
                'usual split.',
                {'note': "Pay at the Land Office by cashier's cheque or as the office directs. Never hand "
                         "cash for 'fees' to anyone outside the official counters."})],
  'faqs': [],
  'sources': [],
  'related': [('Buying a condo',
               'Quota, money transfer, due diligence, contract and transfer day, in order.',
               'homes/buy-condo-thailand/'),
              ('What foreigners can own',
               'Condo yes, land no, and the legal routes in between. Read this before any deposit.',
               'homes/foreign-ownership/'),
              ('Wills and documents',
               'A Thai will, certified translations, legalisation and finding a licensed lawyer.',
               'living/wills-and-documents/')],
  'next': ('Moving checklist', 'living/moving-checklist/')},
 {'slug': 'business/foreign-ownership',
  'title': 'Foreign Business Ownership in Thailand 2026: 49% Rule, BOI, Treaty of Amity',
  'description': 'How much of a Thai company a foreigner can own: Foreign Business Act lists, the 49% rule, '
                 'BOI promotion, business licences, the Treaty of Amity and nominee risks.',
  'template': 'editorial',
  'eyebrow': 'BUSINESS GUIDE',
  'heading': 'How much of a Thai business can you own?',
  'short': 'Business ownership rules',
  'intro': 'The Foreign Business Act reserves many activities for Thai-majority companies. For those, '
           'foreigners may own up to 49%. There are four lawful ways to own more, and one unlawful way that '
           'is now being prosecuted.',
  'image': 'home',
  'cards': [],
  'checklist': [],
  'sections': [('The three lists',
                '',
                {'after': ['Activities not on any list, such as manufacturing for export, are open to '
                           'foreign majority ownership.'],
                 'table': {'head': ['List', 'Covers', 'Foreign majority?'],
                           'rows': [['List 1',
                                     'Land trading, farming, media and other protected sectors',
                                     'Never'],
                                    ['List 2',
                                     'Activities touching national security, culture or natural resources',
                                     'Only with Cabinet approval; rare'],
                                    ['List 3',
                                     'Most services, including tourism, restaurants, real estate brokerage '
                                     'and many retail activities',
                                     'Only with a Foreign Business Licence, BOI promotion or a treaty']]}}),
               ('The lawful routes to majority ownership',
                '',
                {'list': ['**BOI promotion:** promoted activities (technology, manufacturing, some services) '
                          'can be 100% foreign-owned, with tax holidays. See [BOI](/business/boi/).',
                          '**Foreign Business Licence:** a licence for a List 3 activity, granted case by '
                          'case, with minimum capital of 3 million THB.',
                          '**US Treaty of Amity:** US citizens and US-controlled companies can own a '
                          'majority in most List 3 activities.',
                          '**Free trade agreements:** some agreements give limited rights to companies from '
                          'certain countries.']}),
               ('The nominee problem',
                '',
                {'after': ['A genuine Thai partner who invests their own money and shares the risk is '
                           'lawful. If your structure only works because a partner never invested, have a '
                           'licensed Thai lawyer restructure it the legal way now.'],
                 'warn': 'Putting Thai friends or staff on the share register to reach 51%, with your money '
                         'behind them, is illegal. The Department of Business Development is investigating '
                         'tens of thousands of companies in tourism, property, hotels and e-commerce, and '
                         'new registration checks took effect on 1 January 2026. Penalties include fines, '
                         'prison and loss of the business.'})],
  'faqs': [],
  'sources': ['g_department_of_business_develop', 'g_thailand_board_of_investment'],
  'related': [('Company setup',
               'Name, shareholders, capital, registration, tax and bank, in the order it happens.',
               'business/company-setup/'),
              ('BOI promotion',
               '100% foreign ownership, tax holidays and easier work permits for promoted activities.',
               'business/boi/'),
              ('Buying a business',
               'Shares or assets, the lease, licences and debts. What to check before you pay.',
               'business/buy-a-business/')],
  'next': ('Company setup', 'business/company-setup/')},
 {'slug': 'business/buy-a-business',
  'title': 'Buying a Business in Thailand as a Foreigner (2026): Due Diligence Guide',
  'description': 'How to buy a bar, restaurant, guesthouse or company in Thailand safely: shares versus '
                 'assets, leases and key money, licences, debts, staff and the nominee trap.',
  'template': 'editorial',
  'eyebrow': 'BUSINESS GUIDE',
  'heading': 'Buying an existing business in Thailand',
  'short': 'Buying a business',
  'intro': 'Buying a running business can be the fastest way into Thai commerce, and in Pattaya the '
           'riskiest. Some bars and restaurants are sold again and again because the lease, the licences or '
           "the numbers don't hold up. The checks below prevent most of it.",
  'image': 'home',
  'cards': [],
  'checklist': [],
  'sections': [('Shares or assets?',
                '',
                {'table': {'head': ['', "Buy the company's shares", 'Buy the business assets'],
                           'rows': [['What you get',
                                     'The company, with its history, contracts, debts and licences',
                                     'Equipment, stock, the name, and a new lease in your own company'],
                                    ['Risk',
                                     'Hidden debts and tax come with it',
                                     'Cleaner, but licences and the lease must be re-done'],
                                    ['Ownership limits',
                                     "The company's foreign shareholding must already be lawful",
                                     'Your company must be lawfully structured']]}}),
               ('The checks that matter',
                '',
                {'steps': ['**The lease.** How many years are left, is it registered, can it be transferred, '
                           "and what will the landlord charge? 'Key money' paid to the seller buys nothing "
                           "if the landlord won't renew.",
                           '**The licences.** Alcohol, food, entertainment and hotel licences are personal '
                           'or tied to the premises. Confirm they transfer.',
                           "**The shareholding.** If the company relies on nominee Thai shareholders, you'd "
                           'be buying a crime. See [foreign ownership](/business/foreign-ownership/).',
                           '**The numbers.** Ask for bank statements and tax filings, not just a '
                           'spreadsheet. Sit in the business on a slow weekday.',
                           '**Staff and debts.** Social security, unpaid wages, supplier debts and severance '
                           'owed to staff.'],
                 'warn': 'Never pay key money or a deposit before the lease and licences are confirmed in '
                         'writing by the landlord and the authorities.'})],
  'faqs': [],
  'sources': [],
  'related': [('Business ownership rules',
               'The 49% rule, the four lawful ways past it, and why nominees are now a serious risk.',
               'business/foreign-ownership/'),
              ('Invest',
               'Rental property and business stakes: real yields, real costs, lawful structures.',
               'invest/'),
              ('Company setup',
               'Name, shareholders, capital, registration, tax and bank, in the order it happens.',
               'business/company-setup/')],
  'next': ('Invest', 'invest/')},
 {'slug': 'living/driving-licence',
  'title': 'Thai Driving Licence for Foreigners 2026: Convert, New, Renew (Pattaya)',
  'description': 'Get a Thai driving licence as a foreigner: convert a foreign licence or IDP, sit the test, '
                 'renew from 2 to 5 years, car and motorbike, at the Banglamung DLT.',
  'template': 'editorial',
  'eyebrow': 'DAILY LIFE',
  'heading': 'Getting a Thai driving licence',
  'short': 'Driving licence',
  'intro': 'If you live here, get a Thai licence. An International Driving Permit only covers short stays, '
           'and insurers can refuse claims from residents without a Thai licence. For Pattaya, the office is '
           'the Department of Land Transport in Banglamung.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('Three ways to get one',
                '',
                {'table': {'head': ['Your situation', 'What you do'],
                           'rows': [['You hold a valid licence from home, or an IDP',
                                     'Convert it: colour, reaction and depth tests, a short training video, '
                                     'no driving test in most cases'],
                                    ['You have no licence for that vehicle',
                                     'Online or classroom training, a written test, then a practical test. A '
                                     '[driving school](#driving-schools) helps'],
                                    ['You already have a Thai licence',
                                     'Renew it: the first licence lasts 2 years, renewals 5 years']]}}),
               ("Documents you'll need",
                '',
                {'list': ['Passport with your visa and latest entry stamp. Most offices want a non-immigrant '
                          'visa or extension; some convert for visa-exempt visitors with proof of address.',
                          'A [residence certificate](/stay-legal/residence-certificate/) from immigration, '
                          'or your work permit.',
                          'A medical certificate from a clinic, issued within the last month (a few hundred '
                          'baht).',
                          "Your foreign licence or IDP, and a certified translation if it isn't in "
                          'English.']}),
               ('The day itself',
                '',
                {'steps': ["Book a queue slot through the DLT's online booking system or at the office.",
                           'Hand in documents and copies, then sit the colour-blindness, reaction (brake) '
                           'and depth-perception tests.',
                           'Watch the road-safety training video, or complete it online in advance.',
                           "Take the written and practical tests, if you're not converting.",
                           'Pay the small fee, have your photo taken and collect the card the same day.'],
                 'note': 'Do car and motorbike on the same visit; the tests are shared.'}),
               ('Driving schools',
                "If you've never ridden a motorbike or driven on the left, a few lessons at a licensed "
                'driving school are worth it. Many in Pattaya teach in English and can arrange the test at '
                'their own track, which DLT accepts.')],
  'faqs': [('Can I ride a rented scooter on my car licence?',
            'Legally, no: motorbikes need a motorbike category. Police checkpoints fine riders without the '
            "right licence, and travel insurance usually won't pay."),
           ('How do I renew from 2 years to 5 years?',
            'Before expiry, bring the same documents plus your current card, do the tests and a short '
            "training session, and you'll get a 5-year licence.")],
  'sources': [],
  'related': [('Residence certificate',
               "Immigration's letter confirming your address. Needed for a driving licence and more.",
               'stay-legal/residence-certificate/'),
              ('Getting around',
               'Baht buses, ride apps, airport transfers and renting a car or bike safely.',
               'living/getting-around-pattaya/'),
              ('Health insurance',
               'Thai or international, costs by age, and which visas require it.',
               'living/health-insurance/')],
  'next': ('Bank account', 'living/bank-account/')},
 {'slug': 'living/bank-account',
  'title': 'Opening a Thai Bank Account as a Foreigner (2026): Banks & Documents',
  'description': 'How foreigners open a Thai bank account: which banks to try, the documents they ask for, '
                 'visa requirements, mobile banking, and using it for visa money proof.',
  'template': 'editorial',
  'eyebrow': 'DAILY LIFE',
  'heading': 'Opening a Thai bank account',
  'short': 'Bank account',
  'intro': 'You need a Thai bank account to pay rent, to avoid 220 THB fees on every foreign-card '
           'withdrawal, and, for retirement and marriage extensions, to hold the money immigration checks. '
           'Banks are cautious with foreigners, so bring more paperwork than you think.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('What banks usually ask for',
                '',
                {'list': ['Passport with a non-immigrant visa or extension. Accounts on a visa-exempt stay '
                          'are increasingly refused.',
                          'Proof of address: a [residence certificate](/stay-legal/residence-certificate/), '
                          'lease or utility bill.',
                          'A Thai phone number in your name.',
                          'Sometimes a work permit, a letter from your embassy, or a reference from a Thai '
                          'account holder.']}),
               ('Which banks',
                'Bangkok Bank, Kasikorn (KBank), SCB and Krungsri are the most used by foreigners in '
                'Pattaya. Policies differ from branch to branch, so if one branch says no, another may say '
                'yes. Branches in shopping malls open at weekends.'),
               ("Once it's open",
                '',
                {'list': ['Set up the mobile banking app; Thai QR payments (PromptPay) are accepted almost '
                          'everywhere.',
                          'Keep the bank book updated: immigration reads it for retirement and marriage '
                          'extensions.',
                          'For property purchases, ask how the bank issues the foreign-exchange record '
                          'before you send money.']})],
  'faqs': [],
  'sources': [],
  'related': [('Retirement visa',
               'Age 50+? 800,000 THB in a Thai bank, or 65,000 THB a month, renewed every year.',
               'visas/retirement/'),
              ('Buying a condo',
               'Quota, money transfer, due diligence, contract and transfer day, in order.',
               'homes/buy-condo-thailand/'),
              ('Moving checklist',
               'Documents to pack, the first week and the first 30 days, in order.',
               'living/moving-checklist/')],
  'next': ('Driving licence', 'living/driving-licence/')},
 {'slug': 'living/health-insurance',
  'title': 'Health Insurance in Thailand for Expats (2026): Costs, Visas & Cover',
  'description': 'Health insurance for foreigners in Thailand: Thai vs international policies, premiums by '
                 'age, visas that require cover, pre-existing conditions, car insurance.',
  'template': 'editorial',
  'eyebrow': 'DAILY LIFE',
  'heading': 'Health insurance for life in Thailand',
  'short': 'Health insurance',
  'intro': 'Private hospitals in Thailand are excellent, and they bill like it. Good cover protects your '
           "savings, and several visas (the Non-O-A, the LTR) require it. Buy before you're older: many "
           'insurers stop accepting new customers somewhere around 70 to 75.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('Thai or international policy?',
                '',
                {'table': {'head': ['', 'Thai insurer', 'International insurer'],
                           'rows': [['Premium', 'Lower', 'Higher'],
                                    ['Cover outside Thailand',
                                     'Usually none, or limited',
                                     'Regional or worldwide'],
                                    ['Age limits for new policies',
                                     'Often around 70',
                                     'Some accept older applicants'],
                                    ['Visa certificates',
                                     'Usually issued in the format immigration expects',
                                     'Check that the certificate meets the visa wording']]}}),
               ('What it costs',
                'Inpatient-only cover from a Thai insurer starts at a few thousand baht a month for people '
                'in their 30s and 40s and rises steeply after 60. International comprehensive plans can cost '
                'several times more. Deductibles cut premiums a lot.'),
               ('Read the small print',
                '',
                {'list': ['Pre-existing conditions are excluded or loaded, often for two years or '
                          'permanently.',
                          'Outpatient cover is usually an add-on.',
                          'Accidents on a motorbike without the right [licence](/living/driving-licence/) '
                          'may not be covered.']}),
               ('Car and motorbike insurance',
                'Every vehicle needs compulsory third-party insurance (Por Ror Bor), renewed with the road '
                'tax. It covers very little. Add voluntary cover: Class 1 is comprehensive; Class 2+ and 3+ '
                'are cheaper middle options.')],
  'faqs': [],
  'sources': [],
  'related': [('Retirement visa',
               'Age 50+? 800,000 THB in a Thai bank, or 65,000 THB a month, renewed every year.',
               'visas/retirement/'),
              ('LTR visa',
               '10 years, a digital work permit and one yearly report, for higher earners and wealthy '
               'retirees.',
               'visas/ltr/'),
              ('Cost of living',
               'Monthly budgets for singles, couples and families, line by line, by city.',
               'living/cost-of-living/')],
  'next': ('Getting around', 'living/getting-around-pattaya/')},
 {'slug': 'living/getting-around-pattaya',
  'title': 'Getting Around Pattaya (2026): Baht Buses, Taxis, Airports, Car & Bike Hire',
  'description': 'How to get around Pattaya: baht bus routes and fares, ride apps, airport transfers to '
                 'Suvarnabhumi and U-Tapao, renting a car or motorbike safely, and what it costs.',
  'template': 'editorial',
  'eyebrow': 'DAILY LIFE',
  'heading': 'Getting around Pattaya',
  'short': 'Getting around',
  'intro': 'You can live well in Pattaya without a car. Baht buses run the main roads, ride apps cover the '
           'rest, and both airports are an easy transfer away.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('Everyday options',
                '',
                {'table': {'head': ['Option', 'Typical cost', 'Good to know'],
                           'rows': [['Baht bus (songthaew)',
                                     '10 to 20 THB a ride on fixed routes',
                                     'Hop on, press the buzzer to stop, pay the driver. Agree a price first '
                                     'if you hire one privately'],
                                    ['Bolt and Grab',
                                     '60 to 200 THB across town',
                                     'Price shown upfront; cars and motorbike taxis'],
                                    ['Motorbike taxi',
                                     '30 to 100 THB',
                                     'Drivers wear numbered vests; helmets required'],
                                    ['Car or scooter rental',
                                     'Scooter from about 3,000 THB a month; car from about 15,000 THB',
                                     'Licence and insurance matter: see below']]}}),
               ('Airports',
                '',
                {'list': ['**Suvarnabhumi (Bangkok):** about 1.5 to 2 hours. Private transfers from about '
                          '1,200 to 1,800 THB; buses run to Jomtien and North Pattaya.',
                          '**U-Tapao:** about 45 minutes south, with regional flights.',
                          '**Don Mueang (Bangkok):** about 2.5 hours, for budget airlines.']}),
               ('Renting a car or motorbike safely',
                '',
                {'list': ['Ride or drive only with the right [licence](/living/driving-licence/). Without '
                          "it, insurance won't pay.",
                          "Wear a helmet; it's the law and the checkpoints enforce it.",
                          'Photograph the vehicle before you take it, and read what the insurance excludes.',
                          'Never leave your passport as a deposit. Offer a cash deposit or a copy '
                          'instead.']})],
  'faqs': [],
  'sources': [],
  'related': [('Driving licence',
               'Convert your licence, sit the test, or renew: car and motorbike, all in one guide.',
               'living/driving-licence/'),
              ('Living in Pattaya',
               'Jomtien, Pratumnak, Naklua, East Pattaya and more, compared for daily life.',
               'living/pattaya/'),
              ('Home services',
               'Cleaners, air-con servicing, repairs, utilities and internet: who, how and how much.',
               'living/home-services/')],
  'next': ('Home services', 'living/home-services/')},
 {'slug': 'living/home-services',
  'title': 'Home Services in Pattaya (2026): Cleaning, Repairs, Air Con & Utilities',
  'description': 'Running a home in Pattaya: what cleaners, air-con servicing and repairs cost, paying '
                 'electricity and water, setting up internet, and dealing with condo management.',
  'template': 'editorial',
  'eyebrow': 'DAILY LIFE',
  'heading': 'Running your home in Pattaya',
  'short': 'Home services',
  'intro': 'The little things keep a home running in the tropics: air conditioners serviced, a reliable '
           "cleaner, a plumber who turns up. Here's what's normal and what it costs.",
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('What things cost',
                '',
                {'table': {'head': ['Service', 'Typical price (THB)'],
                           'rows': [['Cleaner',
                                     '300 to 500 an hour, or 1,000 to 2,000 for a condo deep clean'],
                                    ['Air-con service', '500 to 800 per unit; every 3 to 6 months'],
                                    ['Plumber or electrician call-out', '500 to 1,500 plus parts'],
                                    ['Pest control', '1,500 to 3,000 a visit, or a yearly contract'],
                                    ['Fibre internet', '500 to 1,000 a month']]}}),
               ('Utilities',
                '',
                {'list': ['Electricity is billed by PEA in houses, often by the building in condos. Ask '
                          'which rate you pay.',
                          'Water is cheap; bills of a few hundred baht are normal.',
                          'Internet: AIS, True and 3BB all install within days. Bring your passport and '
                          'lease.',
                          'Pay at 7-Eleven, by bank app or by direct debit.']}),
               ('Repairs in a rental',
                'Your landlord pays for wear and breakdowns; you pay for damage. Report problems in writing, '
                "with photos, the day they happen. In condos, the building's juristic office handles common "
                'areas and can recommend tradespeople.')],
  'faqs': [],
  'sources': [],
  'related': [('Renting in Pattaya',
               'Typical rents, deposits, contracts and the questions to ask before you sign.',
               'homes/rent-in-pattaya/'),
              ('Cost of living',
               'Monthly budgets for singles, couples and families, line by line, by city.',
               'living/cost-of-living/')],
  'next': ('Wills and documents', 'living/wills-and-documents/')},
 {'slug': 'living/wills-and-documents',
  'title': 'Thai Wills, Translations & Legalisation for Foreigners (2026)',
  'description': 'Making a Thai will for property and bank accounts, certified translation and legalisation '
                 'of documents, registering a marriage, and finding a licensed lawyer in Pattaya.',
  'template': 'editorial',
  'eyebrow': 'LEGAL AND DOCUMENTS',
  'heading': 'Wills, translations and legal paperwork',
  'short': 'Wills and documents',
  'intro': 'Two kinds of paperwork catch foreign residents out: a missing will, which leaves family facing '
           "months in a Thai court, and foreign documents that Thai offices won't accept until they're "
           'translated and legalised.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [('A Thai will',
                'If you own a condo, a car or a bank account here, make a Thai will for your Thai assets. '
                "It's simple: written (in Thai, or bilingual), signed in front of two witnesses who don't "
                'benefit, and naming an executor. Without one, your heirs need a court order, which takes '
                "months and a lawyer's fees, before a bank or the Land Office will act.",
                {'note': "Keep your home-country will for your other assets and make sure the two don't "
                         'contradict each other. A lawyer drafts both in one conversation.'}),
               ('Translation and legalisation',
                '',
                {'steps': ['Get the original document (birth, marriage, divorce or degree certificate) and '
                           'have it certified in the country that issued it.',
                           "Have it legalised by that country's embassy in Thailand, or apostilled at home "
                           'where accepted.',
                           'Get a certified Thai translation.',
                           "Have the translation legalised at the Ministry of Foreign Affairs' Department of "
                           'Consular Affairs.'],
                 'after': ['This chain is needed for marriage registration, family visas, some bank and land '
                           'office steps, and school enrolment.']}),
               ('Finding a lawyer',
                '',
                {'list': ["Ask for the lawyer's licence from the Lawyers Council of Thailand, and check it.",
                          'Get the scope and the fee in writing before work starts.',
                          "Be wary of anyone offering to make illegal structures 'work'. That advice costs "
                          'more than the fee.']})],
  'faqs': [],
  'sources': [],
  'related': [('Marriage visa',
               'Married to a Thai? 400,000 THB in the bank or 40,000 THB a month, renewed yearly.',
               'visas/marriage/'),
              ('What foreigners can own',
               'Condo yes, land no, and the legal routes in between. Read this before any deposit.',
               'homes/foreign-ownership/'),
              ('Business ownership rules',
               'The 49% rule, the four lawful ways past it, and why nominees are now a serious risk.',
               'business/foreign-ownership/')],
  'next': ('Stay legal', 'stay-legal/')},
 {'slug': 'faq',
  'title': 'Moving to Thailand FAQ: Visas, Homes, Money, Work & Daily Life',
  'description': 'Straight answers to the questions people ask before moving to Thailand: visas, working, '
                 'buying property, money, healthcare, driving, family and staying legal.',
  'template': 'editorial',
  'eyebrow': 'QUESTIONS',
  'heading': 'Questions people ask before moving',
  'short': 'FAQ',
  'intro': 'Short answers, with a link to the full guide for each.',
  'image': 'coast',
  'cards': [],
  'checklist': [],
  'sections': [],
  'faqs': [('What is the easiest long-stay visa?',
            'Under 50 and earning online: usually the [DTV](/visas/dtv/). Over 50 with savings: the '
            '[retirement visa](/visas/retirement/). Prefer to pay to skip paperwork: [Thailand '
            'Privilege](/visas/thailand-privilege/).'),
           ('Can I work in Thailand?',
            'Only with a [work permit](/visas/work-permit/). The DTV covers remote work for clients and '
            'employers outside Thailand.'),
           ('Can foreigners buy property?',
            'A condo, yes, in your own name. Land, no. Read [what foreigners can '
            'own](/homes/foreign-ownership/).'),
           ('How much money do I need?',
            'A couple lives comfortably in Pattaya on about 80,000 THB a month. Try the [cost '
            'calculator](/tools/cost-calculator/).'),
           ('Do I need health insurance?',
            'Some visas require it, and everyone should have it. See [health '
            'insurance](/living/health-insurance/).'),
           ('What are 90-day reports?',
            'A free address confirmation every 90 days of continuous stay. See [the 90-day '
            'report](/stay-legal/90-day-report/).'),
           ('Can I drive on my home licence?',
            'Briefly, with an International Driving Permit. Residents should get a [Thai '
            'licence](/living/driving-licence/).'),
           ('What happens if I overstay?',
            '500 THB a day, and bans for longer overstays. Read [overstay](/stay-legal/overstay/) and act '
            'early.'),
           ('Can my family come with me?', 'Yes, on most routes. See [family visas](/visas/family/).'),
           ('Do you guarantee visas?',
            'No. Nobody honest can. We choose a route you clearly qualify for and make the application as '
            'strong as it can be.')],
  'sources': [],
  'related': [('Start here',
               'The complete order for moving to Thailand: choose a visa, budget, pick an area, find a home, '
               'land and set up, then stay legal. Timelines and checklists.',
               'start-here/')],
  'next': ('Start here', 'start-here/')}]

PAGE_UPDATES = {'homes': {'sections': [],
           'faqs': [],
           'sources': [],
           'related': [],
           'next': ('Moving checklist', 'living/moving-checklist/'),
           'cards': [('Renting in Pattaya',
                      'Typical rents, deposits, contracts and the questions to ask before you sign.',
                      'homes/rent-in-pattaya/'),
                     ('What foreigners can own',
                      'Condo yes, land no, and the legal routes in between. Read this before any deposit.',
                      'homes/foreign-ownership/'),
                     ('Buying a condo',
                      'Quota, money transfer, due diligence, contract and transfer day, in order.',
                      'homes/buy-condo-thailand/'),
                     ('Land Office transfer',
                      'Documents, title deeds, fees and taxes for the day the property becomes yours.',
                      'homes/property-transfer/'),
                     ('Ownership checker',
                      'Three questions about what, whose name and where the money comes from.',
                      'tools/ownership-checker/')]},
 'homes/rent-in-pattaya': {'sections': [('What rent costs, by type',
                                         '',
                                         {'after': ['Six-month leases cost 10 to 20% more. Short lets of one '
                                                    'to three months cost more again, especially from '
                                                    'November to March.'],
                                          'table': {'head': ['Home', 'Typical monthly rent (THB)', 'Where'],
                                                    'rows': [['Studio condo',
                                                              '8,000 to 15,000',
                                                              'Central Pattaya, Jomtien, Naklua'],
                                                             ['1-bed condo',
                                                              '12,000 to 25,000',
                                                              'Most areas; sea views cost more'],
                                                             ['2-bed condo',
                                                              '25,000 to 50,000',
                                                              'Jomtien, Pratumnak, Wongamat'],
                                                             ['3-bed house with garden',
                                                              '25,000 to 60,000',
                                                              'East Pattaya, Huay Yai, Mabprachan'],
                                                             ['Pool villa',
                                                              '50,000 to 150,000+',
                                                              'East Pattaya, Na Jomtien, Bang Saray']]}}),
                                        ('What a normal lease looks like',
                                         '',
                                         {'list': ["**Deposit:** two months' rent, refunded at the end minus "
                                                   'damage. Plus the first month in advance.',
                                                   '**Length:** 12 months is standard; 6 months is '
                                                   'negotiable outside high season.',
                                                   '**Utilities:** you pay electricity and water. In condos, '
                                                   "check whether you're charged government rates or a "
                                                   'building mark-up.',
                                                   '**Included:** furniture, air conditioning, often '
                                                   "internet in condos. Common-area fees are the owner's.",
                                                   '**TM30:** the owner must file your [address '
                                                   'report](/stay-legal/tm30/) within 24 hours. Ask for the '
                                                   'receipt.']}),
                                        ('Before you sign',
                                         '',
                                         {'steps': ['View in the evening too: noise from bars, building '
                                                    'sites and roads changes after dark.',
                                                    'Photograph every room and existing damage, and attach '
                                                    'the photos to the contract.',
                                                    'Check the air conditioners were cleaned recently, the '
                                                    'water pressure and the mobile signal.',
                                                    "Get the contract in English and Thai, with the owner's "
                                                    'ID and title deed copy.',
                                                    'Agree in writing how and when the deposit is '
                                                    'returned.']}),
                                        ('Homes available now',
                                         'Our property partner [Pattaya Home '
                                         'Pro](https://pattayahomepro.com/for-rent/) lists rentals with '
                                         'prices and photos. Confirm current availability and terms for the '
                                         'exact home before paying anything.')],
                           'faqs': [('Can I rent before I arrive?',
                                     'Yes, by video viewing and a deposit. Safer still: take a short first '
                                     'lease or a serviced apartment for the first month, and commit once '
                                     "you've seen the area."),
                                    ('Do agents charge tenants?',
                                     "In Thailand the owner normally pays the agent's commission on a long "
                                     "lease. Be wary of anyone charging you a finder's fee for a standard "
                                     'rental.')],
                           'sources': [],
                           'related': [('Living in Pattaya',
                                        'Jomtien, Pratumnak, Naklua, East Pattaya and more, compared for '
                                        'daily life.',
                                        'living/pattaya/'),
                                       ('Buying a condo',
                                        'Quota, money transfer, due diligence, contract and transfer day, in '
                                        'order.',
                                        'homes/buy-condo-thailand/'),
                                       ('TM30 notification',
                                        'Your landlord tells immigration where you live within 24 hours. '
                                        'Keep the receipt.',
                                        'stay-legal/tm30/')],
                           'next': ('Moving checklist', 'living/moving-checklist/'),
                           'cards': []},
 'homes/buy-condo-thailand': {'sections': [('The steps',
                                            '',
                                            {'steps': ["**Choose and check the unit.** Ask the building's "
                                                       'juristic office whether foreign quota is available, '
                                                       'and for the common-fee and sinking-fund figures.',
                                                       '**Due diligence.** A lawyer checks the title deed '
                                                       "(chanote), the seller's right to sell, debts on the "
                                                       "unit, and the building's licences.",
                                                       '**Reservation and contract.** Pay a small '
                                                       'reservation, then sign a sale contract in English '
                                                       'and Thai with clear deadlines and refund terms.',
                                                       '**Send the money from abroad.** Transfer in foreign '
                                                       "currency to a Thai account, stating it's for buying "
                                                       'a condo. Ask the bank for the foreign-exchange '
                                                       'certificate (FET) or credit advice.',
                                                       '**Transfer at the Land Office.** Both sides or their '
                                                       'representatives attend, pay the fees and taxes, and '
                                                       'the title is registered in your name.']}),
                                           ('What it costs to transfer',
                                            '',
                                            {'after': ['Everything is negotiable, so write who pays what in '
                                                       'the contract. Off-plan buyers also pay into the '
                                                       "building's sinking fund at transfer."],
                                             'table': {'head': ['Cost', 'Rate', 'Usually paid by'],
                                                       'rows': [['Transfer fee',
                                                                 '2% of the appraised value',
                                                                 'Split 50/50, or as agreed'],
                                                                ['Specific business tax',
                                                                 '3.3%, if the seller owned it under 5 years',
                                                                 'Seller'],
                                                                ['Stamp duty',
                                                                 "0.5%, when business tax doesn't apply",
                                                                 'Seller'],
                                                                ['Withholding tax',
                                                                 'Varies with the seller and holding period',
                                                                 'Seller']]}}),
                                           ('New-build or resale?',
                                            'New-build (off-plan) units come with payment plans and '
                                            "developer warranties, but you're betting on completion and on "
                                            'the quota still being open. Resale units are what you see, with '
                                            'a history you can check. In Pattaya, resale units are often '
                                            'cheaper per square metre than new launches nearby.')],
                              'faqs': [('Can I get a mortgage?',
                                        'Thai banks rarely lend to foreigners without Thai income. Most '
                                        'buyers pay cash, use developer payment plans, or borrow at home.'),
                                       ('Do I need a lawyer?',
                                        "You don't legally have to, but you should. Due diligence costs a "
                                        "small fraction of the price and is the one step you can't fix "
                                        'later.')],
                              'sources': [],
                              'related': [('Land Office transfer',
                                           'Documents, title deeds, fees and taxes for the day the property '
                                           'becomes yours.',
                                           'homes/property-transfer/'),
                                          ('What foreigners can own',
                                           'Condo yes, land no, and the legal routes in between. Read this '
                                           'before any deposit.',
                                           'homes/foreign-ownership/'),
                                          ('Invest',
                                           'Rental property and business stakes: real yields, real costs, '
                                           'lawful structures.',
                                           'invest/')],
                              'next': ('Land Office transfer', 'homes/property-transfer/'),
                              'cards': []},
 'business': {'sections': [('Where to start',
                            '',
                            {'steps': ['Describe the business in one sentence: what you sell, to whom, and '
                                       'whether customers are in Thailand.',
                                       'Check whether that activity is restricted for foreigners: [foreign '
                                       'ownership rules](/business/foreign-ownership/).',
                                       'Choose the structure: Thai-majority company with real Thai partners, '
                                       'BOI promotion, a Foreign Business Licence, or the US Treaty of '
                                       'Amity.',
                                       'Register, open the bank account, and get your [work '
                                       'permit](/visas/work-permit/).']})],
              'faqs': [],
              'sources': [],
              'related': [],
              'next': ('Business ownership rules', 'business/foreign-ownership/'),
              'cards': [('Business ownership rules',
                         'The 49% rule, the four lawful ways past it, and why nominees are now a serious '
                         'risk.',
                         'business/foreign-ownership/'),
                        ('Company setup',
                         'Name, shareholders, capital, registration, tax and bank, in the order it happens.',
                         'business/company-setup/'),
                        ('BOI promotion',
                         '100% foreign ownership, tax holidays and easier work permits for promoted '
                         'activities.',
                         'business/boi/'),
                        ('Work permit',
                         'Required for any work in Thailand. How to get one, renew it and change jobs.',
                         'visas/work-permit/'),
                        ('Buying a business',
                         'Shares or assets, the lease, licences and debts. What to check before you pay.',
                         'business/buy-a-business/'),
                        ('Invest',
                         'Rental property and business stakes: real yields, real costs, lawful structures.',
                         'invest/')]},
 'business/company-setup': {'sections': [('Decide the basics',
                                          '',
                                          {'table': {'head': ['Decision', 'What to know'],
                                                     'rows': [['Shareholders',
                                                               'At least two. Foreign shareholding is '
                                                               'limited by the [Foreign Business '
                                                               'Act](/business/foreign-ownership/)'],
                                                              ['Capital',
                                                               'No legal minimum for Thai-majority '
                                                               'companies, but 2 million THB paid-up per '
                                                               'foreign work permit is the usual rule'],
                                                              ['Directors',
                                                               'One or more; foreigners can be directors'],
                                                              ['Office',
                                                               "A real address, with the owner's consent; "
                                                               'virtual offices cause problems at '
                                                               'work-permit time']]}}),
                                         ('The registration steps',
                                          '',
                                          {'steps': ['Reserve the company name online with the Department of '
                                                     'Business Development.',
                                                     'File the memorandum of association and hold the '
                                                     'statutory meeting.',
                                                     'Register the company, with the articles, shareholder '
                                                     "list and directors' details.",
                                                     'Get the corporate tax ID, and register for VAT if '
                                                     'turnover will exceed 1.8 million THB a year.',
                                                     'Open the company bank account and deposit the capital.',
                                                     'Register with social security and hire your Thai '
                                                     'staff.']}),
                                         ('Every year after',
                                          '',
                                          {'list': ['Monthly withholding tax and VAT returns, and social '
                                                    'security payments.',
                                                    'Audited accounts and an annual shareholder meeting.',
                                                    'Corporate income tax returns twice a year.'],
                                           'note': 'Keep an accountant from the first month. Missed filings '
                                                   'make work-permit renewals fail.'})],
                            'faqs': [],
                            'sources': [],
                            'related': [('Business ownership rules',
                                         'The 49% rule, the four lawful ways past it, and why nominees are '
                                         'now a serious risk.',
                                         'business/foreign-ownership/'),
                                        ('Business visa',
                                         'For employees and company owners. Comes with a work permit and '
                                         'yearly renewals.',
                                         'visas/business/'),
                                        ('Work permit',
                                         'Required for any work in Thailand. How to get one, renew it and '
                                         'change jobs.',
                                         'visas/work-permit/')],
                            'next': ('Business visa', 'visas/business/'),
                            'cards': []},
 'business/boi': {'sections': [('What BOI promotion can give you',
                                '',
                                {'list': ['100% foreign ownership in the promoted activity.',
                                          'Corporate income tax holidays, often 3 to 8 years, depending on '
                                          'the activity and location.',
                                          'Duty exemptions on machinery and some raw materials.',
                                          'Permission to own land for the promoted business.',
                                          'Smart visas and work permits through the One Stop Service '
                                          'Center.']}),
                               ('Who usually qualifies',
                                'Manufacturing, software and digital services, research, medical and green '
                                'industries, and regional headquarters. Ordinary local services such as '
                                'restaurants, bars and small trading usually do not.'),
                               ('The process',
                                '',
                                {'steps': ["Check that your activity is on the BOI's list, and the "
                                           'conditions attached (minimum investment, location, technology).',
                                           'Apply with a business plan and projections.',
                                           'Attend the BOI interview.',
                                           'On approval, set up the company and meet the conditions within '
                                           'the deadlines.']})],
                  'faqs': [],
                  'sources': ['g_thailand_board_of_investment'],
                  'related': [('Business ownership rules',
                               'The 49% rule, the four lawful ways past it, and why nominees are now a '
                               'serious risk.',
                               'business/foreign-ownership/'),
                              ('LTR visa',
                               '10 years, a digital work permit and one yearly report, for higher earners '
                               'and wealthy retirees.',
                               'visas/ltr/'),
                              ('Company setup',
                               'Name, shareholders, capital, registration, tax and bank, in the order it '
                               'happens.',
                               'business/company-setup/')],
                  'next': ('Company setup', 'business/company-setup/'),
                  'cards': []},
 'invest': {'sections': [('Rental property',
                          'Condos in Pattaya and Jomtien let well to long-stay foreigners and Thai '
                          'professionals. Net yields of 4 to 6% a year are realistic for well-chosen units '
                          'after fees, vacancies and management; gross figures in brochures are higher. Buy '
                          'near what renters want (beach, transport, shops) and in buildings with healthy '
                          'sinking funds.',
                          {'list': ['Running costs: common fees, sinking fund, insurance, management (often '
                                    '10 to 15% of rent), repairs and furnishing.',
                                    'Foreign buyers bring funds from abroad: see [buying a '
                                    'condo](/homes/buy-condo-thailand/).',
                                    'Rental income is taxable in Thailand; keep records.']}),
                         ('Business stakes',
                          'You can invest in a Thai company as a minority shareholder in restricted sectors, '
                          'or as a majority owner through [lawful routes](/business/foreign-ownership/). The '
                          'test is simple: would the structure survive an official check? If it relies on '
                          'nominees, the answer in 2026 is no.'),
                         ('Promises to walk away from',
                          '',
                          {'list': ['Guaranteed rental returns for years, paid by the developer. Price the '
                                    'unit without them.',
                                    "Buy-back promises from companies you can't check.",
                                    "Land ownership 'through our company' for a fee.",
                                    'Off-plan projects without a construction permit and an environmental '
                                    'approval.']})],
            'faqs': [],
            'sources': [],
            'related': [('Buying a condo',
                         'Quota, money transfer, due diligence, contract and transfer day, in order.',
                         'homes/buy-condo-thailand/'),
                        ('Buying a business',
                         'Shares or assets, the lease, licences and debts. What to check before you pay.',
                         'business/buy-a-business/'),
                        ('LTR visa',
                         '10 years, a digital work permit and one yearly report, for higher earners and '
                         'wealthy retirees.',
                         'visas/ltr/')],
            'next': ('Talk through your plans', 'contact/'),
            'cards': []},
 'living': {'sections': [],
            'faqs': [],
            'sources': [],
            'related': [],
            'next': ('Homes', 'homes/'),
            'cards': [('Living in Pattaya',
                       'Jomtien, Pratumnak, Naklua, East Pattaya and more, compared for daily life.',
                       'living/pattaya/'),
                      ('Cost of living',
                       'Monthly budgets for singles, couples and families, line by line, by city.',
                       'living/cost-of-living/'),
                      ('Moving checklist',
                       'Documents to pack, the first week and the first 30 days, in order.',
                       'living/moving-checklist/'),
                      ('Bank account',
                       'Which visa you need, which banks to try, and the documents to bring.',
                       'living/bank-account/'),
                      ('Driving licence',
                       'Convert your licence, sit the test, or renew: car and motorbike, all in one guide.',
                       'living/driving-licence/'),
                      ('Health insurance',
                       'Thai or international, costs by age, and which visas require it.',
                       'living/health-insurance/'),
                      ('Getting around',
                       'Baht buses, ride apps, airport transfers and renting a car or bike safely.',
                       'living/getting-around-pattaya/'),
                      ('Home services',
                       'Cleaners, air-con servicing, repairs, utilities and internet: who, how and how much.',
                       'living/home-services/'),
                      ('Wills and documents',
                       'A Thai will, certified translations, legalisation and finding a licensed lawyer.',
                       'living/wills-and-documents/'),
                      ('Cost calculator',
                       'Pick a city, household, home and lifestyle. See the monthly total, line by line.',
                       'tools/cost-calculator/')]},
 'living/pattaya': {'sections': [('The areas side by side',
                                  '',
                                  {'table': {'head': ['Area', 'Feels like', 'Best for', 'Homes'],
                                             'rows': [['Jomtien',
                                                       'Long beach, relaxed, lots of long-stay residents',
                                                       'Retirees, couples, first-timers',
                                                       'Condos of every age; good-value rentals'],
                                                      ['Pratumnak',
                                                       'Green hill between Pattaya and Jomtien, quiet',
                                                       'People who want calm near the centre',
                                                       'Mid to high-end condos, a few villas'],
                                                      ['Naklua and Wongamat',
                                                       'Northern beaches, more upmarket',
                                                       'Families and buyers wanting new builds',
                                                       'High-rise condos, sea views'],
                                                      ['Central Pattaya',
                                                       'Busy, walkable, everything open late',
                                                       'Short stays and people who want the action',
                                                       'Older condos and serviced apartments'],
                                                      ['East Pattaya',
                                                       'Green, spacious, villages and lakes',
                                                       'Families with pets, people who want a garden',
                                                       'Houses and pool villas in gated estates'],
                                                      ['Na Jomtien',
                                                       'Beachfront south of Jomtien, quieter',
                                                       'Long stays near the sea',
                                                       'Resort-style condos'],
                                                      ['Bang Saray',
                                                       'Fishing village 25 minutes south',
                                                       'People who want Thai village life',
                                                       'Villas and low-rise condos']]}}),
                                 ('What to check before choosing',
                                  '',
                                  {'list': ['**Schools:** most international schools are in East Pattaya and '
                                            'towards Sattahip; check the morning drive.',
                                            '**Hospitals:** the main private hospitals are in Central and '
                                            'North Pattaya; 15 minutes matters in an emergency.',
                                            '**Flooding:** some low-lying sois flood in heavy rain. Ask '
                                            'neighbours, not agents.',
                                            '**Noise:** building sites and bars change a street quickly. '
                                            'Visit at night.'],
                                   'note': 'Compare real listings by area on [Pattaya Home '
                                           'Pro](https://pattayahomepro.com/areas/jomtien/), our property '
                                           'partner.'})],
                    'faqs': [],
                    'sources': [],
                    'related': [('Renting in Pattaya',
                                 'Typical rents, deposits, contracts and the questions to ask before you '
                                 'sign.',
                                 'homes/rent-in-pattaya/'),
                                ('Cost of living',
                                 'Monthly budgets for singles, couples and families, line by line, by city.',
                                 'living/cost-of-living/'),
                                ('Getting around',
                                 'Baht buses, ride apps, airport transfers and renting a car or bike safely.',
                                 'living/getting-around-pattaya/')],
                    'next': ('Cost of living', 'living/cost-of-living/'),
                    'cards': []},
 'living/cost-of-living': {'sections': [('Typical monthly budgets in Pattaya',
                                         '',
                                         {'after': ['Simple means a 1-bed condo, cooking at home and baht '
                                                    'buses. Comfortable means a 2-bed condo, eating out '
                                                    'often and your own scooter. Premium means a house or '
                                                    'sea-view condo, a car and imported food. Bangkok and '
                                                    'Phuket run about 25 to 30% higher; Chiang Mai about 20% '
                                                    'lower.'],
                                          'table': {'head': ['Household', 'Simple', 'Comfortable', 'Premium'],
                                                    'rows': [['Single',
                                                              '35,000 THB',
                                                              '55,000 THB',
                                                              '100,000+ THB'],
                                                             ['Couple',
                                                              '50,000 THB',
                                                              '80,000 THB',
                                                              '150,000+ THB'],
                                                             ['Family of four',
                                                              '90,000 THB',
                                                              '150,000 THB',
                                                              '250,000+ THB']]}}),
                                        ('The line items',
                                         '',
                                         {'table': {'head': ['Item', 'Typical cost (THB a month)'],
                                                    'rows': [['Rent',
                                                              'See [renting in '
                                                              'Pattaya](/homes/rent-in-pattaya/): 12,000 to '
                                                              '50,000 for most condos'],
                                                             ['Electricity',
                                                              '1,500 to 6,000; air conditioning is the big '
                                                              'variable'],
                                                             ['Water and internet', '800 to 1,500'],
                                                             ['Phone plan', '300 to 800'],
                                                             ['Thai food',
                                                              '80 to 150 a meal at local places'],
                                                             ['Western food', '300 to 800 a meal'],
                                                             ['Health insurance',
                                                              '3,000 to 15,000 per adult, rising with age'],
                                                             ['International school',
                                                              'From 30,000 per child, often far more']]}}),
                                        ('Build your own number',
                                         'Use the [cost calculator](/tools/cost-calculator/) for your city, '
                                         'household and lifestyle. Then add a buffer of 10%: the first '
                                         'months always cost more while you buy the things a furnished '
                                         "rental doesn't include.")],
                           'faqs': [],
                           'sources': [],
                           'related': [('Health insurance',
                                        'Thai or international, costs by age, and which visas require it.',
                                        'living/health-insurance/'),
                                       ('Renting in Pattaya',
                                        'Typical rents, deposits, contracts and the questions to ask before '
                                        'you sign.',
                                        'homes/rent-in-pattaya/')],
                           'next': ('Homes', 'homes/'),
                           'cards': []},
 'living/moving-checklist': {'sections': [('Before you fly',
                                           '',
                                           {'list': ['Visa approved and printed. See [visas](/visas/).',
                                                     'Passport valid for 18+ months, with blank pages.',
                                                     'Bank statements, pension or salary proof, and copies.',
                                                     'Marriage and birth certificates, legalised if needed: '
                                                     '[documents](/living/wills-and-documents/).',
                                                     'Driving licence plus an International Driving Permit.',
                                                     '[Health insurance](/living/health-insurance/) active '
                                                     'from day one.',
                                                     "First month's accommodation booked, and viewings "
                                                     'arranged: [renting](/homes/rent-in-pattaya/).']}),
                                          ('First week',
                                           '',
                                           {'list': ['Thai SIM card, at the airport or a phone shop, with '
                                                     'your passport.',
                                                     'Move in, inspect and photograph the home, collect keys '
                                                     'and the contract.',
                                                     'Landlord files your [TM30](/stay-legal/tm30/). Get the '
                                                     'receipt.',
                                                     'Download Bolt or Grab for transport and food, and '
                                                     'learn the [baht bus '
                                                     'routes](/living/getting-around-pattaya/).']}),
                                          ('First 30 days',
                                           '',
                                           {'list': ['Open a [bank account](/living/bank-account/).',
                                                     'Get a [residence '
                                                     'certificate](/stay-legal/residence-certificate/), then '
                                                     'a [Thai driving licence](/living/driving-licence/).',
                                                     'Register with a hospital and a dentist; keep your '
                                                     'insurance card in your wallet.',
                                                     'Put your [90-day report](/stay-legal/90-day-report/) '
                                                     'and [extension](/stay-legal/extension-of-stay/) dates '
                                                     'in your calendar.']}),
                                          ('Every year',
                                           '',
                                           {'list': ['Extension of stay, and the money test that goes with '
                                                     'it.',
                                                     '90-day reports, unless your visa replaces them.',
                                                     'Re-entry permit before every trip abroad: [re-entry '
                                                     'permits](/stay-legal/re-entry-permit/).',
                                                     "Driving licence renewal when it's due."]})],
                             'faqs': [],
                             'sources': [],
                             'related': [('Start here',
                                          'The complete order for moving to Thailand: choose a visa, budget, '
                                          'pick an area, find a home, land and set up, then stay legal. '
                                          'Timelines and checklists.',
                                          'start-here/'),
                                         ('Bank account',
                                          'Which visa you need, which banks to try, and the documents to '
                                          'bring.',
                                          'living/bank-account/')],
                             'next': ('Stay legal', 'stay-legal/'),
                             'cards': []}}

VISA_UPDATES = {'dtv': {'sections': [('Who the DTV is for',
                       '',
                       {'list': ['**Remote workers and freelancers** paid by companies or clients outside '
                                 "Thailand. You'll show an employment contract, client contracts or a "
                                 'business registration abroad, plus a portfolio or profile.',
                                 '**Soft-power participants**: Muay Thai, Thai cooking, Thai language, '
                                 "seminars, sports events, music and medical treatment. You'll need a letter "
                                 'from the gym, school or hospital.',
                                 '**Spouses and children under 20** of a main DTV holder can apply as '
                                 'dependants.'],
                        'note': 'The DTV does not allow you to work for a Thai company or serve Thai '
                                'customers. If that is your plan, you need a [business visa and work '
                                'permit](/visas/business/).'}),
                      ('The requirements',
                       '',
                       {'after': ['Embassies apply the rules differently. Some ask for longer statement '
                                  'histories, proof of address in the country you apply from, or a letter '
                                  "explaining your work. Check your file against that embassy's current list "
                                  'before you submit.'],
                        'table': {'head': ['What', 'Detail'],
                                  'rows': [['Age', '20 or over'],
                                           ['Money',
                                            '500,000 THB or equivalent in your own name, usually shown by 3 '
                                            'to 6 months of bank statements'],
                                           ['Purpose evidence',
                                            'Remote work: contracts, payslips, company or client details. '
                                            'Soft power: an enrolment or confirmation letter from a Thai '
                                            'provider'],
                                           ['Passport',
                                            'At least 6 months validity; more is better, since your stays '
                                            'are capped by it'],
                                           ['Where to apply',
                                            "Thailand's e-Visa system, from outside Thailand, through the "
                                            'embassy covering where you live']]}}),
                      ('How long you can stay',
                       'Each entry gives you 180 days. You can extend once per entry by another 180 days at '
                       'a Thai immigration office for 1,900 THB, so a single entry can last up to a year. '
                       'Leave and come back, and the clock restarts.',
                       {'paras': ["On longer stays you'll still do a [90-day "
                                  'report](/stay-legal/90-day-report/) and your landlord files a '
                                  '[TM30](/stay-legal/tm30/). Keep an eye on tax: since 2024, foreign income '
                                  'brought into Thailand in a year when you are tax-resident (180+ days) can '
                                  'be taxable. Ask a tax adviser about your case.']}),
                      ('How to apply, step by step',
                       '',
                       {'steps': ['Confirm you qualify: income source abroad, or a soft-power letter, plus '
                                  '500,000 THB in your own account.',
                                  'Gather documents: passport scan, photo, 3 to 6 months of statements, '
                                  "contracts or the provider letter, proof of address where you'll apply.",
                                  "Apply on Thailand's official e-Visa website and pay the 10,000 THB fee "
                                  '(charged in local currency).',
                                  'Wait for the decision, typically 1 to 3 weeks. Print the approval.',
                                  'Fly in, then plan your 90-day reports and the optional 180-day '
                                  'extension.']}),
                      ('Common reasons DTV applications fail',
                       '',
                       {'list': ['Savings topped up just before applying, with no history.',
                                 "Contracts that don't show who pays you or that the client is outside "
                                 'Thailand.',
                                 "A soft-power letter from a provider that doesn't match the course you "
                                 'describe.',
                                 'Applying through an embassy in a country where you are only visiting.']})],
         'faqs': [('Can I apply for a DTV from inside Thailand?',
                   'Not as a standard route. Applications go through the e-Visa system to an embassy outside '
                   'Thailand. Many people make a short trip to a nearby country to apply; check that '
                   "embassy's current rules first."),
                  ('Does the money have to stay in my account?',
                   'You must show it when you apply. Keep a healthy balance afterwards too: re-entry and '
                   'extension officers can ask about your means of support.'),
                  ('Can I bring my family?',
                   'Yes. A spouse and children under 20 can apply as dependants. Each dependant needs their '
                   'own application and fee.')],
         'sources': ['g_thai_e_visa_official_website', 'g_royal_thai_embassy_information'],
         'related': [('LTR visa',
                      '10 years, a digital work permit and one yearly report, for higher earners and wealthy '
                      'retirees.',
                      'visas/ltr/'),
                     ('Education visa',
                      'For enrolled students. Often the DTV is better for Muay Thai and cooking courses.',
                      'visas/education/'),
                     ('90-day report',
                      'Due every 90 days of continuous stay. File online, in person or through an agent.',
                      'stay-legal/90-day-report/')],
         'next': ('Cost of living', 'living/cost-of-living/')},
 'ltr': {'sections': [('The four ways to qualify',
                       '',
                       {'after': ['Every applicant also needs health insurance (or a deposit) at the level '
                                  'the BOI sets. The criteria were eased in January 2025, so thresholds '
                                  "differ from many older articles. Check your figures against the BOI's "
                                  'current list.'],
                        'table': {'head': ['Type', 'Who it fits', 'The core test'],
                                  'rows': [['Wealthy Global Citizen',
                                            'People with significant wealth',
                                            'At least US$1 million in assets and US$500,000 invested in '
                                            'Thailand (bonds, property or a business), plus income of around '
                                            'US$80,000 a year'],
                                           ['Wealthy Pensioner',
                                            'Retirees aged 50+',
                                            'Pension or passive income of US$80,000 a year, or US$40,000 '
                                            'plus US$250,000 invested in Thailand'],
                                           ['Work-from-Thailand Professional',
                                            'Remote employees of established foreign companies',
                                            "Income of around US$80,000 a year (lower with a master's degree "
                                            'or other qualifications), from a sizeable overseas employer'],
                                           ['Highly-Skilled Professional',
                                            'Specialists in targeted industries',
                                            "Income of around US$80,000 a year, or less with a master's "
                                            'degree or for some research and government roles']]}}),
                      ('What you get',
                       '',
                       {'list': ['10 years of residence, renewed after the first 5 if you still qualify.',
                                 'An annual address report instead of [90-day '
                                 'reports](/stay-legal/90-day-report/).',
                                 'A digital work permit for the job the visa is based on.',
                                 'Fast-track lanes at major airports.',
                                 'A flat 17% personal income tax rate for Highly-Skilled Professionals.',
                                 'Visas for a spouse and children under 20.']}),
                      ('How the application works',
                       '',
                       {'steps': ['Pick your category and gather income, asset and insurance evidence.',
                                  "Apply online through the BOI's LTR system, which pre-screens eligibility.",
                                  'After BOI endorsement, collect the visa at a Thai embassy or at the One '
                                  'Stop Service Center in Thailand.',
                                  'Pay the 50,000 THB fee and register your digital work permit if you will '
                                  'work.']})],
         'faqs': [('Is the LTR better than Thailand Privilege?',
                   "If you qualify, usually yes: it's cheaper and you can work. Privilege suits people who "
                   "don't meet the income tests or just want the simplest route. See [Thailand "
                   'Privilege](/visas/thailand-privilege/).'),
                  ('How long does approval take?',
                   'The BOI aims for about 20 working days after a complete file, but missing documents add '
                   'weeks. Allow two months.')],
         'sources': ['g_boi_long_term_resident_visa_po'],
         'related': [('Thailand Privilege',
                      '5 to 20 years with no income test and VIP airport help. From 900,000 THB.',
                      'visas/thailand-privilege/'),
                     ('DTV visa',
                      '5 years, 180 days per entry, for remote workers and Muay Thai, cooking or culture '
                      'students.',
                      'visas/dtv/'),
                     ('Permanent residence',
                      'After 3 years of yearly extensions. A small yearly quota, a long process, real '
                      'benefits.',
                      'visas/permanent-residence/')],
         'next': ('Cost of living', 'living/cost-of-living/')},
 'thailand-privilege': {'sections': [('The tiers in 2026',
                                      '',
                                      {'after': ['The cheaper Bronze tier (650,000 THB) was withdrawn at the '
                                                 'end of 2025. Prices and promotions change; Thailand '
                                                 'Privilege sometimes runs family offers.'],
                                       'table': {'head': ['Tier', 'Fee (THB)', 'Length', 'Good to know'],
                                                 'rows': [['Gold',
                                                           '900,000',
                                                           '5 years',
                                                           'The entry tier now that Bronze is closed'],
                                                          ['Platinum',
                                                           '1,500,000',
                                                           '10 years',
                                                           'Family members can be added at a lower price'],
                                                          ['Diamond',
                                                           '2,500,000',
                                                           '15 years',
                                                           'More service points each year'],
                                                          ['Reserve',
                                                           '5,000,000',
                                                           '20 years',
                                                           'By invitation']]}}),
                                     ('What membership includes',
                                      '',
                                      {'list': ['A Privilege visa stamped for the length of your membership, '
                                                'with multiple entries.',
                                                'Airport assistance and fast track on arrival and departure '
                                                'at major airports.',
                                                'Help with [90-day reports](/stay-legal/90-day-report/) and '
                                                'some government paperwork.',
                                                'Yearly service points for lounges, limousine transfers, spa '
                                                'or health checks, depending on tier.']}),
                                     ("Who it suits, and who it doesn't",
                                      "**It suits** people who travel in and out often, can't easily "
                                      "document income, or value time over money. It's also popular with "
                                      'families who want every member on the same long visa.',
                                      {'paras': ["**It doesn't suit** anyone who needs to work in Thailand: "
                                                 'membership gives no work rights. If you have high income, '
                                                 'compare the [LTR](/visas/ltr/), which is far cheaper for '
                                                 '10 years.']}),
                                     ('How to apply',
                                      '',
                                      {'steps': ['Choose the tier and apply with a passport copy and photo. '
                                                 'A background check follows.',
                                                 'On approval, pay the membership fee.',
                                                 'Receive your e-visa or have it stamped on arrival, '
                                                 'depending on where you are.']})],
                        'faqs': [('Does Thailand Privilege let me buy property?',
                                  "It doesn't change ownership law. As a foreigner you can own a condo unit; "
                                  'land rules are the same for everyone. See [what foreigners can '
                                  'own](/homes/foreign-ownership/).'),
                                 ('Is the fee refundable?',
                                  'No. Treat it as a cost, not an investment, and compare it with the '
                                  'alternatives first.')],
                        'sources': ['g_thailand_privilege_card_co_off'],
                        'related': [('LTR visa',
                                     '10 years, a digital work permit and one yearly report, for higher '
                                     'earners and wealthy retirees.',
                                     'visas/ltr/'),
                                    ('Retirement visa',
                                     'Age 50+? 800,000 THB in a Thai bank, or 65,000 THB a month, renewed '
                                     'every year.',
                                     'visas/retirement/'),
                                    ('Re-entry permit',
                                     'Leaving Thailand on an extension? Without this permit, the extension '
                                     'ends at the border.',
                                     'stay-legal/re-entry-permit/')],
                        'next': ('Cost of living', 'living/cost-of-living/')},
 'retirement': {'sections': [('The money rule',
                              'You must show one of these, every year:',
                              {'list': ['**800,000 THB in a Thai bank account** in your name. It must be '
                                        'there at least 2 months before you apply, and stay at that level '
                                        'for 3 months after; for the rest of the year it must not drop below '
                                        '400,000 THB.',
                                        '**Monthly income of at least 65,000 THB**, shown with an embassy '
                                        'letter or by transfers from abroad into your Thai account.',
                                        '**A combination** of income and savings adding up to 800,000 THB a '
                                        'year.'],
                               'warn': 'Immigration checks the bank book page by page. Money parked for a '
                                       'weekend, or a balance that dips at the wrong time, is the most '
                                       'common reason we see retirement extensions refused.'}),
                             ('Non-O or O-A?',
                              '',
                              {'after': ['Many retirees enter first and convert to a Non-O at immigration '
                                         'once their Thai bank account is in place. Whether you can convert '
                                         'depends on how you entered and your nationality, so check before '
                                         'you fly.'],
                               'table': {'head': ['', 'Non-O (retirement)', 'Non-O-A'],
                                         'rows': [['Where you start',
                                                   'Often converted inside Thailand at immigration, or '
                                                   'issued abroad',
                                                   'Applied for at a Thai embassy in your home country'],
                                                  ['Health insurance',
                                                   'Not required for the visa itself',
                                                   'Required, at the level the embassy sets (commonly around '
                                                   'US$100,000 cover)'],
                                                  ['Extensions',
                                                   'Yearly, with the money rule',
                                                   'Yearly, money rule plus continuing insurance']]}}),
                             ('Renewing every year',
                              '',
                              {'steps': ['Two to three months before expiry: make sure the bank balance (or '
                                         'income transfers) meets the rule.',
                                         'Up to 45 days before expiry: get a bank letter dated the same day '
                                         'you apply, and update your bank book.',
                                         'Apply at immigration with passport, TM.7 form, photo, bank letter '
                                         'and book, your [TM30](/stay-legal/tm30/) receipt and a map to your '
                                         'home.',
                                         "Pay 1,900 THB. You'll usually get a 'under consideration' stamp, "
                                         'then the full year about a month later.',
                                         'Leaving Thailand? Get a [re-entry '
                                         'permit](/stay-legal/re-entry-permit/) first, or the extension is '
                                         'cancelled.']})],
                'faqs': [('Can I work on a retirement visa?',
                          'No. Volunteering is grey too. If you want to work, look at the [business visa and '
                          'work permit](/visas/business/).'),
                         ('Can my younger partner join me?',
                          "Yes, as a dependant on a Non-O, provided you're married. Unmarried partners need "
                          'their own visa.'),
                         ('Is there a 10-year retirement visa?',
                          'Citizens of a few countries can apply for the Non-O-X, which has higher money '
                          'requirements. For most people, the [LTR Wealthy Pensioner](/visas/ltr/) is the '
                          'long option.')],
                'sources': ['g_thai_immigration_bureau', 'g_thai_e_visa_official_website'],
                'related': [('Extensions and renewals',
                             'How yearly extensions work for retirement, marriage, business, family and '
                             'student visas.',
                             'stay-legal/extension-of-stay/'),
                            ('Bank account',
                             'Which visa you need, which banks to try, and the documents to bring.',
                             'living/bank-account/'),
                            ('Health insurance',
                             'Thai or international, costs by age, and which visas require it.',
                             'living/health-insurance/')],
                'next': ('Living in Pattaya', 'living/pattaya/')},
 'marriage': {'sections': [('What you need',
                            '',
                            {'list': ['A marriage registered at a Thai district office (amphur), or a '
                                      'foreign marriage registered in Thailand. The certificate is called '
                                      'Kor Ror 2 or 3 (and Kor Ror 22 for foreign marriages).',
                                      '**400,000 THB** in a Thai bank account in your name for at least 2 '
                                      'months, or **40,000 THB a month** in income.',
                                      "Your spouse's ID card and house registration book (tabien baan).",
                                      'Photos of you together at home, and sometimes a simple map.']}),
                           ('The yearly extension',
                            '',
                            {'steps': ['Apply at your immigration office with your spouse. Both of you '
                                       'usually need to attend.',
                                       "Bring the bank letter and book, marriage certificate, your spouse's "
                                       'ID and house book, photos and the TM.7 form.',
                                       "Expect a 30-day 'under consideration' stamp and a home visit by an "
                                       'officer during that period.',
                                       "Return to collect the full year's extension."],
                             'note': 'Officers want to see a genuine shared life: clothes in the wardrobe, '
                                     'wedding photos, neighbours who know you. Paper marriages are '
                                     'prosecuted.'})],
              'faqs': [('Do we need to live together?',
                        'Yes. The extension is based on supporting your family in Thailand, and the home '
                        'visit checks it.'),
                       ('What if we separate?',
                        'The extension ends with the marriage. Plan early; you may qualify for another route '
                        'such as [retirement](/visas/retirement/).')],
              'sources': ['g_thai_immigration_bureau'],
              'related': [('Family visas',
                           'For parents of Thai children, dependants of visa holders and parents of '
                           'students.',
                           'visas/family/'),
                          ('Wills and documents',
                           'A Thai will, certified translations, legalisation and finding a licensed lawyer.',
                           'living/wills-and-documents/'),
                          ('Extensions and renewals',
                           'How yearly extensions work for retirement, marriage, business, family and '
                           'student visas.',
                           'stay-legal/extension-of-stay/')],
              'next': ('Living in Pattaya', 'living/pattaya/')},
 'education': {'sections': [('Who qualifies',
                             '',
                             {'list': ['Students enrolled full time at a Thai university or international '
                                       'school.',
                                       'Students at a Ministry of Education licensed Thai language school, '
                                       'for courses of a set number of hours.',
                                       'Trainees at some licensed Muay Thai and vocational schools.']}),
                            ('How it works',
                             '',
                             {'steps': ['Enrol and pay the school. They send you an acceptance letter and '
                                        'the documents for the embassy.',
                                        'Apply for the Non-ED through the e-Visa system. It is usually '
                                        'issued for 90 days.',
                                        'Extend at immigration with a school letter, normally every 90 days '
                                        'or yearly depending on the course.',
                                        'Attend. Officers may ask you to speak or read Thai at the '
                                        'extension.']}),
                            ('DTV or education visa?',
                             'For Muay Thai, Thai cooking and short courses, the [DTV](/visas/dtv/) is '
                             'usually better if you have 500,000 THB in savings: five years and 180 days per '
                             'entry instead of 90-day steps. The education visa makes sense for full-time '
                             'degrees, children at school, and people without the DTV savings.')],
               'faqs': [('Can I work part time on an education visa?', 'No, not without a work permit.'),
                        ('Can my parent stay with me?',
                         'A parent of a school-age student can apply for a [guardian '
                         'visa](/visas/family/).')],
               'sources': [],
               'related': [('DTV visa',
                            '5 years, 180 days per entry, for remote workers and Muay Thai, cooking or '
                            'culture students.',
                            'visas/dtv/'),
                           ('Family visas',
                            'For parents of Thai children, dependants of visa holders and parents of '
                            'students.',
                            'visas/family/'),
                           ('90-day report',
                            'Due every 90 days of continuous stay. File online, in person or through an '
                            'agent.',
                            'stay-legal/90-day-report/')],
               'next': ('Living in Pattaya', 'living/pattaya/')},
 'business': {'sections': [('What the company must have',
                            '',
                            {'list': ['**Registered capital of 2 million THB** for each foreign employee, '
                                      'fully paid up (some BOI-promoted and other companies have lower '
                                      'thresholds).',
                                      '**Four Thai employees** on the social security system for each work '
                                      'permit.',
                                      '**A salary** for you at or above the minimum immigration expects for '
                                      'your nationality (often 50,000 THB a month for Western nationals).',
                                      'Tax filings up to date, and an office the company actually uses.']}),
                           ('Getting the visa and permit',
                            '',
                            {'steps': ['The company prepares its documents: registration, shareholder list, '
                                       'tax and social security filings, financial statements.',
                                       'Apply for the Non-B through the e-Visa system or a Thai embassy, '
                                       'usually issued for 90 days.',
                                       'Once in Thailand, apply for the work permit at the Department of '
                                       'Employment.',
                                       'Extend your stay for a year at immigration, with the work permit and '
                                       "the company's documents."]}),
                           ('Renewing each year',
                            'Renewals repeat the company checks: capital, Thai staff, salary and tax. If the '
                            "company falls short, the extension is refused, so check the company's numbers a "
                            'month before your date. See [extension of '
                            'stay](/stay-legal/extension-of-stay/).')],
              'faqs': [('Can I set up my own company and give myself a work permit?',
                        'Yes, if the company is properly structured and meets the capital and Thai staff '
                        'rules. Read [company setup](/business/company-setup/) and [foreign ownership '
                        'rules](/business/foreign-ownership/) first.'),
                       ('Is there an investment visa?',
                        'Investment can support certain routes, such as the [LTR Wealthy Global '
                        'Citizen](/visas/ltr/) or [Thailand Privilege](/visas/thailand-privilege/). Older '
                        'condo-investment visas exist on paper but are rarely the best option now.')],
              'sources': [],
              'related': [('Work permit',
                           'Required for any work in Thailand. How to get one, renew it and change jobs.',
                           'visas/work-permit/'),
                          ('Company setup',
                           'Name, shareholders, capital, registration, tax and bank, in the order it '
                           'happens.',
                           'business/company-setup/'),
                          ('BOI promotion',
                           '100% foreign ownership, tax holidays and easier work permits for promoted '
                           'activities.',
                           'business/boi/')],
              'next': ('Business & invest', 'business/')}}
