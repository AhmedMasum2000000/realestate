"""Tests for the WP-CLI driver: command construction and the indexing guard."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.ssh import Result, SshRunner  # noqa: E402
from rep.wordpress import WpSite  # noqa: E402


class RecordingRunner(SshRunner):
    """A runner that records commands instead of connecting anywhere."""

    def __init__(self, **kwargs):
        super().__init__(host="192.0.2.1", user="u", dry_run=True, **kwargs)
        self.commands: list[str] = []

    def run(self, command: str, *, cwd: str = "") -> Result:
        full = f"cd {cwd} && {command}" if cwd else command
        self.commands.append(full)
        return Result(command=full, exit_code=0, stdout="", stderr="")


def make_site() -> tuple[WpSite, RecordingRunner]:
    runner = RecordingRunner()
    return WpSite(runner=runner, docroot="/home/u/example.com"), runner


class TestQuoting:
    def test_values_with_spaces_and_quotes_are_escaped(self):
        site, runner = make_site()
        site.wp("option", "update", "blogname", "O'Brien Homes & Co")
        cmd = runner.commands[-1]
        # The apostrophe must be escaped, and the whole value kept as one arg.
        assert "'O'\"'\"'Brien Homes & Co'" in cmd

    def test_runs_inside_the_docroot(self):
        site, runner = make_site()
        site.wp("core", "version")
        assert runner.commands[-1].startswith("cd /home/u/example.com && ")

    def test_semicolons_cannot_break_out(self):
        site, runner = make_site()
        site.wp("option", "update", "blogname", "; rm -rf /")
        assert "; rm -rf /" not in runner.commands[-1].replace("'; rm -rf /'", "")


class TestSetOptions:
    def test_public_none_leaves_indexing_untouched(self):
        site, runner = make_site()
        site.set_options("T", "Tag", "Asia/Bangkok", public=None)
        assert not any("blog_public" in c for c in runner.commands)

    def test_public_false_disables_indexing(self):
        site, runner = make_site()
        site.set_options("T", "Tag", "Asia/Bangkok", public=False)
        assert any("blog_public 0" in c for c in runner.commands)

    def test_public_true_enables_indexing(self):
        site, runner = make_site()
        site.set_options("T", "Tag", "Asia/Bangkok", public=True)
        assert any("blog_public 1" in c for c in runner.commands)

    def test_permalinks_untouched_unless_asked(self):
        # Rewriting the structure changes the URL of every published post.
        site, runner = make_site()
        site.set_options("T", "Tag", "Asia/Bangkok", public=None)
        assert not any("rewrite" in c for c in runner.commands)

    def test_permalinks_set_when_given(self):
        site, runner = make_site()
        site.set_options(permalinks="/%postname%/")
        assert any("rewrite structure /%postname%/" in c for c in runner.commands)
        assert any("rewrite flush" in c for c in runner.commands)

    def test_empty_title_leaves_the_site_name_alone(self):
        site, runner = make_site()
        site.set_options(title="", tagline="", timezone="")
        assert not any("blogname" in c for c in runner.commands)
        assert not any("blogdescription" in c for c in runner.commands)
        assert not any("timezone_string" in c for c in runner.commands)

    def test_no_arguments_is_a_no_op(self):
        site, runner = make_site()
        site.set_options()
        assert runner.commands == []


class TestIdempotence:
    def test_install_core_is_skipped_when_already_installed(self, monkeypatch):
        site, runner = make_site()
        monkeypatch.setattr(site, "is_installed", lambda: True)
        site.install_core("https://x.com", "T", "admin", "pw", "a@b.c")
        assert not any("core install" in c for c in runner.commands)

    def test_download_core_is_skipped_when_files_exist(self, monkeypatch):
        site, runner = make_site()
        monkeypatch.setattr(site, "has_core_files", lambda: True)
        site.download_core()
        assert not any("core download" in c for c in runner.commands)


class TestStateMismatchGuard:
    """A `new` site that already has WordPress must be refused, not overwritten."""

    def _run(self, state: str, installed: bool):
        import sys
        from pathlib import Path as _P
        sys.path.insert(0, str(_P(__file__).resolve().parents[1] / "src"))
        from rep.config import Site
        from rep.cpanel import CpanelClient
        from rep.provision import provision_site
        import rep.wordpress as wpmod

        runner = RecordingRunner()
        cp = CpanelClient(host="192.0.2.1", user="cp", token="t", dry_run=True)
        site = Site(domain="example.com", state=state, title="X")

        original = wpmod.WpSite.is_installed
        wpmod.WpSite.is_installed = lambda self: installed
        try:
            return provision_site(
                site, cp, runner, "/home/cp", {"example.com"}, None,
                domains_known=True, do_listings=False,
            )
        finally:
            wpmod.WpSite.is_installed = original

    def test_new_site_with_existing_wordpress_is_refused(self):
        report = self._run("new", installed=True)
        assert report.failed
        state_step = next(s for s in report.steps if s.name == "state")
        assert "already installed" in state_step.detail
        # It must stop before doing anything else to the site.
        assert not any(s.name in ("theme", "plugins", "settings") for s in report.steps)

    def test_new_site_with_no_wordpress_proceeds(self):
        report = self._run("new", installed=False)
        assert not report.failed
        assert any(s.name == "wordpress" for s in report.steps)

    def test_live_site_with_existing_wordpress_proceeds(self):
        report = self._run("live", installed=True)
        assert not report.failed
        assert not any(s.name == "state" for s in report.steps)
