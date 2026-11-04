"""Where the old WordPress URLs of ledadpro.com go now that the static site is live.

Built from the WordPress sitemaps and every page Search Console has shown in the last
16 months (Nov 2026). Old posts get a 301 to the closest new page, so their rankings
and links carry over; leftover real-estate theme pages answer 410 Gone.

ledadpro_build.py writes these as Apache rules to sites/ledadpro-live/redirects.conf;
vps/live-deploy.sh puts them in the site's .htaccess block. WordPress itself stays
(wp-admin, uploads, privacy policy and terms keep working).
"""

TO = {
    '/services/led-caravan/': ['led-advertising-truck-rental-in-bangladesh', 'led-covered-van-mobile-advertising-in-bangladesh',
                               'portable-led-screen-advertising-in-bangladesh', 'led-car-branding'],
    '/pricing/': ['billboard-cost-in-dhaka', 'led-billboard-price-in-bd', 'billboard-price-in-bangladesh',
                  'outdoor-led-display-screen-price-in-bangladesh'],
    '/locations/': ['billboard-locations-in-bangladesh', 'digital-billboards-in-bangladesh', 'digital-billboard-bangladesh',
                    'billboard-bangladesh', 'led-billboard-bangladesh',
                    'digital-billboards-in-bangladesh-with-led-ad-pro-bangladeshs-no-1-led-advertising-agency',
                    'continental-hotel-shahbag-led-advertising-billboard', 'baipayl-savar-led-advertising-billboard',
                    'abdullahpur-led-advertising-billboard'],
    '/led-screen-rental/': ['led-screen-rental-bangladesh', 'led-screen-rental-service-bangladesh', 'digital-screen-rent-dhaka',
                            'digital-screen-setup', 'indoor-led-advertising-in-bangladesh', 'indoor-led-branding',
                            'led-signage-in-bangladesh', 'digital-signage-display-branding-in-bangladesh-2025'],
    '/about/': ['best-advertising-agency-in-bangladesh', 'best-billboard-advertising-agency-in-bangladesh',
                'advertising-agency-in-bangladesh', 'billboard-advertising-agency-in-dhaka',
                'billboard-advertising-agency-in-bangladesh', 'advertising-in-bangladesh',
                'six-years-of-ledadpro-advertising-in-bangladesh', 'led-billboard-installation', 'billboard-setup-adn'],
    '/guides/how-to-choose-a-billboard-location/': ['billboard-marketing-strategies'],
    '/#contact': ['contact', 'contact-us'],
    '/': ['led-ooh-advertising', 'billboard-advertising-bangladesh', 'billboard-advertising-bangladesh-2',
          'billboard-advertising-in-bangladesh', 'billboard-advertising-in-bangladesh-2', 'digital-screen-advertising-in-bangladesh',
          'best-billboard-advertising-in-bangladesh', 'led-screen-advertising-bangladesh', 'led-branding-in-bangladesh',
          'led-advertising-billboard-in-bangladesh', 'outdoor-advertising', 'out-of-home-advertising', 'billboard-advertising',
          'pillar-light-box-bangladesh', 'pillar-light-box-bangladesh-high-impact-outdoor-advertising-solutions',
          'blog', 'news', 'news-and-updates', 'elementor-4064'],
    # old single-screen posts -> their area page
    '/locations/gulshan/': ['led-advertising-billboard-in-gulshan', 'led-advertising-in-gulshan', 'gulshan-1-led-billboard',
                            'gulshan-2-baridhara-facing', 'gulshan-banani-facing', 'gulshan-1-g1-facing-led-billboard',
                            'police-plaza-gulshan-1-led-billboard'],
    '/locations/tejgaon/': ['police-plaza-gmg-mor-led-advertising-billboard', 'tejgaon-led-advertising-billboard'],
    '/locations/mirpur/': ['mirpur-10-led-advertising-billboard'],
    '/locations/rajshahi/': ['rda-market-shaheb-bazar-rajshahi', 'new-market-rajshahi-led-advertising-billboard'],
    '/locations/cumilla/': ['townhall-cumilla-led-advertising-billboard'],
    '/locations/chattogram/': ['gec-mor-chattogram-led-advertising-billboard'],
    '/locations/bogura/': ['shat-matha-mor-bogura-led-advertising-billboard'],
    '/locations/sadarghat/': ['shadarghat-led-advertising-billboard', 'sadarghat-fire-service-led-advertising-billboard'],
    '/locations/sylhet/': ['uposhohor-pomt-sylhet', 'naripul-point-sylhet', 'jitumiah-point-sylhet-led-advertising-billboard',
                           'chowkideki-point-sylhet'],
    '/locations/dhanmondi/': ['dhanmondi-27', 'dhanmondi-2-led-billboard', 'shimanto-square-led-advertising-billboardminipole'],
    '/locations/karwan-bazar/': ['bashundhara-city-led-billboard'],
    '/locations/mohakhali/': ['mohakhali-led-advertising-billboard', 'mohakhali-flyover-led-advertising-billboard'],
    '/locations/airport/': ['airport-led-billboard-by-led-ad-pro'],
}

# Pages of the real-estate theme the WordPress site once used: nothing to send them to.
GONE = ['new-property', 'my-properties', 'my-profile', 'my-invoices', 'my-favorites', 'my-saved-searches', 'packages',
        'payment-invoice', 'payment-completed', 'login', 'register', 'compare', 'advanced-search']

# WordPress pages that stay as they are.
KEEP = ['privacy-policy', 'terms', 'wp-json', 'feed']


def rules():
    seen = set()
    out = ['# Old WordPress URLs (tools/ledadpro_redirects.py)']
    for target, slugs in TO.items():
        for s in slugs:
            assert s not in seen, s
            seen.add(s)
            out.append(f'RewriteRule ^index\\.php/{s}/?$ {target} [R=301,L,NE]')
    out.append('RewriteRule ^index\\.php/(' + '|'.join(GONE) + ')/?$ - [G,L]')
    out.append('RewriteRule ^index\\.php/(tag|category|author)/ / [R=301,L]')
    out.append('RewriteRule ^index\\.php/[0-9]{4}/([0-9]{2}/)?$ / [R=301,L]')
    # Any other old post is a former screen or topic post: the locations hub is the closest fit.
    out.append('RewriteCond %{REQUEST_URI} !^/index\\.php/(' + '|'.join(KEEP) + ')(/|$)')
    out.append('RewriteRule ^index\\.php/[^/]+/?$ /locations/ [R=301,L]')
    # The WordPress sitemaps now list only redirected pages; the static sitemap replaces them.
    out.append('RewriteRule ^wp-sitemap.*\\.xml$ - [G,L]')
    return '\n'.join(out) + '\n'


def count():
    return sum(len(v) for v in TO.values())
