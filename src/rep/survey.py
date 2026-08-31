"""Fingerprint what is actually served at a domain, from the public site alone.

No credentials, no SSH -- just an HTTP GET. The point is to catch a `state:`
in sites.yml that no longer matches reality *before* a run acts on it, because
treating a live site as empty is how a working site gets overwritten.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import requests

# Asset paths leak the theme and plugin slugs on almost every WordPress site.
THEME_RE = re.compile(r"/wp-content/themes/([A-Za-z0-9_-]+)/")
PLUGIN_RE = re.compile(r"/wp-content/plugins/([A-Za-z0-9_-]+)/")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
GENERATOR_RE = re.compile(
    r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', re.IGNORECASE
)

# Phrases that mean "an unfinished installer is exposed to the public". An
# installer reachable by anyone is a takeover waiting to happen: whoever
# completes it chooses the admin password and the database it points at.
INSTALLER_MARKERS = (
    "system configuration",
    "installation wizard",
    "setup wizard",
    "database configuration",
    "purchase code",
    "envato purchase",
    "wp-admin/setup-config.php",
    "let&#8217;s get started",
)

WP_MARKERS = ("/wp-content/", "/wp-includes/", "wp-json")


@dataclass
class SiteFacts:
    domain: str
    reachable: bool = False
    status: int = 0
    error: str = ""
    title: str = ""
    generator: str = ""
    is_wordpress: bool = False
    theme: str = ""
    plugins: list[str] = field(default_factory=list)
    installer_exposed: bool = False
    final_url: str = ""

    @property
    def verdict(self) -> str:
        if not self.reachable:
            return "unreachable"
        if self.installer_exposed:
            return "INSTALLER EXPOSED"
        if self.is_wordpress:
            return "wordpress"
        if self.status >= 400:
            return f"http {self.status}"
        return "something else"

    @property
    def expected_state(self) -> str:
        """The `state:` sites.yml should carry for this domain."""
        if self.is_wordpress:
            return "live"
        return "new"


def survey(domain: str, timeout: int = 20) -> SiteFacts:
    facts = SiteFacts(domain=domain)
    try:
        resp = requests.get(
            f"https://{domain}/",
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "realestate-provisioning-survey/1.0"},
        )
    except requests.RequestException as exc:
        facts.error = str(exc)
        return facts

    facts.reachable = True
    facts.status = resp.status_code
    facts.final_url = resp.url
    body = resp.text or ""
    lowered = body.lower()

    match = TITLE_RE.search(body)
    if match:
        facts.title = re.sub(r"\s+", " ", match.group(1)).strip()[:160]

    match = GENERATOR_RE.search(body)
    if match:
        facts.generator = match.group(1).strip()[:80]

    facts.is_wordpress = any(m in lowered for m in WP_MARKERS)

    themes = THEME_RE.findall(body)
    facts.theme = themes[0] if themes else ""
    facts.plugins = sorted(set(PLUGIN_RE.findall(body)))

    facts.installer_exposed = any(m in lowered for m in INSTALLER_MARKERS)

    return facts
