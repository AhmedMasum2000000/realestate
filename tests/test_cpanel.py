"""Tests for cPanel naming rules and the dry-run guarantee."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.cpanel import CpanelClient, db_names, generate_password  # noqa: E402
from rep.provision import resolve_docroot  # noqa: E402
from rep.config import load_sites  # noqa: E402


class TestDbNames:
    @pytest.mark.parametrize(
        "slug",
        ["pattayahomespro_com", "secondhomethailand_com", "propertiesshare_com",
         "a_very_long_domain_name_that_keeps_going_com"],
    )
    def test_within_mysql_limits(self, slug):
        db, user = db_names("casapat", slug)
        # cPanel stores names prefixed; MySQL caps identifiers at 64.
        assert len(db) <= 64 and len(user) <= 64
        assert db.startswith("casapat_") and user.startswith("casapat_")

    def test_tld_is_dropped(self):
        db, user = db_names("cp", "pattayahomespro_com")
        assert "com" not in db.replace("cp_", "")
        assert db == "cp_pattayahomesprowp"
        assert user == "cp_pattayahomesprou"

    def test_distinct_per_site(self):
        names = {db_names("cp", s) for s in
                 ["thaihomespro_com", "pattayahomepro_com", "pattayahomespro_com"]}
        assert len(names) == 3

    def test_deterministic(self):
        assert db_names("cp", "x_com") == db_names("cp", "x_com")


class TestPassword:
    def test_length_and_complexity(self):
        for _ in range(50):
            pw = generate_password()
            assert len(pw) == 28
            assert any(c.islower() for c in pw)
            assert any(c.isupper() for c in pw)
            assert any(c.isdigit() for c in pw)
            assert any(c in "!@#%^*_-+=" for c in pw)

    def test_no_shell_hostile_characters(self):
        # Quotes, backslashes and backticks would break wp-config or the shell.
        for _ in range(50):
            assert not set(generate_password()) & set("\"'`\\$;|&<>()")

    def test_values_differ(self):
        assert len({generate_password() for _ in range(20)}) == 20


class TestDryRun:
    def test_mutating_calls_do_not_touch_the_network(self):
        # host is unroutable on purpose: if dry-run leaked, this would raise.
        cp = CpanelClient(host="192.0.2.1", user="u", token="t", dry_run=True)
        for result in (
            cp.add_addon_domain("example.com", "/home/u/example.com", "example"),
            cp.create_database("u_db"),
            cp.create_database_user("u_user", "pw"),
            cp.grant_all("u_user", "u_db"),
            cp.request_autossl(),
        ):
            assert result["_dry_run"] is True

    def test_secrets_are_masked_in_the_plan(self):
        cp = CpanelClient(host="192.0.2.1", user="u", token="t", dry_run=True)
        label = cp.create_database_user("u_user", "SuperSecret123!")["_label"]
        assert "SuperSecret123!" not in label
        assert "***" in label


class TestDocroot:
    def test_main_domain_uses_public_html(self):
        site = next(s for s in load_sites() if s.domain == "pattayahomespro.com")
        path = resolve_docroot(site, "/home/casapat", set(), "pattayahomespro.com")
        assert path == "/home/casapat/public_html"

    def test_addon_domain_gets_its_own_directory(self):
        site = next(s for s in load_sites() if s.domain == "thaihomespro.com")
        path = resolve_docroot(site, "/home/casapat", set(), "pattayahomespro.com")
        assert path == "/home/casapat/thaihomespro.com"

    def test_trailing_slash_in_home_is_handled(self):
        site = next(s for s in load_sites() if s.domain == "thaihomespro.com")
        assert resolve_docroot(site, "/home/casapat/", set(), None) == "/home/casapat/thaihomespro.com"
