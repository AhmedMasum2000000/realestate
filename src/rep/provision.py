"""Per-site provisioning: domain, database, WordPress, branding, listings.

Ordering matters and is deliberate:

  1. domain + database first  -- WordPress cannot install without them
  2. core install             -- everything after this needs a booted WP
  3. content type (mu-plugin) -- must exist before listings are imported
  4. listings                 -- last, and the only slow step

Every step is idempotent, so a run that dies halfway can simply be re-run.
"""

from __future__ import annotations

import json
import shlex
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .config import ROOT, Site
from .cpanel import CpanelClient, db_names, generate_password
from .listings import apply_filter, load_csv
from .ssh import SshRunner
from .wordpress import WpSite

MU_PLUGIN = ROOT / "wp" / "mu-plugin" / "casa-listings.php"
IMPORT_SCRIPT = ROOT / "wp" / "import-listings.php"
SECRETS_DIR = ROOT / "secrets"


@dataclass
class StepResult:
    name: str
    status: str          # "done" | "skipped" | "failed" | "planned"
    detail: str = ""

    SYMBOLS = {"done": "+", "skipped": ".", "failed": "!", "planned": ">"}

    def line(self) -> str:
        return f"  [{self.SYMBOLS.get(self.status, '?')}] {self.name}" + (
            f" -- {self.detail}" if self.detail else ""
        )


@dataclass
class SiteReport:
    domain: str
    steps: list[StepResult] = field(default_factory=list)
    admin_password: str = ""
    db_password: str = ""

    def add(self, name: str, status: str, detail: str = "") -> StepResult:
        step = StepResult(name, status, detail)
        self.steps.append(step)
        return step

    @property
    def failed(self) -> bool:
        return any(s.status == "failed" for s in self.steps)


def resolve_docroot(site: Site, server_home: str, existing_domains: set[str],
                    main_domain: str | None) -> str:
    """Where this site's files live.

    The account's main domain sits in public_html; everything else gets its own
    directory. Getting this wrong would install WordPress over another site, so
    we key off what cPanel reports rather than guessing from sites.yml.
    """
    if main_domain and site.domain == main_domain.lower():
        return f"{server_home.rstrip('/')}/public_html"
    return site.docroot(server_home)


def write_secret(filename: str, lines: list[str]) -> Path:
    """Append generated credentials to a gitignored file, 0600."""
    SECRETS_DIR.mkdir(mode=0o700, exist_ok=True)
    path = SECRETS_DIR / filename
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    path.chmod(0o600)
    return path


