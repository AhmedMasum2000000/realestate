"""Tests for the site preview generator."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.preview import (  # noqa: E402
    ILLUSTRATIONS, REQUIRED_PALETTE, SpecError, css, initials, load_spec, render,
)


@pytest.fixture(scope="module")
def sites():
    return load_spec()


class TestSpec:
    def test_all_eight_sites_present(self, sites):
        assert len(sites) == 8
        domains = {s.domain for s in sites}
        assert domains == {
            "pattayahomespro.com", "pattayahomepro.com", "thaihomespro.com",
            "secondhomethailand.com", "mysecondhomepro.com", "secondpassportpro.com",
            "moveinthailand.com", "propertiesshare.com",
        }

    def test_every_palette_is_complete_and_valid(self, sites):
        for site in sites:
            for key in REQUIRED_PALETTE:
                assert re.fullmatch(r"#[0-9a-fA-F]{6}", site.palette[key]), \
                    f"{site.domain}: palette.{key} is {site.palette[key]!r}"

    def test_each_site_has_its_own_identity(self, sites):
        """Eight businesses, not one template with the name swapped."""
        accents = [s.palette["accent"] for s in sites]
        assert len(set(accents)) == len(accents), "two sites share an accent colour"
        fonts = [(s.fonts["display"], s.fonts["body"]) for s in sites]
        assert len(set(fonts)) == len(fonts), "two sites share a type pairing"
        illustrations = [s.get("illustration") for s in sites]
        assert len(set(illustrations)) == len(illustrations), "two sites share an illustration"

    def test_every_illustration_exists(self, sites):
        for site in sites:
            assert site.get("illustration") in ILLUSTRATIONS

    def test_bad_archetype_is_rejected(self, tmp_path):
        path = tmp_path / "spec.yml"
        path.write_text("sites:\n  - {domain: a.com, archetype: nonsense, palette: {}}\n")
        with pytest.raises(SpecError, match="archetype"):
            load_spec(path)

    def test_bad_colour_is_rejected(self, tmp_path):
        path = tmp_path / "spec.yml"
        path.write_text(
            "sites:\n  - domain: a.com\n    archetype: listings\n"
            "    palette: {ink: 'not a colour'}\n"
        )
        with pytest.raises(SpecError, match="palette"):
            load_spec(path)


class TestRender:
    def test_pages_have_no_skeleton_tags(self, sites):
        # The artifact host wraps the file; emitting our own would nest documents.
        for site in sites:
            page = render(site)
            assert "<!doctype" not in page.lower()
            assert "<html" not in page.lower()
            assert "<body" not in page.lower()

    def test_title_is_early_enough_to_be_found(self, sites):
        for site in sites:
            assert f"<title>{site.name}</title>" in render(site)[:8192]

    def test_all_three_theme_states_are_defined(self, sites):
        for site in sites:
            sheet = css(site)
            assert ":root {" in sheet
            assert "@media (prefers-color-scheme: dark)" in sheet
            assert ':root[data-theme="dark"]' in sheet
            assert ':root:not([data-theme="light"])' in sheet

    def test_body_paints_its_own_background(self, sites):
        # A transparent body borrows the host's ground and breaks in one theme.
        for site in sites:
            assert "background:var(--ground)" in css(site).replace(" ", "")

    def test_tags_are_balanced(self, sites):
        for site in sites:
            page = render(site)
            for tag in ("section", "div", "article", "header", "footer", "ul"):
                assert page.count(f"<{tag}") == page.count(f"</{tag}>"), \
                    f"{site.domain}: unbalanced <{tag}>"

    def test_copy_is_escaped(self):
        from rep.preview import PreviewSite
        site = load_spec()[0]
        site.raw = dict(site.raw, hero_title="Homes & <script>alert(1)</script>")
        page = render(site)
        assert "<script>alert(1)</script>" not in page
        assert "&amp;" in page

    def test_no_placeholder_leaked(self, sites):
        for site in sites:
            page = render(site)
            assert "None" not in page
            assert "{" not in page.split("</style>")[1]

    def test_fonts_load_from_the_allowed_host(self, sites):
        for site in sites:
            page = render(site)
            assert "https://fonts.googleapis.com/css2?family=" in page
            assert "&display=swap" in page

    def test_every_archetype_renders(self, sites):
        seen = {s.archetype for s in sites}
        assert seen == {"listings", "advisory", "product"}
        for site in sites:
            assert len(render(site)) > 8000


class TestInitials:
    @pytest.mark.parametrize(
        "name,expected",
        [("Pattaya Homes Pro", "PH"), ("Move In Thailand", "MI"), ("Solo", "S")],
    )
    def test_two_letters_max(self, name, expected):
        assert initials(name) == expected
