"""Build the Second Home Thailand site and its WordPress route manifest.

Concierge pages are written for this site (sht/content.py). Guides, visa routes and the
Visa Finder reuse Move In Thailand's copy (mit/content.py) in this site's design, with a
canonical link to the Move In Thailand original so search engines see one source.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup, escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def load(name, path):
    # Both sites name their copy content.py; load each under its own module name.
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    sys.path.pop(0)
    return module


sht = load('sht_content', HERE/'content.py')
mit = load('mit_content', ROOT/'mit'/'content.py')
CHECKED, MIT_PAGES, ROUTE_SPECS, SOURCES, VISAS = mit.CHECKED, mit.PAGES, mit.ROUTE_SPECS, mit.SOURCES, mit.VISAS

DOMAIN = 'secondhomethailand.com'
SITE = 'https://' + DOMAIN + '/'
SISTER = 'https://moveinthailand.com/'
# Move In Thailand pages that describe that business rather than the shared guide library.
NOT_SHARED = {'about', 'privacy', 'services', 'residency-care', 'contact', 'fees', 'tools', 'visas', ''}
SHARED_TEMPLATES = {'editorial': 'guide', 'visa': 'guide', 'finder': 'finder'}
HUBS = [('Residency routes', 'visas'), ('Staying legal', 'stay-legal'), ('Homes & property', 'homes'), ('Living in Thailand', 'living'), ('Business & investment', 'business'), ('Start here', 'start-here')]

ICONS = {
    'arrow': '<path d="M4 12h15m-6-6 6 6-6 6"/>',
    'external': '<path d="M14 4h6v6m0-6L10 14"/><path d="M10 4H5v15h15v-5"/>',
    'plus': '<path d="M12 4v16M4 12h16"/>',
}


def icon(name):
    if name not in ICONS:
        raise ValueError(f'Unknown icon: {name}')
    return Markup('<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">' + ICONS[name] + '</svg>')


def own_pages():
    def page(slug, template, title, description, **extra):
        return {'slug': slug, 'template': template, 'title': title, 'description': description, 'shared': False, **extra}
    return [
        page('', 'home', 'Second Home Thailand | Residency Concierge for Your Life in Thailand', 'A private residency desk for people making Thailand their second home: route strategy, applications, homes, arrival and renewals, planned once and agreed in writing.'),
        page('concierge', 'concierge', 'Concierge Services | Residency, Home & Arrival in Thailand | Second Home Thailand', 'Route Review, the full Residency Programme and ongoing Residency Care. Fixed scope and fee, agreed in writing before any paid work starts.', short='Concierge'),
        page('approach', 'approach', 'Our Approach | How Second Home Thailand Works', 'Fit before speed, written scope, official sources and no promises we cannot keep. How a Second Home Thailand engagement runs, from consultation to renewals.', short='Approach'),
        page('visas', 'routes', 'Thailand Residency Routes Compared | Privilege, LTR, Retirement & DTV', 'Compare Thailand’s long-stay routes side by side: length of stay, who each suits, the money test and whether you can work.', short='Routes'),
        page('library', 'library', 'Thailand Residency Library | Visas, Homes, Living & Staying Legal', 'Practical, source-linked guides for living in Thailand long term: visas, reports and extensions, property, banking, insurance and daily life.', short='Library'),
        page('contact', 'contact', 'Schedule a Consultation | Second Home Thailand', 'Tell us about the move you have in mind. A first consultation about your route, your home and your timeline, with no obligation.', short='Consultation'),
        page('privacy', 'privacy', 'Privacy | Second Home Thailand', 'What the consultation form collects, why, where it is kept, how long, and the choices you have. No tracking cookies.', short='Privacy'),
    ]


def shared_pages():
    pages = []
    for page in MIT_PAGES:
        if page['slug'] in NOT_SHARED or page['slug'].startswith('tools/') and page['template'] != 'finder' or page['template'] not in SHARED_TEMPLATES:
            continue
        copy = dict(page, shared=True, layout=SHARED_TEMPLATES[page['template']])
        copy['title'] = re.sub(r'\s*\|\s*Move In Thailand\s*$', '', copy['title']) + ' | Second Home Thailand'
        pages.append(copy)
    return pages


def structured_data(page, faqs):
    canonical = SITE + (page['slug'] + '/' if page['slug'] else '')
    entries = [
        {'@type': 'Organization', '@id': SITE + '#organization', 'name': 'Second Home Thailand', 'url': SITE, 'logo': SITE + 'wp-content/sht-site/assets/mark.png'},
        {'@type': 'WebSite', '@id': SITE + '#website', 'name': 'Second Home Thailand', 'url': SITE, 'inLanguage': 'en'},
        {'@type': 'WebPage', '@id': canonical + '#page', 'url': canonical, 'name': page['title'], 'description': page['description'], 'isPartOf': {'@id': SITE + '#website'}, 'inLanguage': 'en'},
    ]
    if page['slug']:
        entries.append({'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE}, {'@type': 'ListItem', 'position': 2, 'name': page['title'].split('|')[0].strip(), 'item': canonical}]})
    if faqs:
        entries.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]})
    return {'@context': 'https://schema.org', '@graph': entries}


def build(output: Path, preview: bool):
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    asset_source = HERE/'assets'
    required = ['site.css', 'motion.js', 'mark.svg', 'mark.png', 'og.png', 'fonts/anton-latin-400-normal.woff2', 'fonts/inter-latin-400-normal.woff2', 'fonts/inter-latin-500-normal.woff2', 'fonts/inter-latin-600-normal.woff2', 'fonts/martian-mono-latin-400-normal.woff2']
    missing = [name for name in required if not (asset_source/name).is_file()]
    if missing:
        raise SystemExit('Missing prepared assets: ' + ', '.join(missing))
    shutil.copytree(asset_source, output/'assets')
    # The enquiry form and Visa Finder run on Move In Thailand's tested script, pointed at this site's config.
    shared_js = (ROOT/'mit'/'assets'/'site.js').read_text(encoding='utf-8').replace("'mit-config'", "'sht-config'").replace("'wp-json/mit/v1/'", "'wp-json/sht/v1/'").replace('Move In Thailand: small, local tools', 'Second Home Thailand: small, local tools (shared with Move In Thailand)')
    (output/'assets'/'site.js').write_text(shared_js, encoding='utf-8')
    asset_prefix = '/assets/' if preview else '/wp-content/sht-site/assets/'
    version = hashlib.sha256(b''.join((output/'assets'/name).read_bytes() for name in ('site.css', 'site.js', 'motion.js'))).hexdigest()[:10]

    pages = own_pages() + shared_pages()
    known = {page['slug'] for page in pages}

    def asset(path):
        return asset_prefix + path + ('?v=' + version if path.endswith(('.css', '.js')) else '')

    def url(path):
        # Links to pages this site does not carry (calculators, fees) go to Move In Thailand.
        path = path.lstrip('/')
        route = urlsplit(path).path.strip('/')
        if path.startswith('wp-json/') or route in known:
            return '/' + path
        return SISTER + path

    def md(text):
        out = str(escape(text or ''))
        out = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{m[2]}" target="_blank" rel="noopener">{m[1]}</a>' if m[2].startswith('http') else f'<a href="{url(m[2])}">{m[1]}</a>', out)
        return Markup(re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', out))

    by_slug = {page['slug']: page for page in pages}

    def label(page):
        hub = {slug: name for name, slug in HUBS}.get(page['slug'])
        if hub and page['shared']:
            return hub
        if page.get('short'):
            return page['short']
        if page.get('visa'):
            return page['visa']['short']
        return page['title'].split('|')[0].split(':')[0].strip()

    def guides_in(prefix):
        return [page for page in pages if page['shared'] and page['layout'] == 'guide' and (page['slug'] == prefix or page['slug'].startswith(prefix + '/'))]

    photos = json.loads((asset_source/'photos'/'photos.json').read_text())

    def photo(name, cls='', sizes='100vw', eager=False, alt=None):
        # Responsive WebP with explicit dimensions, so pages do not shift while photos load.
        if name not in photos:
            raise ValueError(f'Unknown photo: {name}')
        widths = sorted(photos[name]['sizes'])
        width, height = widths[-1]
        srcset = ', '.join(f"{asset(f'photos/{name}-{w}.webp')} {w}w" for w, _ in widths)
        text = sht.PHOTOS[name] if alt is None else alt
        return Markup(f'<img class="{escape(cls)}" src="{asset(f"photos/{name}-{widths[0][0]}.webp")}" srcset="{srcset}" sizes="{escape(sizes)}" width="{width}" height="{height}" alt="{escape(text)}" loading="{"eager" if eager else "lazy"}" decoding="async">')

    guide_count = sum(1 for page in pages if page['shared'] and page['layout'] == 'guide')
    route_count = len(VISAS) + sum(1 for page in MIT_PAGES if page['slug'].startswith('visas/') and page['template'] == 'editorial')
    metrics = [(guide_count, 'Guides in the library'), (route_count, 'Residency routes compared'), (len(SOURCES), 'Official sources linked')]
    env = Environment(loader=FileSystemLoader(HERE/'templates'), autoescape=True, undefined=StrictUndefined, keep_trailing_newline=True)
    env.filters['md'] = md
    env.globals.update(icon=icon, photo=photo, url=url, asset=asset, label=label, by_slug=by_slug, guides_in=guides_in, hubs=HUBS, hub_names={slug: name for name, slug in HUBS}, metrics=metrics,
                       route_specs=ROUTE_SPECS, visas=VISAS, checked=CHECKED, source_map=SOURCES, sht=sht, sister=SISTER, site=SITE)
    config = {'basePath': '/', 'apiBase': '/wp-json/sht/v1/', 'preview': preview, 'checked': CHECKED, 'visas': {visa['slug']: {'name': visa['name']} for visa in VISAS}, 'fees': {}, 'whatsapp': ''}
    routes = []
    for page in pages:
        slug = page['slug']
        relative = (slug + '/' if slug else '') + 'index.html'
        destination = output/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        template = page['layout'] if page['shared'] else page['template']
        faqs = sht.FAQ if template == 'home' else page.get('visa', {}).get('faqs', page.get('faqs', []))
        canonical = (SISTER if page['shared'] else SITE) + (slug + '/' if slug else '')
        html = env.get_template(template + '.html.j2').render(page=page, faqs=faqs, canonical=canonical, config=config, schema=structured_data(page, faqs), preview=preview)
        destination.write_text(html, encoding='utf-8')
        main = re.search(r'<!--sht-content-start-->(.*?)<!--sht-content-end-->', html, re.S)
        if not main:
            raise SystemExit(f'No editable page region: {slug}')
        routes.append({'path': '/' + slug + '/' if slug else '/', 'file': relative, 'slug': slug or 'home', 'title': page['title'], 'description': page['description'],
                       'canonical': canonical, 'content_hash': hashlib.sha256(('<!-- wp:html -->' + main[1] + '<!-- /wp:html -->').encode('utf-8')).hexdigest()})
    (output/'404.html').write_text(env.get_template('404.html.j2').render(page={'slug': '404', 'template': '404', 'title': 'Page not found | Second Home Thailand', 'description': 'This page is not part of Second Home Thailand.', 'shared': False},
                                                                           faqs=[], canonical=SITE, config=config, schema={}, preview=preview), encoding='utf-8')
    known_paths = {route['path'].rstrip('/') or '/' for route in routes}
    for file in [route['file'] for route in routes] + ['404.html']:
        html = (output/file).read_text(encoding='utf-8')
        for target in re.findall(r'(?:href|src)="([^"]+)"', html):
            path = urlsplit(target).path
            if path.startswith(asset_prefix):
                if not (output/'assets'/path[len(asset_prefix):]).is_file():
                    raise SystemExit(f'Missing asset {path} in {file}')
            elif target.startswith('/') and not path.startswith('/wp-json/') and (path.rstrip('/') or '/') not in known_paths:
                raise SystemExit(f'Unknown internal link {target} in {file}')
    content_version = hashlib.sha256(json.dumps(routes, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
    # The old template's pages, posts and author archive fold into the new site.
    aliases = {'/home/': '/', '/sample-page/': '/', '/about/': '/approach/', '/about-us/': '/approach/', '/services/': '/concierge/', '/our-services/': '/concierge/', '/pricing/': '/concierge/', '/contact-us/': '/contact/', '/blog/': '/library/', '/news/': '/library/'}
    manifest = {'version': version, 'content_version': content_version, 'built_at': date.today().isoformat(), 'domain': DOMAIN, 'routes': routes, 'aliases': aliases}
    (output/'routes.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    # Only this site's own pages are listed; shared guides point search engines to Move In Thailand.
    listed = [route for route in routes if route['canonical'].startswith(SITE)]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('<url><loc>' + xml_escape(SITE.rstrip('/') + route['path']) + '</loc><lastmod>' + manifest['built_at'] + '</lastmod></url>\n' for route in listed) + '</urlset>\n'
    (output/'sitemap.xml').write_text(sitemap, encoding='utf-8')
    (output/'release.json').write_text(json.dumps({'site': 'Second Home Thailand', 'version': version, 'pages': len(routes), 'listed': len(listed)}), encoding='utf-8')
    print(f'Built {len(routes)} pages ({len(listed)} in the sitemap) in {output} ({"preview" if preview else "production"}).')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(ROOT/'.cache'/'sht-build'))
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args()
    build(Path(args.output).resolve(), args.preview)
