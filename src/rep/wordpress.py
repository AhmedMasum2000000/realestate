"""WordPress installation and configuration, driven through WP-CLI over SSH.

Every method is idempotent: running provision twice must not create a second
admin user, re-download core over a live site, or duplicate listings.
"""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ssh import Result, SshRunner

WP_CLI_URL = "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar"


class WordPressError(Exception):
    """A WP-CLI step failed in a way the operator needs to see."""


@dataclass
class WpSite:
    """WP-CLI bound to one document root on the server."""

    runner: SshRunner
    docroot: str
    wp_bin: str = "wp"

    # -- plumbing -----------------------------------------------------------

    def wp(self, *args: str, allow_fail: bool = False) -> Result:
        """Run a wp-cli subcommand in this site's docroot."""
        cmd = " ".join([self.wp_bin, *(shlex.quote(a) for a in args)])
        # cPanel shared hosts frequently run an old default PHP; --skip-plugins
        # is deliberately NOT set here because some steps need plugins loaded.
        result = self.runner.run(cmd, cwd=self.docroot)
        if not allow_fail:
            result.check()
        return result

    def wp_json(self, *args: str) -> Any:
        """Run a wp-cli command expected to emit JSON and parse it."""
        result = self.wp(*args, "--format=json")
        if self.runner.dry_run or not result.stdout.strip():
            return []
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise WordPressError(
                f"expected JSON from `{result.command}` but got: {result.stdout[:300]!r}"
            ) from exc

    # -- bootstrap ----------------------------------------------------------

    def ensure_wp_cli(self, server_home: str) -> str:
        """Make sure a `wp` command exists; return the path to use.

        Managed cPanel hosts usually ship WP-CLI. When they do not, drop the
        phar into ~/bin, which is the one place we can always write.
        """
        if self.runner.dry_run:
            return self.wp_bin

        if self.runner.run("command -v wp").ok:
            return "wp"

        target = f"{server_home.rstrip('/')}/bin/wp"
        if self.runner.exists(target):
            self.wp_bin = target
            return target

        self.runner.run(f"mkdir -p {shlex.quote(server_home.rstrip('/') + '/bin')}").check()
        self.runner.run(
            f"curl -fsSL {shlex.quote(WP_CLI_URL)} -o {shlex.quote(target)} "
            f"&& chmod +x {shlex.quote(target)}"
        ).check()
        self.wp_bin = target
        return target

    def is_installed(self) -> bool:
        """True when WordPress is present AND its database is initialised."""
        if self.runner.dry_run:
            return False
        if not self.runner.exists(f"{self.docroot}/wp-includes/version.php"):
            return False
        return self.wp("core", "is-installed", allow_fail=True).ok

    def has_core_files(self) -> bool:
        if self.runner.dry_run:
            return False
        return self.runner.exists(f"{self.docroot}/wp-includes/version.php")

    # -- install ------------------------------------------------------------

    def download_core(self, locale: str = "en_US") -> None:
        if self.has_core_files():
            return
        self.runner.run(f"mkdir -p {shlex.quote(self.docroot)}").check()
        self.wp("core", "download", f"--locale={locale}")

    def write_config(self, db_name: str, db_user: str, db_password: str) -> None:
        if not self.runner.dry_run and self.runner.exists(f"{self.docroot}/wp-config.php"):
            return
        self.wp(
            "config",
            "create",
            f"--dbname={db_name}",
            f"--dbuser={db_user}",
            f"--dbpass={db_password}",
            "--dbhost=localhost",
            "--skip-check",
        )
        # Sensible hardening for a fresh site.
        self.wp("config", "set", "DISALLOW_FILE_EDIT", "true", "--raw", "--type=constant")
        self.wp("config", "set", "WP_AUTO_UPDATE_CORE", "minor", "--type=constant")

    def install_core(
        self, url: str, title: str, admin_user: str, admin_password: str, admin_email: str
    ) -> None:
        if self.is_installed():
            return
        self.wp(
            "core",
            "install",
            f"--url={url}",
            f"--title={title}",
            f"--admin_user={admin_user}",
            f"--admin_password={admin_password}",
            f"--admin_email={admin_email}",
            "--skip-email",
        )

    # -- configuration ------------------------------------------------------

    def set_options(
        self,
        title: str = "",
        tagline: str = "",
        timezone: str = "",
        public: bool | None = None,
        permalinks: str = "",
    ) -> None:
        """Apply site settings. Every argument is skippable, and an empty or
        None value means "leave this alone".

        That matters on a live site: forcing `public` off would drop it out of
        Google, and rewriting the permalink structure would change the URL of
        every post already published. Neither is something to do by default.
        """
        if title:
            self.wp("option", "update", "blogname", title)
        if tagline:
            self.wp("option", "update", "blogdescription", tagline)
        if timezone:
            self.wp("option", "update", "timezone_string", timezone)
        if public is not None:
            self.wp("option", "update", "blog_public", "1" if public else "0")
        if permalinks:
            self.wp("rewrite", "structure", permalinks, "--hard")
            self.wp("rewrite", "flush", "--hard")

    def installed_plugins(self) -> set[str]:
        if self.runner.dry_run:
            return set()
        data = self.wp_json("plugin", "list", "--field=name")
        return {str(x) for x in data} if isinstance(data, list) else set()

    def ensure_plugins(self, slugs: list[str]) -> list[str]:
        """Install and activate each plugin. Returns the ones newly added."""
        present = self.installed_plugins()
        added: list[str] = []
        for slug in slugs:
            if slug in present:
                self.wp("plugin", "activate", slug, allow_fail=True)
                continue
            res = self.wp("plugin", "install", slug, "--activate", allow_fail=True)
            if res.ok:
                added.append(slug)
        return added

    def ensure_theme(self, slug: str, child: bool = True) -> str:
        """Install the parent theme and, optionally, scaffold+activate a child."""
        self.wp("theme", "install", slug, allow_fail=True)
        if not child:
            self.wp("theme", "activate", slug)
            return slug

        child_slug = f"{slug}-child"
        if self.runner.dry_run or not self.runner.exists(
            f"{self.docroot}/wp-content/themes/{child_slug}"
        ):
            self.wp("scaffold", "child-theme", child_slug, f"--parent_theme={slug}",
                    "--activate", allow_fail=True)
        else:
            self.wp("theme", "activate", child_slug, allow_fail=True)
        return child_slug

    def active_theme(self) -> str:
        """The stylesheet slug currently active, or "" when unknown."""
        if self.runner.dry_run:
            return ""
        res = self.wp("theme", "list", "--status=active", "--field=name", allow_fail=True)
        return res.stdout.strip().splitlines()[-1].strip() if res.stdout.strip() else ""

    def post_type_exists(self, name: str) -> bool:
        """Whether some plugin or theme already registers this post type."""
        if self.runner.dry_run:
            return False
        res = self.wp("post-type", "list", "--field=name", allow_fail=True)
        return name in {line.strip() for line in res.stdout.splitlines()}

    # -- content scaffolding -------------------------------------------------

    def existing_page_slugs(self) -> set[str]:
        if self.runner.dry_run:
            return set()
        res = self.wp(
            "post", "list", "--post_type=page", "--post_status=any",
            "--field=post_name", allow_fail=True,
        )
        return {line.strip() for line in res.stdout.splitlines() if line.strip()}

    def create_page(self, title: str, slug: str, content: str = "") -> str:
        """Create a published page and return its ID, or "" in a dry run."""
        args = [
            "post", "create",
            "--post_type=page",
            f"--post_title={title}",
            f"--post_name={slug}",
            "--post_status=publish",
            "--porcelain",
        ]
        if content:
            args.append(f"--post_content={content}")
        res = self.wp(*args, allow_fail=True)
        out = res.stdout.strip().splitlines()
        return out[-1].strip() if out and out[-1].strip().isdigit() else ""

    def page_id(self, slug: str) -> str:
        if self.runner.dry_run:
            return ""
        res = self.wp(
            "post", "list", "--post_type=page", "--post_status=any",
            f"--name={slug}", "--field=ID", allow_fail=True,
        )
        out = res.stdout.strip().splitlines()
        return out[-1].strip() if out and out[-1].strip().isdigit() else ""

    def set_front_page(self, front_id: str, blog_id: str = "") -> None:
        """Point the site at a real homepage instead of the post feed."""
        if not front_id:
            return
        self.wp("option", "update", "show_on_front", "page")
        self.wp("option", "update", "page_on_front", front_id)
        if blog_id:
            self.wp("option", "update", "page_for_posts", blog_id)

    def menu_exists(self, name: str) -> bool:
        if self.runner.dry_run:
            return False
        res = self.wp("menu", "list", "--field=name", allow_fail=True)
        return name in {line.strip() for line in res.stdout.splitlines()}

    def build_menu(self, name: str, page_ids: list[str]) -> None:
        """Create a navigation menu, fill it, and assign it to the theme.

        Themes name their locations differently (`primary`, `menu-1`, ...), so
        the location is read from the theme rather than assumed.
        """
        if not self.menu_exists(name):
            self.wp("menu", "create", name, allow_fail=True)
        for pid in page_ids:
            if pid:
                self.wp("menu", "item", "add-post", name, pid, allow_fail=True)

        res = self.wp("menu", "location", "list", "--field=location", allow_fail=True)
        locations = [l.strip() for l in res.stdout.splitlines() if l.strip()]
        for location in locations[:1] or (["primary"] if self.runner.dry_run else []):
            self.wp("menu", "location", "assign", name, location, allow_fail=True)

    def set_logo(self, local_logo: Path) -> None:
        """Upload a logo to the media library and set it as the site logo."""
        remote = f"/tmp/{local_logo.name}"
        self.runner.upload(local_logo, remote)
        res = self.wp(
            "media", "import", remote, "--porcelain", allow_fail=True
        )
        attachment_id = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
        if attachment_id.isdigit():
            self.wp("theme", "mod", "set", "custom_logo", attachment_id, allow_fail=True)
            self.wp("option", "update", "site_icon", attachment_id, allow_fail=True)
        self.runner.run(f"rm -f {shlex.quote(remote)}", cwd="")

    def install_mu_plugin(self, local_php: Path) -> None:
        """Drop a must-use plugin in place (cannot be deactivated by accident)."""
        mu_dir = f"{self.docroot}/wp-content/mu-plugins"
        self.runner.run(f"mkdir -p {shlex.quote(mu_dir)}").check()
        self.runner.upload(local_php, f"{mu_dir}/{local_php.name}")

    def admin_url(self, domain: str) -> str:
        return f"https://{domain}/wp-admin/"
