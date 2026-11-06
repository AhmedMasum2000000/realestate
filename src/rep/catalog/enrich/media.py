"""Hero image download.

Card images are downloaded and served from our own origin. Hotlinking them
would leave every listing card dependent on a third party's URL structure and
hotlink policy — one change there and the catalogue goes blank all at once.

Gallery images stay hotlinked: twelve per listing across 424 listings is
thousands of files, which does not belong in a repository. A gallery image that
stops resolving costs one thumbnail; a hero that stops resolving costs the card.
"""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .casa import TIMEOUT, USER_AGENT

ASSET_ROOT = Path("assets/properties")
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 3_000_000


def extension(url: str) -> str:
    suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
    return suffix if suffix in ALLOWED_EXT else ".jpg"


def local_path(root: Path, reference: str, url: str) -> Path:
    return root / ASSET_ROOT / reference / f"hero{extension(url)}"


def public_path(reference: str, url: str) -> str:
    return f"/{ASSET_ROOT}/{reference}/hero{extension(url)}"


def download(root: Path, reference: str, url: str) -> str:
    """Return the public path, or "" on failure.

    Existing files are left alone, which makes the whole pass resumable and
    keeps repeat runs free.
    """
    target = local_path(root, reference, url)
    if target.exists() and target.stat().st_size > 0:
        return public_path(reference, url)

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            if response.status != 200:
                return ""
            body = response.read(MAX_BYTES + 1)
    except (urllib.error.URLError, OSError, ValueError):
        return ""

    if not body or len(body) > MAX_BYTES:
        return ""

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    return public_path(reference, url)
