"""Read Move In Thailand's existing public brand assets, confirmed through cPanel.

Never reads credentials or database contents. Only public images, styles and
page HTML are included in the download artifact.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rep.cpanel import CpanelClient

DOMAIN = "moveinthailand.com"
OUT = ROOT / ".cache" / "mit-source"
OUT.mkdir(parents=True, exist_ok=True)


class PublicPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            self.assets.append((a.get("src") or a.get("data-src") or "", a.get("alt", ""), "image"))
        elif tag == "link" and "stylesheet" in a.get("rel", ""):
            self.assets.append((a.get("href", ""), "stylesheet", "style"))
        elif tag == "a":
            self.links.append(a.get("href", ""))


def collect():
    session = requests.Session()
    session.headers["User-Agent"] = "MoveInThailand-BrandAudit/1.0"
    page = session.get(f"https://{DOMAIN}/", timeout=45)
    page.raise_for_status()
    page.encoding = "utf-8"
    (OUT / "homepage.html").write_text(page.text, encoding="utf-8")
    parsed = PublicPage()
    parsed.feed(page.text)
    candidates = list(parsed.assets)
    candidates += [(url, "background", "image") for url in re.findall(r'url\([\'\"]?([^\)\'\"]+)', page.text)]
    manifest = {"domain": DOMAIN, "source": "public files confirmed in cPanel", "assets": [], "links": parsed.links}
    cp = None
    root = ""
    if all(os.environ.get(k) for k in ("CPANEL_HOST", "CPANEL_USER", "CPANEL_API_TOKEN")):
        cp = CpanelClient(os.environ["CPANEL_HOST"], os.environ["CPANEL_USER"], os.environ["CPANEL_API_TOKEN"], dry_run=True)
        root = cp.docroot(DOMAIN)
        manifest["cpanel_document_root"] = root
        # Inspect the original media library before choosing any photographs.
        uploads = f"{root}/wp-content/uploads"
        dates = cp.list_dir(uploads)
        manifest["media_folders"] = sorted(dates)
        for year in sorted((v for v in dates if re.fullmatch(r"20\d\d", v)), reverse=True)[:2]:
            year_dir = f"{uploads}/{year}"
            for month in sorted((v for v in cp.list_dir(year_dir) if re.fullmatch(r"\d\d", v)), reverse=True)[:4]:
                folder = f"{year_dir}/{month}"
                files = cp.list_dir(folder)
                originals = [n for n in files if re.search(r"\.(jpg|jpeg|png|webp)$", n, re.I) and not re.search(r"-\d+x\d+\.", n)]
                manifest.setdefault("media_inventory", []).extend([f"wp-content/uploads/{year}/{month}/{n}" for n in originals])
                for name in originals[:18]:
                    candidates.append((f"https://{DOMAIN}/wp-content/uploads/{year}/{month}/{name}", name, "image"))
    else:
        manifest["source"] = "public homepage only - cPanel confirmation pending"

    seen = set()
    for value, alt, kind in candidates:
        url = urljoin(f"https://{DOMAIN}/", value)
        info = urlparse(url)
        if info.hostname not in (DOMAIN, f"www.{DOMAIN}") or info.path in seen or not value:
            continue
        seen.add(info.path)
        relative = unquote(info.path.lstrip("/"))
        if ".." in Path(relative).parts or not re.search(r"\.(css|png|jpg|jpeg|webp|svg)$", relative, re.I):
            continue
        if cp and not cp.exists(f"{root}/{relative}"):
            continue
        try:
            response = session.get(url, timeout=25)
            response.raise_for_status()
            if len(response.content) > 8_000_000:
                continue
        except requests.RequestException:
            continue
        destination = OUT / "files" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)
        manifest["assets"].append({"file": relative, "url": url, "alt": alt, "kind": kind, "bytes": len(response.content), "cpanel_confirmed": bool(cp)})
        if len(manifest["assets"]) >= 65:
            break
    if cp:
        partner_root = cp.docroot("pattayahomepro.com")
        for reference in ("CP1790", "CP1799", "CP1849", "CP1860"):
            relative = f"assets/properties/{reference}/hero.webp"
            if not cp.exists(f"{partner_root}/{relative}"):
                continue
            response = session.get(f"https://pattayahomepro.com/{relative}", timeout=25)
            response.raise_for_status()
            destination = OUT / "partner" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(response.content)
            manifest["assets"].append({"file": f"partner/{relative}", "url": f"https://pattayahomepro.com/{relative}", "alt": f"Partner property photograph {reference}", "kind": "image", "bytes": len(response.content), "cpanel_confirmed": True})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"document_root": root, "files": len(manifest["assets"]), "assets": manifest["assets"]}, indent=2))


if __name__ == "__main__":
    collect()
