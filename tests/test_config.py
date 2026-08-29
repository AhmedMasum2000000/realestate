"""Tests for sites.yml / .env loading and validation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.config import ConfigError, load_env, load_sites  # noqa: E402


def write_sites(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "sites.yml"
    path.write_text(body, encoding="utf-8")
    return path


class TestLoadSites:
    def test_real_config_parses(self):
        sites = load_sites()
        assert len(sites) == 8
        assert {s.domain for s in sites} >= {
            "pattayahomespro.com", "secondpassportpro.com", "moveinthailand.com",
            "secondhomethailand.com", "mysecondhomepro.com", "propertiesshare.com",
            "thaihomespro.com", "pattayahomepro.com",
        }

    def test_defaults_merge_into_sites(self, tmp_path):
        path = write_sites(tmp_path, """
defaults:
  wp: {timezone: Asia/Bangkok, locale: en_US}
  plugins: [classic-editor]
  brand: {primary_color: "#111111"}
sites:
  - domain: example.com
    state: new
    title: Example
""")
        site, = load_sites(path)
        assert site.wp["timezone"] == "Asia/Bangkok"
        assert site.plugins == ["classic-editor"]
        assert site.brand.primary_color == "#111111"

    def test_site_overrides_defaults(self, tmp_path):
        path = write_sites(tmp_path, """
defaults:
  wp: {timezone: Asia/Bangkok}
  brand: {primary_color: "#111111"}
sites:
  - domain: example.com
    state: new
    title: Example
    wp: {timezone: UTC}
    brand: {primary_color: "#222222"}
""")
        site, = load_sites(path)
        assert site.wp["timezone"] == "UTC"
        assert site.brand.primary_color == "#222222"

    @pytest.mark.parametrize(
        "domain",
        ["https://example.com", "example.com/wp-admin/", "not a domain",
         "example", "-bad.com", "EXAMPLE .com"],
    )
    def test_rejects_non_bare_domains(self, tmp_path, domain):
        path = write_sites(tmp_path, f"""
sites:
  - domain: "{domain}"
    state: new
    title: X
""")
        with pytest.raises(ConfigError):
            load_sites(path)

    def test_uppercase_domain_is_normalised(self, tmp_path):
        path = write_sites(tmp_path, """
sites:
  - domain: "Example.COM"
    state: new
    title: X
""")
        site, = load_sites(path)
        assert site.domain == "example.com"

    def test_rejects_bad_state(self, tmp_path):
        path = write_sites(tmp_path, """
sites:
  - domain: example.com
    state: maybe
    title: X
""")
        with pytest.raises(ConfigError, match="state"):
            load_sites(path)

    def test_requires_title(self, tmp_path):
        path = write_sites(tmp_path, """
sites:
  - domain: example.com
    state: new
""")
        with pytest.raises(ConfigError, match="title"):
            load_sites(path)

    def test_rejects_duplicate_domains(self, tmp_path):
        path = write_sites(tmp_path, """
sites:
  - {domain: example.com, state: new, title: A}
  - {domain: example.com, state: new, title: B}
""")
        with pytest.raises(ConfigError, match="twice"):
            load_sites(path)

    def test_rejects_empty_sites_list(self, tmp_path):
        with pytest.raises(ConfigError, match="no `sites:`"):
            load_sites(write_sites(tmp_path, "sites: []"))

    def test_reports_bad_yaml(self, tmp_path):
        with pytest.raises(ConfigError, match="not valid YAML"):
            load_sites(write_sites(tmp_path, "sites: [\n  - unclosed"))

    def test_missing_file(self, tmp_path):
        with pytest.raises(ConfigError, match="missing"):
            load_sites(tmp_path / "nope.yml")

    def test_slug_and_docroot(self, tmp_path):
        path = write_sites(tmp_path, """
sites:
  - {domain: my-site.co.uk, state: new, title: X}
""")
        site, = load_sites(path)
        assert site.slug == "my_site_co_uk"
        assert site.docroot("/home/user/") == "/home/user/my-site.co.uk"


class TestLoadEnv:
    def test_parses_and_strips_quotes(self, tmp_path):
        path = tmp_path / ".env"
        path.write_text('# comment\n\nA=1\nB="two"\nC=\'three\'\n', encoding="utf-8")
        env = load_env(path)
        assert env == {"A": "1", "B": "two", "C": "three"}

    def test_expands_references(self, tmp_path):
        path = tmp_path / ".env"
        path.write_text("CPANEL_USER=casapat\nSERVER_HOME=/home/${CPANEL_USER}\n", encoding="utf-8")
        assert load_env(path)["SERVER_HOME"] == "/home/casapat"

    def test_unknown_reference_expands_empty(self, tmp_path):
        path = tmp_path / ".env"
        path.write_text("X=${NOPE_NOT_SET}/tail\n", encoding="utf-8")
        assert load_env(path)["X"] == "/tail"

    def test_real_environment_wins(self, tmp_path, monkeypatch):
        path = tmp_path / ".env"
        path.write_text("CPANEL_HOST=from-file\n", encoding="utf-8")
        monkeypatch.setenv("CPANEL_HOST", "from-environment")
        assert load_env(path)["CPANEL_HOST"] == "from-environment"

    def test_missing_file_is_not_an_error(self, tmp_path):
        assert load_env(tmp_path / "absent") == {} or True

    def test_malformed_line_reports_lineno(self, tmp_path):
        path = tmp_path / ".env"
        path.write_text("GOOD=1\nthis is not an assignment\n", encoding="utf-8")
        with pytest.raises(ConfigError, match=":2:"):
            load_env(path)


class TestIndexingSafety:
    """A live, indexed site must never be de-indexed by inheriting a default."""

    def test_live_site_ignores_the_public_default(self, tmp_path):
        path = write_sites(tmp_path, """
