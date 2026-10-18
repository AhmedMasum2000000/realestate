"""Tests for multi-host support and running without a control panel."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.cli import make_clients  # noqa: E402
from rep.config import ConfigError, Host, load_all  # noqa: E402
from rep.provision import provision_site  # noqa: E402
import rep.wordpress as wpmod  # noqa: E402
from tests.helpers import RecordingRunner  # noqa: E402


def write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "sites.yml"
    path.write_text(body, encoding="utf-8")
    return path


class TestHostConfig:
    def test_shipped_config_loads_hosts(self):
        sites, hosts = load_all()
        assert "default" in hosts
        assert hosts["default"].kind == "cpanel"
        assert all(s.host in hosts for s in sites)

    def test_config_without_hosts_block_still_works(self, tmp_path):
        sites, hosts = load_all(write(tmp_path, """
sites:
  - {domain: a.com, state: new, title: A}
"""))
        assert hosts["default"].kind == "cpanel"
        assert sites[0].host == "default"

    def test_unknown_host_is_rejected(self, tmp_path):
        with pytest.raises(ConfigError, match="not defined"):
            load_all(write(tmp_path, """
hosts:
  main: {kind: cpanel}
sites:
  - {domain: a.com, state: new, title: A, host: typo}
"""))

    def test_bad_kind_is_rejected(self, tmp_path):
        with pytest.raises(ConfigError, match="kind"):
            load_all(write(tmp_path, """
hosts:
  main: {kind: ftp}
sites:
  - {domain: a.com, state: new, title: A, host: main}
"""))

    def test_sites_can_sit_on_different_hosts(self, tmp_path):
        sites, hosts = load_all(write(tmp_path, """
hosts:
  main: {kind: cpanel}
  other: {kind: ssh, ssh_host: 1.2.3.4, ssh_user: u1, home: /home/u1}
sites:
  - {domain: a.com, state: live, host: main}
  - {domain: b.com, state: live, host: other}
"""))
        assert [s.host for s in sites] == ["main", "other"]
        assert hosts["other"].can_create_sites is False
        assert hosts["other"].resolved_home({}) == "/home/u1"


class TestEnvResolution:
    def test_suffixed_key_wins_for_its_host(self):
        host = Host(name="hostinger", kind="ssh")
        env = {"SSH_KEY_PATH": "/generic", "SSH_KEY_PATH_HOSTINGER": "/specific"}
        assert host.env_key("SSH_KEY_PATH", env) == "/specific"

    def test_falls_back_to_unsuffixed(self):
        host = Host(name="default", kind="cpanel")
        assert host.env_key("SSH_KEY_PATH", {"SSH_KEY_PATH": "/generic"}) == "/generic"

    def test_hyphens_in_host_names_become_underscores(self):
        host = Host(name="my-box", kind="ssh")
        assert host.env_key("SSH_USER", {"SSH_USER_MY_BOX": "u"}) == "u"

    def test_home_derived_from_user_when_unset(self):
        host = Host(name="default", kind="cpanel")
        assert host.resolved_home({"SSH_USER": "casapat"}) == "/home/casapat"


class TestClientConstruction:
    def test_ssh_host_gets_no_cpanel_client(self):
        cp, ssh = make_clients(
            Host(name="hostinger", kind="ssh"),
            {"SSH_HOST_HOSTINGER": "h", "SSH_USER_HOSTINGER": "u"},
            dry_run=True,
        )
        assert cp is None
        assert ssh.host == "h" and ssh.user == "u"

    def test_cpanel_host_gets_both(self):
        cp, ssh = make_clients(
            Host(name="default", kind="cpanel"),
            {"SSH_HOST": "s", "SSH_USER": "u", "CPANEL_HOST": "c",
             "CPANEL_USER": "cu", "CPANEL_API_TOKEN": "t"},
            dry_run=True,
        )
        assert cp is not None and cp.user == "cu"


class TestProvisioningWithoutAControlPanel:
    """The majority case here: the site already exists, so no panel is needed."""

    def _provision(self, installed: bool, cp=None):
        from rep.config import Site
        runner = RecordingRunner()
        site = Site(domain="example.com", state="live", title="", host="h")
        original = wpmod.WpSite.is_installed
        wpmod.WpSite.is_installed = lambda self: installed
        try:
            return provision_site(site, cp, runner, "/home/u", set(), None,
                                  domains_known=False, do_listings=False)
        finally:
            wpmod.WpSite.is_installed = original

    def test_existing_site_provisions_fully_without_cpanel(self):
        report = self._provision(installed=True)
        assert not report.failed
        names = [s.name for s in report.steps]
        # Everything WP-CLI can do still runs.
        for step in ("settings", "theme", "plugins", "logo", "listing type"):
            assert step in names

    def test_domain_step_explains_the_limitation(self):
        report = self._provision(installed=True)
        domain = next(s for s in report.steps if s.name == "domain")
        assert domain.status == "skipped"
        assert "no control panel" in domain.detail

    def test_new_install_without_a_panel_fails_clearly(self):
        report = self._provision(installed=False)
        assert report.failed
        db = next(s for s in report.steps if s.name == "database")
        assert "cannot be created" in db.detail
        # It must stop rather than half-install WordPress with no database.
        assert not any(s.name == "wordpress" for s in report.steps)
