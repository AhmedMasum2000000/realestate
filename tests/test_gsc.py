"""Search Console client and bin/gsc against a simulated Google API."""

import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rep.cpanel import CpanelError  # noqa: E402
from rep.gsc import GscError, SearchConsole, domain_property, url_property  # noqa: E402

KEY = json.dumps({"client_email": "bot@proj.iam.gserviceaccount.com"})


class Resp:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self._body = body if body is not None else {}
        self.content = json.dumps(self._body).encode() if body is not None else b""
        self.text = self.content.decode()

    def json(self):
        return self._body


class FakeGoogle:
    """Answers the handful of endpoints bin/gsc uses and records every call."""

    def __init__(self, verify_failures=0):
        self.calls = []
        self.owners = ["bot@proj.iam.gserviceaccount.com"]
        self.verify_failures = verify_failures

    def request(self, method, url, timeout=None, json=None):
        self.calls.append((method, url, json))
        if url.endswith("/token"):
            if json["verificationMethod"] == "META":
                return Resp(body={"token": '<meta name="google-site-verification" content="abc123" />'})
            return Resp(body={"token": "google-site-verification=xyz"})
        if "webResource?verificationMethod=" in url:
            if self.verify_failures:
                self.verify_failures -= 1
                return Resp(400, {"error": {"message": "token not found"}})
            ident = json["site"]["identifier"]
            # The real API returns the id percent-encoded.
            rid = quote(f"dns://{ident}" if json["site"]["type"] == "INET_DOMAIN" else ident, safe="")
            return Resp(body={"id": rid, "owners": self.owners})
        if "/webResource/" in url:
            if "%25" in url:
                return Resp(400, {"error": {"message": "The ID for this site is missing or invalid"}})
            if method == "PUT":
                self.owners = json["owners"]
            return Resp(body={"id": "x", "owners": self.owners})
        if "/searchAnalytics/query" in url:
            return Resp(body={"rows": []})
        if url.endswith("/sitemaps"):
            return Resp(body={"sitemap": [{"path": "https://pattayahomepro.com/sitemap.xml"}]})
        if "urlInspection" in url:
            return Resp(body={"inspectionResult": {"indexStatusResult": {"verdict": "PASS"}}})
        if method == "PUT":
            return Resp()
        return Resp(404, {"error": {"message": "unexpected " + url}})


# -- client ---------------------------------------------------------------

def test_properties():
    assert domain_property("example.com") == "sc-domain:example.com"
    assert url_property("example.com") == "https://example.com/"


def test_errors_carry_status_and_message():
    g = SearchConsole(KEY, session=FakeGoogle(verify_failures=1))
    with pytest.raises(GscError, match="400: token not found"):
        g.verify("SITE", "https://example.com/", "META")


def test_paths_are_url_encoded():
    fake = FakeGoogle()
    g = SearchConsole(KEY, session=fake)
    g.submit_sitemap("sc-domain:example.com", "https://example.com/sitemap.xml")
    url = fake.calls[-1][1]
    assert "/sites/sc-domain%3Aexample.com/sitemaps/https%3A%2F%2Fexample.com%2Fsitemap.xml" in url


def test_add_owner_is_idempotent():
    fake = FakeGoogle()
    g = SearchConsole(KEY, session=fake)
    g.add_owner("dns://example.com", "Me@Gmail.com")
    g.add_owner("dns://example.com", "me@gmail.com")
    assert fake.owners.count("Me@Gmail.com") == 1
    assert sum(1 for m, *_ in fake.calls if m == "PUT") == 1


def test_analytics_window_ends_before_the_reporting_lag():
    fake = FakeGoogle()
    SearchConsole(KEY, session=fake).analytics("sc-domain:x.com", 28, ["query"])
    body = fake.calls[-1][2]
    from datetime import date, timedelta
    assert body["endDate"] == (date.today() - timedelta(days=2)).isoformat()
    assert body["dimensions"] == ["query"]


# -- bin/gsc --------------------------------------------------------------

