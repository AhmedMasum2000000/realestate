"""Shared plumbing for the bin/ scripts: env loading, client construction, output."""

from __future__ import annotations

import sys
from typing import NoReturn

from .config import (
    REQUIRED_FOR_CPANEL,
    REQUIRED_FOR_SSH,
    ConfigError,
    Site,
    load_env,
    load_sites,
    missing_keys,
)
from .cpanel import CpanelClient
from .ssh import SshRunner


def die(message: str, code: int = 1) -> NoReturn:
    print(f"\nERROR: {message}\n", file=sys.stderr)
    raise SystemExit(code)


def banner(text: str) -> None:
    print(f"\n{text}\n{'=' * len(text)}")


def load_or_die() -> tuple[list[Site], dict[str, str]]:
    try:
        return load_sites(), load_env()
    except ConfigError as exc:
        die(str(exc))


def require_env(env: dict[str, str], keys: tuple[str, ...], purpose: str) -> None:
    missing = missing_keys(env, keys)
    if missing:
        die(
            f"config/.env is missing {', '.join(missing)} -- needed to {purpose}.\n"
            f"       Copy config/.env.example to config/.env and fill it in."
        )


# Stand-ins used only when previewing a plan with no credentials on disk.
# They never reach the network: every mutating call is short-circuited by
# dry_run, and the one read (list_domains) is allowed to fail.
_PLACEHOLDER = "(not-set)"


def make_cpanel(env: dict[str, str], dry_run: bool) -> CpanelClient:
    if not dry_run:
        require_env(env, REQUIRED_FOR_CPANEL, "talk to cPanel")
    return CpanelClient(
        host=env.get("CPANEL_HOST") or _PLACEHOLDER,
        user=env.get("CPANEL_USER") or _PLACEHOLDER,
        token=env.get("CPANEL_API_TOKEN") or _PLACEHOLDER,
        port=int(env.get("CPANEL_PORT") or 2083),
        dry_run=dry_run,
    )


def make_ssh(env: dict[str, str], dry_run: bool) -> SshRunner:
    if not dry_run:
        require_env(env, REQUIRED_FOR_SSH, "install WordPress over SSH")
    return SshRunner(
        host=env.get("SSH_HOST") or _PLACEHOLDER,
        user=env.get("SSH_USER") or _PLACEHOLDER,
        port=int(env.get("SSH_PORT") or 22),
        key_path=env.get("SSH_KEY_PATH", ""),
        password=env.get("SSH_PASSWORD", ""),
        dry_run=dry_run,
    )


def server_home(env: dict[str, str], dry_run: bool = False) -> str:
    home = env.get("SERVER_HOME") or f"/home/{env.get('CPANEL_USER', '')}"
    if not home.strip("/"):
        if dry_run:
            return "/home/(your-cpanel-user)"
        die("SERVER_HOME is empty and CPANEL_USER is unset; cannot guess the home directory")
    return home


def pick_site(sites: list[Site], domain: str) -> Site:
    """Find one site by domain, tolerating a pasted URL or wp-admin path."""
    needle = (
        domain.strip()
        .lower()
        .replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .split("/")[0]
    )
    for site in sites:
        if site.domain == needle:
            return site
    known = "\n         ".join(s.domain for s in sites)
    die(f"{domain!r} is not in config/sites.yml. Known sites:\n         {known}")


def add_common_args(parser) -> None:
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually make changes. Without this, nothing is written anywhere.",
    )
