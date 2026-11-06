"""Listing enrichment from the source site.

Roughly 40% of the export's `source_url` values still resolve; the rest
301-redirect to the index because the listing was sold or withdrawn. That is
treated as a normal outcome, not an error — the build degrades to a placeholder
and the listing simply stays un-indexed.

Only photographs are taken. The page's own marketing text is deliberately not
republished: copying another site's descriptions verbatim is duplicate content
under Google's spam policy, and our generated copy is differentiated anyway.
"""

from __future__ import annotations

import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request

PROVIDER = "casa"

USER_AGENT = "PattayaHomeProBot/1.0 (+https://pattayahomepro.com/bot)"
# Requests are serial and each round trip already takes several seconds, so the
# effective rate sits near one request every five seconds without this. The
# delay is the floor, not the actual pace.
DELAY = 0.75
JITTER = 0.4
RETRIES = 3
TIMEOUT = 30

CDN = re.compile(
    r"https://assets\.casapattaya\.com/file/casa-pattaya/[^\s\"'\\<>]+?"
    r"\.(?:jpg|jpeg|png|webp)",
    re.IGNORECASE,
)

# The main gallery sits between these two markers; everything after the second
# belongs to the "recommended" carousel, i.e. other people's listings.
GALLERY_START = "swiper-large"
GALLERY_END = "recommended-slider"

PHOTO_EXT = (".jpg", ".jpeg", ".webp")


def encode(url: str) -> str:
    """Percent-encode the path. Some filenames are Thai, which is legal on the
    CDN but not valid inside an HTML attribute unescaped."""
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((
        parts.scheme,
        parts.netloc,
        urllib.parse.quote(parts.path, safe="/-_.~"),
        parts.query,
        parts.fragment,
    ))


def fetch(url: str) -> dict:
    """Return {ok, status, final_url, html}. Never raises for network trouble —
    a failure here must not abort a thousand-URL run."""
    last = ""
    for attempt in range(RETRIES):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                body = response.read().decode("utf-8", errors="replace")
                return {
                    "ok": True,
                    "status": response.status,
                    "final_url": response.geturl(),
                    "html": body,
                }
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 410):
                return {"ok": False, "status": exc.code, "final_url": url, "html": ""}
            last = f"http {exc.code}"
        except Exception as exc:  # timeouts, DNS, reset connections
            last = type(exc).__name__
        time.sleep(2 ** attempt)
    return {"ok": False, "status": 0, "final_url": url, "html": "", "error": last}


def gallery(html: str) -> list[str]:
    start = html.find(GALLERY_START)
    stop = html.find(GALLERY_END)
    region = html[start:stop] if 0 <= start < stop else html

    seen: list[str] = []
    for match in CDN.finditer(region):
        url = encode(match.group(0))
        if url not in seen:
            seen.append(url)
    return seen


def pick_hero(images: list[str]) -> str:
    """Prefer an actual photograph. The og:image is often a PNG screenshot of
    a floor plan or price list, which makes a poor card image."""
    for url in images:
        if url.lower().endswith(PHOTO_EXT):
            return url
    return images[0] if images else ""


def scrape(url: str) -> dict:
    """One listing. `delisted` means the source redirected us to its index."""
    result = fetch(url)
    final = result.get("final_url", "")
    delisted = final.rstrip("/").endswith("/properties")

    if not result["ok"] or delisted or not result["html"]:
        return {
            "ok": False,
            "status": result.get("status", 0),
            "final_url": final,
            "delisted": delisted,
            "images": [],
        }

    images = gallery(result["html"])
    return {
        "ok": bool(images),
        "status": result["status"],
        "final_url": final,
        "delisted": False,
        "images": images,
        "hero": pick_hero(images),
    }


def pause() -> None:
    time.sleep(DELAY + random.uniform(0, JITTER))
