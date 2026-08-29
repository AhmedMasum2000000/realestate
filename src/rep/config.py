"""Loading and validating config/sites.yml and config/.env.

Nothing here reaches the network. Import this to find out *what* we intend to
do; the cpanel/wordpress modules do the doing.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
SITES_FILE = CONFIG_DIR / "sites.yml"
ENV_FILE = CONFIG_DIR / ".env"

# A domain we are willing to touch. Deliberately strict: a typo here would
# create a stray addon domain on a live server.
DOMAIN_RE = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))+$")

VALID_STATES = {"live", "new"}


class ConfigError(Exception):
    """Raised when sites.yml or .env is wrong in a way we can explain."""


@dataclass
class Brand:
    primary_color: str = "#1a3a5c"
    accent_color: str = "#c9a227"
    logo: str = ""

    def logo_path(self) -> Path | None:
        if not self.logo:
            return None
        p = Path(self.logo)
        return p if p.is_absolute() else ROOT / p


@dataclass
class ListingSource:
    csv: str = ""
    filter: dict[str, str] = field(default_factory=dict)
    # Manual column mapping for headers the auto-matcher gets wrong:
    #   columns: {price: "Asking Price (THB)"}
    columns: dict[str, str] = field(default_factory=dict)

    def csv_path(self) -> Path | None:
        if not self.csv:
            return None
        p = Path(self.csv)
        return p if p.is_absolute() else ROOT / p


@dataclass
class Site:
    domain: str
    state: str
    title: str
    tagline: str = ""
    brand: Brand = field(default_factory=Brand)
    listings: ListingSource = field(default_factory=ListingSource)
    wp: dict[str, Any] = field(default_factory=dict)
    theme: dict[str, Any] = field(default_factory=dict)
    plugins: list[str] = field(default_factory=list)

    @property
    def is_new(self) -> bool:
        return self.state == "new"

    @property
    def slug(self) -> str:
        """Filesystem-safe name, e.g. pattayahomespro_com."""
        return self.domain.replace(".", "_").replace("-", "_")

    def docroot(self, server_home: str) -> str:
        """Where this site's files live on the server.

        The primary domain sits in public_html; addon domains get their own
        directory beside it. Which one is primary is decided at runtime by
        cpanel.resolve_docroots(), so this is the fallback convention only.
        """
        return f"{server_home.rstrip('/')}/{self.domain}"


def _merge_defaults(defaults: dict[str, Any], raw: dict[str, Any]) -> Site:
    domain = str(raw.get("domain", "")).strip().lower()
    if not domain:
        raise ConfigError("a site entry is missing `domain`")
    if not DOMAIN_RE.match(domain):
        raise ConfigError(
            f"{domain!r} does not look like a bare domain name. "
            "Write it as example.com -- no https://, no trailing slash, no /wp-admin."
        )

    state = str(raw.get("state", "new")).strip().lower()
    if state not in VALID_STATES:
        raise ConfigError(
            f"{domain}: state is {state!r}, expected one of {sorted(VALID_STATES)}"
        )

    title = str(raw.get("title") or "").strip()
    if not title and state == "new":
        raise ConfigError(
            f"{domain}: `title` is required for a new site -- it is the name "
            "WordPress is installed with."
        )
    # On a live site an absent title means "keep the name the site already has",
    # which is safer than overwriting it with a guess.

    brand_defaults = dict(defaults.get("brand") or {})
    brand_raw = dict(raw.get("brand") or {})
    brand_defaults.update({k: v for k, v in brand_raw.items() if v not in (None, "")})
    if raw.get("logo"):
        brand_defaults["logo"] = raw["logo"]
    brand = Brand(
        primary_color=brand_defaults.get("primary_color", "#1a3a5c"),
        accent_color=brand_defaults.get("accent_color", "#c9a227"),
        logo=brand_defaults.get("logo", "") or "",
    )

    listings_raw = dict(raw.get("listings") or {})
    listings = ListingSource(
        csv=str(listings_raw.get("csv") or ""),
        filter=dict(listings_raw.get("filter") or {}),
        columns=dict(listings_raw.get("columns") or {}),
    )

    site_wp = dict(raw.get("wp") or {})
    site_theme = dict(raw.get("theme") or {})
    site_plugins = list(raw.get("plugins") or [])

    wp = dict(defaults.get("wp") or {})
    wp.update(site_wp)
    theme = dict(defaults.get("theme") or {})
    theme.update(site_theme)
    plugins = list(site_plugins or defaults.get("plugins") or [])

    # The defaults block describes how to BUILD a new site. Inheriting it onto
    # a site that is already live would change things nobody asked to change:
    # swap a working theme, activate plugins on production, drop the site out
    # of Google. So on a live site only settings written on that site itself
    # take effect; anything absent is left exactly as it is.
    if state == "live":
        wp = site_wp
        theme = site_theme
        plugins = site_plugins

    return Site(
        domain=domain,
        state=state,
        title=title,
        tagline=str(raw.get("tagline") or ""),
        brand=brand,
        listings=listings,
        wp=wp,
        theme=theme,
        plugins=plugins,
    )


def load_sites(path: Path | None = None) -> list[Site]:
    """Parse sites.yml into Site objects, or raise ConfigError with a fix."""
    path = path or SITES_FILE
    if not path.exists():
        raise ConfigError(f"missing {path}. Copy it from the repo or re-clone.")

    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} is not valid YAML: {exc}") from exc

    defaults = dict(doc.get("defaults") or {})
    raw_sites = doc.get("sites") or []
    if not isinstance(raw_sites, list) or not raw_sites:
        raise ConfigError(f"{path} has no `sites:` list")

    sites = [_merge_defaults(defaults, s) for s in raw_sites]

    seen: set[str] = set()
    for s in sites:
        if s.domain in seen:
            raise ConfigError(f"{s.domain} is listed twice in {path}")
        seen.add(s.domain)

    return sites


def load_env(path: Path | None = None) -> dict[str, str]:
    """Read config/.env into a dict, expanding ${VAR} against earlier keys.

    Real environment variables win, so CI and one-off overrides work without
    editing the file.
    """
    path = path or ENV_FILE
    env: dict[str, str] = {}

    if path.exists():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ConfigError(f"{path}:{lineno}: expected KEY=value, got {line!r}")
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Expand ${OTHER_KEY} against what we've read so far.
            value = re.sub(
                r"\$\{([A-Z0-9_]+)\}",
                lambda m: env.get(m.group(1), os.environ.get(m.group(1), "")),
                value,
            )
            env[key] = value

    for key in list(env) + [
        "CPANEL_HOST", "CPANEL_USER", "CPANEL_API_TOKEN", "CPANEL_PORT",
        "SSH_HOST", "SSH_USER", "SSH_PORT", "SSH_KEY_PATH", "SSH_PASSWORD",
        "SERVER_HOME", "WHM_HOST", "WHM_USER", "WHM_API_TOKEN",
    ]:
        if os.environ.get(key):
            env[key] = os.environ[key]

    return env


REQUIRED_FOR_CPANEL = ("CPANEL_HOST", "CPANEL_USER", "CPANEL_API_TOKEN")
REQUIRED_FOR_SSH = ("SSH_HOST", "SSH_USER")


def missing_keys(env: dict[str, str], keys: tuple[str, ...]) -> list[str]:
    return [k for k in keys if not env.get(k)]