def provision_site(
    site: Site,
    cp: CpanelClient,
    runner: SshRunner,
    server_home: str,
    existing_domains: set[str],
    main_domain: str | None,
    *,
    domains_known: bool = True,
    do_listings: bool = True,
    sideload_images: bool = False,
) -> SiteReport:
    report = SiteReport(domain=site.domain)
    dry = cp.dry_run
    docroot = resolve_docroot(site, server_home, existing_domains, main_domain)

    # -- 1. domain ----------------------------------------------------------
    if site.domain in existing_domains:
        report.add("domain", "skipped", f"already on the account -> {docroot}")
    elif not domains_known:
        # We could not ask cPanel what it serves, so we cannot contradict
        # sites.yml. Report what we would do and move on.
        report.add(
            "domain",
            "skipped" if site.state == "live" else "planned",
            f"cPanel not queried; trusting `state: {site.state}` -> {docroot}",
        )
    elif site.state == "live":
        report.add(
            "domain",
            "failed",
            "marked `state: live` in sites.yml but cPanel does not serve it. "
            "Either it is on a different cPanel account, or the state is wrong.",
        )
        return report
    else:
        subdomain = site.domain.split(".")[0]
        cp.add_addon_domain(site.domain, docroot, subdomain)
        report.add("domain", "planned" if dry else "done", f"addon domain -> {docroot}")

    # -- 2. database --------------------------------------------------------
    db_name, db_user = db_names(cp.user, site.slug)
    wp = WpSite(runner=runner, docroot=docroot)
    # WP-CLI has to exist before is_installed() can mean anything: a missing
    # `wp` binary would look identical to a missing WordPress, and we would
    # then try to install over a live site.
    wp.ensure_wp_cli(server_home)
    already_installed = wp.is_installed()

    if already_installed:
        report.add("database", "skipped", "WordPress already connected to its DB")
        db_password = ""
    else:
        existing_dbs = set() if dry else set(cp.list_databases())
        existing_users = set() if dry else set(cp.list_database_users())
        db_password = generate_password()

        if db_name in existing_dbs:
            report.add("database", "skipped", f"{db_name} exists")
        else:
            cp.create_database(db_name)
            report.add("database", "planned" if dry else "done", db_name)

        if db_user in existing_users:
            report.add("db user", "skipped", f"{db_user} exists")
            # We cannot read an existing password back, so a fresh install
            # against a pre-existing user needs a reset to a known value.
            cp.create_database_user(db_user, db_password)
        else:
            cp.create_database_user(db_user, db_password)
            report.add("db user", "planned" if dry else "done", db_user)

        cp.grant_all(db_user, db_name)
        report.add("db grant", "planned" if dry else "done", f"{db_user} -> {db_name}")
        report.db_password = db_password

    # -- 3. WordPress core --------------------------------------------------
    if already_installed:
        report.add("wordpress", "skipped", "already installed")
    else:
        wp.download_core(locale=site.wp.get("locale", "en_US"))
        wp.write_config(db_name, db_user, db_password)

        admin_password = generate_password()
        wp.install_core(
            url=f"https://{site.domain}",
            title=site.title,
            admin_user=site.wp.get("admin_user", "casaadmin"),
            admin_password=admin_password,
            admin_email=site.wp.get("admin_email", ""),
        )
        report.admin_password = admin_password
        report.add("wordpress", "planned" if dry else "done", "core installed")

    # -- 4. settings, theme, plugins ----------------------------------------
    public = site.wp.get("public")
    wp.set_options(
        title=site.title,
        tagline=site.tagline,
        timezone=site.wp.get("timezone", "Asia/Bangkok"),
        public=public,
    )
    report.add(
        "settings",
        "planned" if dry else "done",
        "indexing left as-is" if public is None
        else ("indexing ON" if public else "indexing OFF"),
    )

    theme_slug = site.theme.get("slug", "astra")
    active = wp.ensure_theme(theme_slug, child=bool(site.theme.get("child", True)))
    report.add("theme", "planned" if dry else "done", active)

    added = wp.ensure_plugins(site.plugins)
    report.add(
        "plugins",
        "planned" if dry else "done",
        f"{len(site.plugins)} requested"
        + (f", {len(added)} newly installed" if added else ""),
    )

    # -- 5. branding --------------------------------------------------------
    logo = site.brand.logo_path()
    if logo and logo.exists():
        wp.set_logo(logo)
        report.add("logo", "planned" if dry else "done", logo.name)
    elif logo:
        report.add("logo", "failed", f"{logo} not found -- drop the file in assets/logos/")
    else:
        report.add("logo", "skipped", "no logo set in sites.yml")

    # -- 6. listing content type -------------------------------------------
    wp.install_mu_plugin(MU_PLUGIN)
    report.add("listing type", "planned" if dry else "done", "casa-listings.php")

    # -- 7. listings --------------------------------------------------------
    csv_path = site.listings.csv_path()
    if not do_listings:
        report.add("listings", "skipped", "--no-listings")
    elif not csv_path:
        report.add("listings", "skipped", "no CSV set in sites.yml")
    elif not csv_path.exists():
        report.add("listings", "failed", f"{csv_path} not found -- drop the file in data/")
    else:
        try:
            rows, mapping = load_csv(csv_path, overrides=site.listings.columns)
            rows = apply_filter(rows, site.listings.filter)
        except (ValueError, OSError) as exc:
            report.add("listings", "failed", str(exc))
            return report

        if not mapping.looks_like_listings:
            report.add(
                "listings",
                "failed",
                f"{csv_path.name} does not look like a listings export "
                f"(matched only: {sorted(mapping.mapped)}). Run bin/inspect-csv on it.",
            )
        elif not rows:
            report.add("listings", "skipped", "filter matched 0 rows")
        else:
            _push_listings(wp, runner, rows, sideload_images=sideload_images)
            detail = f"{len(rows)} listings from {csv_path.name}"
            if mapping.unmapped:
                detail += f" ({len(mapping.unmapped)} extra columns kept as metadata)"
            report.add("listings", "planned" if dry else "done", detail)

    return report


def _push_listings(
    wp: WpSite, runner: SshRunner, rows: list, *, sideload_images: bool
) -> None:
    """Ship the listings as one JSON payload and import them in a single pass.

    One `wp eval-file` beats N `wp post create` calls: WordPress boots once
    instead of once per row, which is the difference between seconds and tens
    of minutes on shared hosting.
    """
    payload = {"listings": [r.to_dict() for r in rows]}

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False)
        local_json = Path(handle.name)

    remote_json = f"/tmp/casa-listings-{local_json.stem}.json"
    remote_php = "/tmp/casa-import-listings.php"

    try:
        runner.upload(local_json, remote_json)
        runner.upload(IMPORT_SCRIPT, remote_php)

        args = ["eval-file", remote_php, remote_json]
        if sideload_images:
            args.append("--sideload-images")
        wp.wp(*args)
    finally:
        local_json.unlink(missing_ok=True)
        runner.run(f"rm -f {shlex.quote(remote_json)} {shlex.quote(remote_php)}")