def load_cli(tmp_path, monkeypatch, fake):
    loader = SourceFileLoader("gsc_cli", str(ROOT / "bin" / "gsc"))
    spec = importlib.util.spec_from_loader("gsc_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    monkeypatch.setattr(mod, "STATE", tmp_path / "gsc.json")
    monkeypatch.setattr(mod, "client", lambda: SearchConsole(KEY, session=fake))
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    return mod


class FakeZone:
    def __init__(self, fail=False):
        self.records, self.fail = [], fail

    def _api2(self, module, function, params, *, mutating):
        if self.fail:
            raise CpanelError("ZoneEdit not permitted")
        if function == "add_zone_record":
            self.records.append({"txtdata": params["txtdata"]})
        return {"data": list(self.records)}


def test_setup_by_dns(tmp_path, monkeypatch):
    fake, zone = FakeGoogle(), FakeZone()
    cli = load_cli(tmp_path, monkeypatch, fake)
    monkeypatch.setenv("CPANEL_HOST", "premium329.web-hosting.com")
    monkeypatch.setattr(cli, "dig", lambda *a: ["dns1.namecheaphosting.com", "dns2.namecheaphosting.com"])
    monkeypatch.setattr(cli, "cpanel", lambda: zone)
    monkeypatch.setattr(cli, "wait_for_txt", lambda value, ns: True)

    assert cli.setup("me@gmail.com") == 0
    assert zone.records == [{"txtdata": "google-site-verification=xyz"}]
    state = json.loads((tmp_path / "gsc.json").read_text())
    assert state["method"] == "dns" and state["property"] == "sc-domain:pattayahomepro.com"
    assert state["verified"] and "meta" not in state
    assert "me@gmail.com" in fake.owners
    assert any("sitemaps/https%3A%2F%2Fpattayahomepro.com%2Fsitemap.xml" in u for _, u, _ in fake.calls)

    # A second run adds no duplicate record.
    cli.setup("me@gmail.com")
    assert len(zone.records) == 1


def test_setup_falls_back_to_meta_when_the_zone_cannot_be_edited(tmp_path, monkeypatch):
    fake = FakeGoogle()
    cli = load_cli(tmp_path, monkeypatch, fake)
    monkeypatch.setenv("CPANEL_HOST", "premium329.web-hosting.com")
    monkeypatch.setattr(cli, "dig", lambda *a: ["dns1.namecheaphosting.com"])
    monkeypatch.setattr(cli, "cpanel", lambda: FakeZone(fail=True))

    assert cli.setup("") == cli.NEEDS_DEPLOY
    state = json.loads((tmp_path / "gsc.json").read_text())
    assert state == {"method": "meta", "property": "https://pattayahomepro.com/", "meta": "abc123"}


def test_meta_flow_needs_a_deploy_then_verifies(tmp_path, monkeypatch):
    fake = FakeGoogle(verify_failures=2)
    cli = load_cli(tmp_path, monkeypatch, fake)
    monkeypatch.setattr(cli, "dig", lambda *a: ["dns1.registrar-servers.com"])
    monkeypatch.setattr(cli, "cpanel", lambda: None)

    assert cli.setup("me@gmail.com") == cli.NEEDS_DEPLOY
    assert cli.submit() == 1, "nothing is connected until Google has verified"

    # After the deploy: the token is reused, and Google's lag is retried through.
    assert cli.setup("me@gmail.com") == 0
    tokens = [c for c in fake.calls if c[1].endswith("/token")]
    assert len(tokens) == 1
    state = json.loads((tmp_path / "gsc.json").read_text())
    assert state["meta"] == "abc123" and state["verified"] == quote("https://pattayahomepro.com/", safe="")
    assert cli.submit() == 0


def test_meta_token_reaches_the_built_page(tmp_path):
    """The tag must be on the live home page, or Google cannot verify — and it
    must stay there on every later build, or Google drops the verification."""
    from rep.catalog.build import build
    root = tmp_path / "root"
    (root / "data").mkdir(parents=True)
    for name in ("catalog.json", "enrichment.json", "legacy-urls.json"):
        (root / "data" / name).symlink_to(ROOT / "data" / name)
    for name in ("templates", "assets"):
        (root / name).symlink_to(ROOT / name)

    build(root, tmp_path / "plain")
    assert "google-site-verification" not in (tmp_path / "plain" / "index.html").read_text()

    (root / "data" / "gsc.json").write_text(json.dumps({"method": "meta", "meta": "abc123"}))
    build(root, tmp_path / "tagged")
    home = (tmp_path / "tagged" / "index.html").read_text()
    assert '<meta name="google-site-verification" content="abc123">' in home


def test_report_renders_markdown(tmp_path, monkeypatch, capsys):
    fake = FakeGoogle()
    cli = load_cli(tmp_path, monkeypatch, fake)
    (tmp_path / "gsc.json").write_text(json.dumps(
        {"property": "sc-domain:pattayahomepro.com", "verified": "dns://pattayahomepro.com"}))
    assert cli.report() == 0
    out = capsys.readouterr().out
    assert "## Search Console — pattayahomepro.com" in out
    assert "_No data yet" in out
    assert "| / | PASS |" in out


def test_report_before_setup_fails_cleanly(tmp_path, monkeypatch):
    cli = load_cli(tmp_path, monkeypatch, FakeGoogle())
    assert cli.report() == 1
    assert cli.submit() == 1
