"""Tests for public-site fingerprinting."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.survey import SiteFacts, survey  # noqa: E402
import rep.survey as survey_mod  # noqa: E402


class FakeResponse:
    def __init__(self, text: str, status: int = 200, url: str = "https://x.com/"):
        self.text, self.status_code, self.url = text, status, url


@pytest.fixture
def fake_get(monkeypatch):
    def install(body: str, status: int = 200):
        monkeypatch.setattr(
            survey_mod.requests, "get",
            lambda *a, **k: FakeResponse(body, status),
        )
    return install


WP_PAGE = """
<html><head><title>Pattaya Home Pro &#8211; Best Deals</title>
<meta name="generator" content="WordPress 7.1" /></head>
<body>
<link href="/wp-content/themes/hello-elementor/style.css">
<script src="/wp-content/plugins/elementor/assets/js/x.js"></script>
<script src="/wp-content/plugins/essential-real-estate/a.js"></script>
<script src="/wp-content/plugins/elementor/assets/js/y.js"></script>
</body></html>
"""


class TestWordPressDetection:
    def test_reads_title_generator_theme_and_plugins(self, fake_get):
        fake_get(WP_PAGE)
        facts = survey("example.com")
        assert facts.reachable and facts.is_wordpress
        assert facts.title == "Pattaya Home Pro &#8211; Best Deals"
        assert facts.generator == "WordPress 7.1"
        assert facts.theme == "hello-elementor"
        assert facts.plugins == ["elementor", "essential-real-estate"]  # deduped, sorted
        assert facts.verdict == "wordpress"
        assert facts.expected_state == "live"

    def test_non_wordpress_page(self, fake_get):
        fake_get("<html><head><title>Hello</title></head><body>hi</body></html>")
        facts = survey("example.com")
        assert not facts.is_wordpress
        assert facts.expected_state == "new"
        assert facts.verdict == "something else"


class TestInstallerDetection:
    @pytest.mark.parametrize(
        "body",
        [
            "<title>System configuration</title>",
            "<title>x</title> Database Configuration required",
            "<title>x</title> please enter your Envato purchase code",
            "<title>x</title><p>Installation Wizard</p>",
        ],
    )
    def test_flags_exposed_installers(self, fake_get, body):
        fake_get(f"<html><head>{body}</head><body></body></html>")
        facts = survey("example.com")
        assert facts.installer_exposed
        assert facts.verdict == "INSTALLER EXPOSED"

    def test_ordinary_site_is_not_flagged(self, fake_get):
        fake_get(WP_PAGE)
        assert not survey("example.com").installer_exposed

    def test_installer_verdict_outranks_wordpress(self, fake_get):
        # A half-installed WordPress is still an exposed installer.
        fake_get(WP_PAGE + "<p>Database configuration</p>")
        facts = survey("example.com")
        assert facts.is_wordpress and facts.verdict == "INSTALLER EXPOSED"


class TestUnreachable:
    def test_network_error_is_reported_not_raised(self, monkeypatch):
        def boom(*a, **k):
            raise survey_mod.requests.RequestException("no DNS")
        monkeypatch.setattr(survey_mod.requests, "get", boom)
        facts = survey("nope.example")
        assert not facts.reachable
        assert facts.verdict == "unreachable"
        assert "no DNS" in facts.error
        # An unreachable domain must never be reported as live.
        assert facts.expected_state == "new"

    def test_http_error_status(self, fake_get):
        fake_get("<title>Not Found</title>", status=404)
        assert survey("example.com").verdict == "http 404"


class TestFactsDefaults:
    def test_empty_facts_are_safe(self):
        facts = SiteFacts(domain="x.com")
        assert facts.verdict == "unreachable"
        assert facts.plugins == []
