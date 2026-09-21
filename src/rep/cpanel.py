"""Thin cPanel UAPI client, plus the handful of calls provisioning needs.

Auth is an API token (cPanel -> Security -> Manage API Tokens), never a
password. Every mutating call routes through `_call` so dry-run is honoured in
exactly one place.
"""

from __future__ import annotations

import json
import secrets
import string
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import requests


class CpanelError(Exception):
    """A cPanel API call failed, with cPanel's own reason attached."""


@dataclass
class CpanelClient:
    host: str
    user: str
    token: str
    port: int = 2083
    dry_run: bool = True
    timeout: int = 45
    verify_tls: bool = True

    @property
    def base(self) -> str:
        return f"https://{self.host}:{self.port}"

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"cpanel {self.user}:{self.token}"}

    # -- transport ----------------------------------------------------------

    def _call(
        self,
        module: str,
        function: str,
        params: dict[str, Any] | None = None,
        *,
        mutating: bool,
    ) -> dict[str, Any]:
        params = params or {}
        label = f"UAPI {module}::{function}({_brief(params)})"

        if mutating and self.dry_run:
            return {"_dry_run": True, "_label": label, "data": None}

        url = f"{self.base}/execute/{quote(module)}/{quote(function)}"
        try:
            resp = requests.get(
                url,
                headers=self._headers,
                params=params,
                timeout=self.timeout,
                verify=self.verify_tls,
            )
        except requests.RequestException as exc:
            raise CpanelError(f"{label}: could not reach {self.host} -- {exc}") from exc

        if resp.status_code == 401:
            raise CpanelError(
                f"{label}: cPanel rejected the credentials (401). "
                "Check CPANEL_USER and that the API token is still valid."
            )
        if resp.status_code >= 400:
            raise CpanelError(f"{label}: HTTP {resp.status_code} -- {resp.text[:400]}")

        try:
            body = resp.json()
        except json.JSONDecodeError as exc:
            raise CpanelError(
                f"{label}: cPanel returned non-JSON. This usually means the host "
                f"or port is wrong. First bytes: {resp.text[:200]!r}"
            ) from exc

        if not body.get("status"):
            errors = body.get("errors") or ["unknown error"]
            raise CpanelError(f"{label}: {'; '.join(str(e) for e in errors)}")

        return body

    # -- reads --------------------------------------------------------------

    def list_domains(self) -> dict[str, Any]:
        body = self._call("DomainInfo", "list_domains", mutating=False)
        return body.get("data") or {}

    def all_domains(self) -> set[str]:
        """Every domain this account serves, main + addon + parked + sub."""
        data = self.list_domains()
        found: set[str] = set()
        main = data.get("main_domain")
        if main:
            found.add(str(main).lower())
        for key in ("addon_domains", "parked_domains", "sub_domains"):
            for d in data.get(key) or []:
                found.add(str(d).lower())
        return found

    def list_databases(self) -> list[str]:
        body = self._call("Mysql", "list_databases", mutating=False)
        return [str(d.get("database")) for d in (body.get("data") or [])]

    def list_database_users(self) -> list[str]:
        body = self._call("Mysql", "list_users", mutating=False)
        return [str(u.get("user")) for u in (body.get("data") or [])]

    def whoami(self) -> dict[str, Any]:
        """Cheap authenticated read used by the preflight check."""
        return self.list_domains()

    # -- writes -------------------------------------------------------------

    def add_addon_domain(self, domain: str, docroot: str, subdomain: str) -> dict[str, Any]:
        return self._call(
            "AddonDomain",
            "addaddondomain",
            {"dir": docroot, "newdomain": domain, "subdomain": subdomain},
            mutating=True,
        )

    def create_database(self, name: str) -> dict[str, Any]:
        return self._call("Mysql", "create_database", {"name": name}, mutating=True)

    def create_database_user(self, name: str, password: str) -> dict[str, Any]:
        return self._call(
            "Mysql", "create_user", {"name": name, "password": password}, mutating=True
        )

    def grant_all(self, db_user: str, db_name: str) -> dict[str, Any]:
        return self._call(
            "Mysql",
            "set_privileges_on_database",
            {"user": db_user, "database": db_name, "privileges": "ALL PRIVILEGES"},
            mutating=True,
        )

    def request_autossl(self) -> dict[str, Any]:
        """Ask AutoSSL to sweep the account. Certificates land minutes later."""
        return self._call("SSL", "start_autossl_check", mutating=True)


# -- naming -----------------------------------------------------------------

# cPanel prefixes DB names/users with "<cpuser>_" and caps the whole thing at
# 64 chars. Keep our part short so long domains cannot overflow it.
_DB_SUFFIX_MAX = 16


def db_names(prefix_user: str, site_slug: str) -> tuple[str, str]:
    """Return (database, db_user) as cPanel will actually store them.

    The TLD is dropped -- it carries no information here and only eats into the
    64-char budget, which cPanel enforces after prefixing "<cpuser>_".
    """
    cpanel_user = prefix_user
    parts = [p for p in site_slug.split("_") if p]
    if len(parts) > 1:
        parts = parts[:-1]  # drop the TLD component
    stem = "".join(parts)[:_DB_SUFFIX_MAX]
    prefix = f"{cpanel_user}_"
    return f"{prefix}{stem}wp", f"{prefix}{stem}u"


def generate_password(length: int = 28) -> str:
    """A password cPanel and MySQL both accept, with no shell-hostile chars."""
    alphabet = string.ascii_letters + string.digits + "!@#%^*_-+="
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in pw)
            and any(c.isupper() for c in pw)
            and any(c.isdigit() for c in pw)
            and any(c in "!@#%^*_-+=" for c in pw)
        ):
            return pw


def _brief(params: dict[str, Any]) -> str:
    """Render params for logs with secrets masked."""
    parts = []
    for k, v in params.items():
        if "pass" in k.lower() or "token" in k.lower():
            v = "***"
        parts.append(f"{k}={v}")
    return ", ".join(parts)
