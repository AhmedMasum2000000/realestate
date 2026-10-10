"""Build the editorial site and its WordPress route manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from content import CALCULATOR_DEFAULTS, CHECKED, FAQ as FAQS, PAGES, SERVICES, SOURCES, VISAS

ICONS = {
    'arrow':'<path d="M4 12h15m-6-6 6 6-6 6"/>',
    'external':'<path d="M14 4h6v6m0-6L10 14"/><path d="M10 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5"/>',
    'check':'<path d="m5 12 4 4L19 6"/>',
    'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
    'compass':'<circle cx="12" cy="12" r="9"/><path d="m15.7 8.3-2.5 5-5 2.5 2.5-5 5-2.5Z"/>',
    'shield':'<path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/>',
    'receipt':'<path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z"/><path d="M9 8h6M9 12h6"/>',
    'pin':'<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    'sun':'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
    'laptop':'<rect x="5" y="4" width="14" height="12" rx="1"/><path d="M3 20h18l-2-4H5l-2 4Z"/>',
    'heart':'<path d="M20 5.5c-2-2-5-1.7-8 1-3-2.7-6-3-8-1C-1 11 12 21 12 21S25 11 20 5.5Z"/>',
    'briefcase':'<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V3h8v4M3 13c6 3 12 3 18 0M12 12v5"/>',
    'spark':'<path d="m12 3 2.3 6.7L21 12l-6.7 2.3L12 21l-2.3-6.7L3 12l6.7-2.3L12 3Z"/>',
    'home':'<path d="m3 10 9-7 9 7M5 9v12h14V9M9 21v-7h6v7"/>',
    'passport':'<rect x="5" y="2" width="14" height="20" rx="2"/><circle cx="12" cy="10" r="4"/><path d="M8 10h8m-4-4c-2 3-2 5 0 8 2-3 2-5 0-8ZM9 18h6"/>',
    'download':'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
    'book':'<path d="M3 4h6l3 2 3-2h6v15h-6l-3 2-3-2H3V4ZM12 6v15"/>',
    'calendar':'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18M7 14h3m4 0h3"/>',
    'users':'<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3m2-17a3 3 0 0 1 0 6m1 5c2 0 3 2 3 4v2"/>',
}

def icon(name):
    if name not in ICONS:
        raise ValueError(f'Unknown icon: {name}')
    return Markup('<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">' + ICONS[name] + '</svg>')

def structured_data(page):
    canonical = 'https://moveinthailand.com/' + (page['slug'] + '/' if page['slug'] else '')
    entries = [
        {'@type':'Organization','@id':'https://moveinthailand.com/#organization','name':'Move In Thailand','url':'https://moveinthailand.com/','logo':'https://moveinthailand.com/wp-content/mit-site/assets/logo.png'},
        {'@type':'WebSite','@id':'https://moveinthailand.com/#website','name':'Move In Thailand','url':'https://moveinthailand.com/','inLanguage':'en'},
        {'@type':'WebPage','@id':canonical+'#page','url':canonical,'name':page['title'],'description':page['description'],'isPartOf':{'@id':'https://moveinthailand.com/#website'},'inLanguage':'en'},
    ]
    if page['slug']:
        entries.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Home','item':'https://moveinthailand.com/'},{'@type':'ListItem','position':2,'name':page['title'].split('|')[0].strip(),'item':canonical}]})
    faqs = FAQS if page['template'] in ('home','visas') else page.get('visa',{}).get('faqs',page.get('faqs',[]))
    if faqs:
        entries.append({'@type':'FAQPage','mainEntity':[{'@type':'Question','name':question,'acceptedAnswer':{'@type':'Answer','text':answer}} for question,answer in faqs]})
    return {'@context':'https://schema.org','@graph':entries}

def build(output: Path, preview: bool):
    output.mkdir(parents=True,exist_ok=True)
    asset_source = HERE/'assets'
    required = ['logo.png','coast.webp','home.webp','fonts/rubik-400.woff2','fonts/rubik-500.woff2','moving-checklist.pdf','site.css','site.js']
    missing = [name for name in required if not (asset_source/name).is_file()]
    if missing:
        raise SystemExit('Missing prepared assets: ' + ', '.join(missing))
    shutil.copytree(asset_source, output/'assets', dirs_exist_ok=True)
    asset_prefix = '/assets/' if preview else '/wp-content/mit-site/assets/'
    version = hashlib.sha256((asset_source/'site.css').read_bytes() + (asset_source/'site.js').read_bytes()).hexdigest()[:10]
    def asset(path):
        return asset_prefix + path + ('?v='+version if path.endswith(('.css','.js')) else '')
    def url(path):
        return '/' + path.lstrip('/')
    env=Environment(loader=FileSystemLoader(HERE/'templates'),autoescape=True,undefined=StrictUndefined,keep_trailing_newline=True)
    env.globals.update(icon=icon,url=url,asset=asset)
    routes=[]
    config={'basePath':'/','apiBase':'/wp-json/mit/v1/','preview':preview,'checked':CHECKED,'visas':{visa['slug']:{'name':visa['name']} for visa in VISAS},'fees':{},'whatsapp':''}
    for page in PAGES:
        slug=page['slug'].strip('/')
        relative=(slug+'/' if slug else '')+'index.html'
        destination=output/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        html=env.get_template(page['template']+'.html.j2').render(page=page,visas=VISAS,services=SERVICES,faqs=FAQS,calculator=CALCULATOR_DEFAULTS,checked=CHECKED,source_map=SOURCES,config=config,schema=structured_data(page),preview=preview)
        destination.write_text(html,encoding='utf-8')
        main=re.search(r'<!--mit-content-start-->(.*?)<!--mit-content-end-->',html,re.S)
        if not main:
            raise SystemExit(f'No editable page region: {slug}')
        routes.append({'path':'/'+slug+'/' if slug else '/','file':relative,'slug':slug or 'home','title':page['title'],'description':page['description'],'content_hash':hashlib.sha256(('<!-- wp:html -->'+main[1]+'<!-- /wp:html -->').encode('utf-8')).hexdigest()})
    # Check generated internal destinations while compiling the site.
    known_paths={route['path'].rstrip('/') or '/' for route in routes}
    for route in routes:
        html=(output/route['file']).read_text(encoding='utf-8')
        for target in re.findall(r'(?:href|src)="([^"]+)"',html):
            path=urlsplit(target).path
            if path.startswith(asset_prefix):
                if not (output/'assets'/path[len(asset_prefix):]).is_file():
                    raise SystemExit(f'Missing asset {path} in {route["path"]}')
            elif target.startswith('/') and not path.startswith('/wp-json/') and (path.rstrip('/') or '/') not in known_paths:
                raise SystemExit(f'Unknown internal link {target} in {route["path"]}')
    content_version=hashlib.sha256(json.dumps(routes,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()[:16]
    manifest={'version':version,'content_version':content_version,'built_at':date.today().isoformat(),'domain':'moveinthailand.com','routes':routes,'aliases':{'/services-2/':'/services/','/about-2/':'/about/','/contact-2/':'/contact/'}}
    (output/'routes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+xml_escape('https://moveinthailand.com'+route['path'])+'</loc><lastmod>2026-10-08</lastmod></url>\n' for route in routes)+'</urlset>\n'
    (output/'sitemap.xml').write_text(sitemap,encoding='utf-8')
    (output/'release.json').write_text(json.dumps({'site':'Move In Thailand','version':version,'pages':len(routes)}),encoding='utf-8')
    print(f'Built {len(routes)} pages in {output} ({"preview" if preview else "production"}).')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default=str(ROOT/'.cache'/'mit-build'))
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    build(Path(args.output).resolve(),args.preview)
