"""On-disk fetch cache.

Enrichment runs over ~1,000 URLs against a live third-party site, so it has to
be restartable without refetching what it already has. Every response — including
the misses — is cached, because a listing that has been delisted will keep being
delisted and refetching it is pure waste.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

CACHE_ROOT = Path(".cache/enrich")

# A hit is re-checked monthly; a miss (delisted, 404) far less often, since that
# state rarely reverses.
TTL_HIT = 30 * 86400
TTL_MISS = 90 * 86400


def key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def path_for(root: Path, provider: str, url: str) -> Path:
    digest = key(url)
    # Shard on the first two hex chars: a thousand files in one directory is
    # tolerable, but this stays cheap if the catalog grows.
    return root / provider / digest[:2] / f"{digest}.json"


def load(root: Path, provider: str, url: str) -> dict | None:
    target = path_for(root, provider, url)
    if not target.exists():
        return None
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    age = time.time() - payload.get("fetched_at", 0)
    ttl = TTL_HIT if payload.get("ok") else TTL_MISS
    if age > ttl:
        return None
    return payload


def store(root: Path, provider: str, url: str, payload: dict) -> None:
    target = path_for(root, provider, url)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {**payload, "fetched_at": time.time()}
    target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