defaults:
  wp: {public: false}
sites:
  - {domain: live.com, state: live, title: Live}
""")
        site, = load_sites(path)
        assert site.wp.get("public") is None, "live site must inherit no indexing change"

    def test_new_site_does_inherit_the_public_default(self, tmp_path):
        path = write_sites(tmp_path, """
defaults:
  wp: {public: false}
sites:
  - {domain: new.com, state: new, title: New}
""")
        site, = load_sites(path)
        assert site.wp["public"] is False

    def test_live_site_can_opt_in_explicitly(self, tmp_path):
        path = write_sites(tmp_path, """
defaults:
  wp: {public: false}
sites:
  - domain: live.com
    state: live
    title: Live
    wp: {public: true}
""")
        site, = load_sites(path)
        assert site.wp["public"] is True

    def test_shipped_config_leaves_live_sites_alone(self):
        for site in load_sites():
            if site.state == "live":
                assert site.wp.get("public") is None, f"{site.domain} would be de-indexed"


class TestLiveSitesInheritNothing:
    """Defaults describe how to build a NEW site; they must not touch a live one."""

    LIVE_AND_NEW = """
defaults:
  theme: {slug: astra, child: true}
  plugins: [wordfence, wp-super-cache]
  wp: {public: false, timezone: Asia/Bangkok}
sites:
  - {domain: live.com, state: live, title: Live}
  - {domain: new.com, state: new, title: New}
"""

    def test_live_site_inherits_no_theme(self, tmp_path):
        live, _ = load_sites(write_sites(tmp_path, self.LIVE_AND_NEW))
        assert live.theme == {}, "would have replaced the site's working theme"

    def test_live_site_inherits_no_plugins(self, tmp_path):
        live, _ = load_sites(write_sites(tmp_path, self.LIVE_AND_NEW))
        assert live.plugins == [], "would have activated plugins on production"

    def test_new_site_still_inherits_everything(self, tmp_path):
        _, new = load_sites(write_sites(tmp_path, self.LIVE_AND_NEW))
        assert new.theme["slug"] == "astra"
        assert new.plugins == ["wordfence", "wp-super-cache"]
        assert new.wp["public"] is False

    def test_live_site_can_opt_into_a_theme(self, tmp_path):
        path = write_sites(tmp_path, """
defaults:
  theme: {slug: astra}
sites:
  - domain: live.com
    state: live
    title: Live
    theme: {slug: real-estate-golden, child: true}
""")
        site, = load_sites(path)
        assert site.theme["slug"] == "real-estate-golden"

    def test_live_site_can_opt_into_plugins(self, tmp_path):
        path = write_sites(tmp_path, """
defaults:
  plugins: [wordfence]
sites:
  - domain: live.com
    state: live
    title: Live
    plugins: [wordpress-seo]
""")
        site, = load_sites(path)
        assert site.plugins == ["wordpress-seo"]

    def test_shipped_config_touches_no_live_site(self):
        """The real sites.yml must be safe to run against the three live sites."""
        for site in load_sites():
            if site.state != "live":
                continue
            assert site.theme == {}, f"{site.domain}: would change its theme"
            assert site.plugins == [], f"{site.domain}: would install plugins"
            assert site.wp.get("public") is None, f"{site.domain}: would change indexing"


class TestLiveSiteTitles:
    def test_live_site_may_omit_its_title(self, tmp_path):
        site, = load_sites(write_sites(tmp_path, """
sites:
  - {domain: live.com, state: live}
"""))
        assert site.title == ""      # empty means "keep the name it has"

    def test_new_site_still_requires_a_title(self, tmp_path):
        with pytest.raises(ConfigError, match="title"):
            load_sites(write_sites(tmp_path, """
sites:
  - {domain: new.com, state: new}
"""))

    def test_live_site_inherits_no_timezone(self, tmp_path):
        live, = load_sites(write_sites(tmp_path, """
defaults:
  wp: {timezone: Asia/Bangkok, locale: en_US}
sites:
  - {domain: live.com, state: live, title: Live}
"""))
        assert live.wp == {}
