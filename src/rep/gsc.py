"""Google Search Console, through its official APIs and a service account.

Covers what Search Console exposes programmatically: proving ownership (Site
Verification API), adding the property, submitting sitemaps, search analytics
and URL inspection (Search Console API).

There is no API for "request indexing" on ordinary pages -- Google's Indexing
API is restricted to job postings and livestreams. Sitemap submission is the
supported lever, so that is what deploys trigger.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any
from urllib.parse import quote

SCOPES = [
    "https://www.googleapis.com/auth/siteverification",
    "https://www.googleapis.com/auth/webmasters",
]
VERIFY = "https://www.googleapis.com/siteVerification/v1"
WEBMASTERS = "https://www.googleapis.com/webmasters/v3"
INSPECT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"


class GscError(Exception):
    pass


def domain_property(domain: str) -> str:
    return f"sc-domain:{domain}"


def url_property(domain: str) -> str:
    return f"https://{domain}/"


class SearchConsole:
    def __init__(self, service_account_json: str, session: Any = None):
        info = json.loads(service_account_json)
        self.email = info["client_email"]
        if session is None:
            from google.auth.transport.requests import AuthorizedSession
            from google.oauth2 import service_account

            creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
            session = AuthorizedSession(creds)
        self.http = session

    # -- transport ----------------------------------------------------------

    def _req(self, method: str, url: str, **kw) -> dict:
        resp = self.http.request(method, url, timeout=60, **kw)
        if resp.status_code >= 400:
            try:
                msg = resp.json().get("error", {}).get("message", resp.text)
            except ValueError:
                msg = resp.text
            raise GscError(f"{method} {url.split('?')[0]} -> {resp.status_code}: {str(msg)[:300]}")
        return resp.json() if resp.content else {}

    # -- ownership ----------------------------------------------------------

    def token(self, kind: str, identifier: str, method: str) -> str:
        """kind INET_DOMAIN + DNS_TXT, or SITE + META."""
        body = {"site": {"type": kind, "identifier": identifier}, "verificationMethod": method}
        return self._req("POST", f"{VERIFY}/token", json=body)["token"]

    def verify(self, kind: str, identifier: str, method: str) -> dict:
        body = {"site": {"type": kind, "identifier": identifier}}
        return self._req("POST", f"{VERIFY}/webResource?verificationMethod={method}", json=body)

    def add_owner(self, resource_id: str, email: str) -> list[str]:
        url = f"{VERIFY}/webResource/{quote(resource_id, safe='')}"
        res = self._req("GET", url)
        owners = res.get("owners", [])
        if email.lower() not in (o.lower() for o in owners):
            res["owners"] = owners + [email]
            res = self._req("PUT", url, json=res)
        return res.get("owners", [])

    # -- property + sitemaps ------------------------------------------------

    def add_site(self, site: str) -> None:
        self._req("PUT", f"{WEBMASTERS}/sites/{quote(site, safe='')}")

    def sites(self) -> list[dict]:
        return self._req("GET", f"{WEBMASTERS}/sites").get("siteEntry", [])

    def submit_sitemap(self, site: str, feed: str) -> None:
        self._req("PUT", f"{WEBMASTERS}/sites/{quote(site, safe='')}/sitemaps/{quote(feed, safe='')}")

    def sitemaps(self, site: str) -> list[dict]:
        return self._req("GET", f"{WEBMASTERS}/sites/{quote(site, safe='')}/sitemaps").get("sitemap", [])

    # -- reporting ----------------------------------------------------------

    def analytics(self, site: str, days: int, dimensions: list[str], limit: int = 10) -> list[dict]:
        # Search data lands with a ~2 day delay; ending there avoids a window
        # whose last days always read as zero.
        end = date.today() - timedelta(days=2)
        body = {
            "startDate": (end - timedelta(days=days - 1)).isoformat(),
            "endDate": end.isoformat(),
            "dimensions": dimensions,
            "rowLimit": limit,
        }
        return self._req("POST", f"{WEBMASTERS}/sites/{quote(site, safe='')}/searchAnalytics/query",
                         json=body).get("rows", [])

    def inspect(self, site: str, url: str) -> dict:
        res = self._req("POST", INSPECT, json={"inspectionUrl": url, "siteUrl": site})
        return res.get("inspectionResult", {}).get("indexStatusResult", {})
