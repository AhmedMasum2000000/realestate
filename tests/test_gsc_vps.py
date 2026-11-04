"""bin/gsc-vps against a simulated Google API and web."""

import json
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rep.gsc import SearchConsole  # noqa: E402

loader = SourceFileLoader("gsc_vps", str(ROOT / "bin" / "gsc-vps"))
spec = spec_from_loader("gsc_vps", loader)
gv = module_from_spec(spec)
loader.exec_module(gv)


class Resp:
    def __init__(self, status=200, body=None, text="", url=""):
        self.status_code = status
        self._body = body
        self.content = json.dumps(body).encode() if body is not None else b""
        self.text = text or self.content.decode()
        self.url = url

    def json(self):
        return self._body


class FakeGoogle:
    def __init__(self):
        self.calls = []

    def request(self, method, url, timeout=None, json=None):
        self.calls.append((method, url, json))
        if url.endswith("/token"):
            return Resp(body={"method": "FILE", "token": "google0123abcd.html"})
        if "webResource?verificationMethod=FILE" in url:
            return Resp(body={"id": "https%3A%2F%2Fwww.example.com%2F", "owners": ["me@gmail.com"]})
        return Resp(body={})


class FakeWeb:
    def get(self, url, timeout=None, allow_redirects=True):
        if url == "https://example.com/":
            return Resp(text="home", url="https://www.example.com/")
        if url.endswith("robots.txt"):
            return Resp(text="User-agent: *\nSitemap: https://www.example.com/sitemap-ledadpro.xml\n"
                             "Sitemap: https://other.com/x.xml\n")
        if url.endswith("google0123abcd.html"):
            return Resp(text="google-site-verification: google0123abcd.html")
        return Resp(404, text="no")


def test_prepare_then_verify(tmp_path, monkeypatch):
    monkeypatch.setattr(gv, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(gv, "resolves_to_vps", lambda h: h != "elsewhere.com")
    google = FakeGoogle()
    gsc = SearchConsole.from_refresh_token("id", "secret", "rt", session=google)
    web = FakeWeb()

    gv.prepare(["example.com", "elsewhere.com"], tmp_path / "out", gsc, http=web)
    f = tmp_path / "out" / "example.com" / "google0123abcd.html"
    assert f.read_text() == "google-site-verification: google0123abcd.html"
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["example.com"]["property"] == "https://www.example.com/"
    assert state["elsewhere.com"]["status"].startswith("skipped")

    assert gv.verify_all(gsc, http=web, pause=0) == 0
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["example.com"]["status"] == "verified"
    assert state["example.com"]["sitemaps"] == ["https://www.example.com/sitemap-ledadpro.xml"]
    urls = [u for _, u, _ in google.calls]
    assert any("/sites/https%3A%2F%2Fwww.example.com%2F/sitemaps/" in u for u in urls)

    # A second prepare reuses the stored file name instead of asking Google again.
    before = len(google.calls)
    (tmp_path / "state.json").write_text(json.dumps({"example.com": {
        "property": "https://www.example.com/", "file": "google0123abcd.html"}}))
    gv.prepare(["example.com"], tmp_path / "out2", gsc, http=web)
    assert len(google.calls) == before


def test_service_account_adds_the_owner(tmp_path, monkeypatch):
    monkeypatch.setattr(gv, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(gv, "resolves_to_vps", lambda h: True)
    google = FakeGoogle()
    gsc = SearchConsole(json.dumps({"client_email": "bot@p.iam.gserviceaccount.com"}), session=google)
    web = FakeWeb()
    gv.prepare(["example.com"], tmp_path / "out", gsc, http=web)
    assert gv.verify_all(gsc, http=web, pause=0) == 0
    puts = [j for m, u, j in google.calls if m == "PUT" and "/webResource/" in u]
    assert puts and gv.OWNER in puts[-1]["owners"]
