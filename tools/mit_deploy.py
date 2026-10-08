"""Deploy only the Move In Thailand editorial folder and its MU plugin.

The original WordPress theme, pages, plugins, configuration and uploads stay
in place. Previously deployed editorial files are retained outside webroot.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import urlparse
import requests

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rep.cpanel import CpanelClient

DOMAIN='moveinthailand.com'

def ensure_dir(client,parent,name):
    path=(parent.rstrip('/')+'/' if parent else '')+name
    if not client.exists(path): client.mkdir(parent or client.home,name)
    return path

def deploy(build,release):
    if not release or not all(char.isalnum() or char=='-' for char in release):
        raise SystemExit('A safe release name is required.')
    manifest=json.loads((build/'routes.json').read_text(encoding='utf-8'))
    if manifest['domain']!=DOMAIN or len(manifest['routes'])<25:
        raise SystemExit('Unexpected site manifest.')
    host=os.environ['CPANEL_HOST'].strip()
    if host.startswith('https://'): host=urlparse(host).hostname
    client=CpanelClient(host,os.environ['CPANEL_USER'],os.environ['CPANEL_API_TOKEN'],dry_run=False)
    root=client.docroot(DOMAIN).strip('/')
    if root.startswith('home/'):
        prefix=client.home.strip('/')+'/'
        if root.startswith(prefix): root=root[len(prefix):]
    if root!=DOMAIN or not client.exists(root+'/wp-config.php'):
        raise SystemExit('Domain root or existing WordPress installation did not match. No deployment performed.')
    content=root+'/wp-content'
    if not client.exists(content): raise SystemExit('WordPress content folder was not found.')
    staging_parent=ensure_dir(client,'','mit-deployments')
    staging=ensure_dir(client,staging_parent,release)
    package=ROOT/'.cache'/('mit-'+release+'.zip');package.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(build.rglob('*')):
            if file.is_file(): archive.write(file,'mit-site/'+file.relative_to(build).as_posix())
        archive.write(ROOT/'mit'/'wordpress'/'mit-experience.php','mu-plugins/mit-experience.php')
    client.upload(package,staging)
    client.extract(staging+'/'+package.name,staging)
    new_site=staging+'/mit-site';new_plugin=staging+'/mu-plugins/mit-experience.php'
    for path in (new_site+'/index.html',new_site+'/routes.json',new_site+'/assets/site.js',new_plugin):
        if not client.exists(path): raise SystemExit('Staged release was incomplete; live files were not switched.')
    ensure_dir(client,content,'mu-plugins')
    live_site=content+'/mit-site';live_plugin=content+'/mu-plugins/mit-experience.php'
    previous_site=staging+'/previous-mit-site';previous_plugin=staging+'/previous-mit-experience.php'
    had_site=client.exists(live_site);had_plugin=client.exists(live_plugin)
    switched_site=False;switched_plugin=False
    def move(source,destination):
        # API 2 receives absolute, checked paths for both sides of every move.
        for path in (source,destination):
            if path.startswith('/') or '..' in path.split('/') or not (path.startswith(content+'/') or path.startswith(staging+'/')):
                raise RuntimeError('File move escaped the named release or website folder.')
        return client.rename(client.home.rstrip('/')+'/'+source,client.home.rstrip('/')+'/'+destination)
    try:
        if had_site: move(live_site,previous_site)
        move(new_site,live_site);switched_site=True
        if had_plugin: move(live_plugin,previous_plugin)
        move(new_plugin,live_plugin);switched_plugin=True
        # Read the published release. GETs do not create an enquiry or send email.
        public='https://'+DOMAIN
        expected=manifest['version']
        response=requests.get(public+'/wp-content/mit-site/release.json',params={'release':release},timeout=45)
        response.raise_for_status()
        if response.json().get('version')!=expected: raise RuntimeError('The public release version did not match.')
        homepage=requests.get(public+'/',params={'mit_release':release},headers={'Cache-Control':'no-cache'},timeout=60)
        homepage.raise_for_status()
        if 'Your next chapter.' not in homepage.text or 'mit-config' not in homepage.text:
            raise RuntimeError('The published homepage did not show the editorial experience.')
        guide=requests.get(public+'/tools/visa-finder/',params={'mit_release':release},timeout=45)
        guide.raise_for_status()
        if 'id="visa-finder"' not in guide.text: raise RuntimeError('The Visa Finder page was not served by WordPress.')
        bootstrap=requests.get(public+'/wp-json/mit/v1/bootstrap',headers={'Cache-Control':'no-cache'},timeout=45)
        bootstrap.raise_for_status()
        if not bootstrap.json().get('token'): raise RuntimeError('The secure enquiry bootstrap was unavailable.')
    except Exception:
        if switched_plugin: move(live_plugin,staging+'/failed-mit-experience.php')
        if had_plugin and client.exists(previous_plugin): move(previous_plugin,live_plugin)
        if switched_site: move(live_site,staging+'/failed-mit-site')
        if had_site and client.exists(previous_site): move(previous_site,live_site)
        raise
    report={'domain':DOMAIN,'release':release,'version':manifest['version'],'pages':len(manifest['routes']),'original_wordpress_preserved':True,'retained_previous_release':staging if had_site or had_plugin else None,'published_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'public_homepage':True,'visa_finder_page':True,'secure_form_bootstrap':True}
    (ROOT/'.cache'/'mit-deploy-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--build',type=Path,default=ROOT/'.cache'/'mit-build');parser.add_argument('--release',required=True);args=parser.parse_args();deploy(args.build.resolve(),args.release)
