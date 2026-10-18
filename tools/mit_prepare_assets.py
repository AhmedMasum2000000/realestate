"""Optimise the confirmed cPanel media without changing the logo artwork."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]

def prepare(source):
    manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    confirmed={item['file']:item for item in manifest['assets'] if item.get('cpanel_confirmed')}
    mapping={
        'logo.png':('wp-content/uploads/2026/03/Logo-Move-In-Thailand-scaled.png',640),
        'coast.webp':('wp-content/uploads/2026/03/wallpaperflare.com_wallpaper.jpg',1600),
        'home.webp':('partner/assets/properties/CP1790/hero.webp',1200),
        'home-2.webp':('partner/assets/properties/CP1799/hero.webp',1200),
        'home-3.webp':('partner/assets/properties/CP1849/hero.webp',1200),
    }
    dest=ROOT/'mit'/'assets';dest.mkdir(parents=True,exist_ok=True)
    provenance=[]
    for name,(original,size) in mapping.items():
        if original not in confirmed:
            raise SystemExit('Asset was not confirmed in cPanel: '+original)
        path=source/'files'/original
        if not path.exists(): path=source/original
        with Image.open(path) as image:
            image=ImageOps.exif_transpose(image)
            image.thumbnail((size,size),Image.Resampling.LANCZOS)
            if name.endswith('.png'):
                image.convert('RGBA').save(dest/name,optimize=True)
            else:
                image.convert('RGB').save(dest/name,format='WEBP',quality=88,method=6)
        provenance.append({'asset':name,'source_url':confirmed[original]['url'],'cpanel_confirmed':True,'original_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'use':'Original brand artwork' if name=='logo.png' else 'Existing website or partner property photograph; not a client testimonial or current availability claim'})
    fonts=dest/'fonts';fonts.mkdir(exist_ok=True)
    for name in ('rubik-400.woff2','rubik-500.woff2'):
        shutil.copyfile(ROOT/'assets'/'brand'/'fonts'/name,fonts/name)
    (ROOT/'mit'/'asset-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Prepared {len(mapping)} confirmed images and two local fonts.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args();prepare(args.source.resolve())
