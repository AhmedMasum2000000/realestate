"""bin/inventory against a simulated cPanel account: read-only and complete."""

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class FakeCpanel:
    def __init__(self, *a, dry_run=False, **k):
        assert dry_run, "inventory must never be able to change the account"

    def list_domains(self):
        return {"main_domain": "pattayahomepro.com", "addon_domains": ["moveinthailand.com"],
                "parked_domains": [], "sub_domains": ["moveinthailand.pattayahomepro.com"]}

    def docroot(self, domain):
        return {"pattayahomepro.com": "pattayahomepro.com", "moveinthailand.com": "moveinthailand.com"}[domain]

    def list_dir(self, path):
        return {"pattayahomepro.com": {"index.html": 1, "assets": 0},
                "moveinthailand.com": {"wp-config.php": 1, "index.php": 1}}[path]


def test_inventory(monkeypatch, capsys):
    loader = SourceFileLoader("inventory", str(ROOT / "bin" / "inventory"))
    spec = importlib.util.spec_from_loader("inventory", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)

    monkeypatch.setattr(mod, "CpanelClient", FakeCpanel)
    monkeypatch.setattr(mod, "live", lambda d: "200")
    monkeypatch.setattr(mod, "dig", lambda kind, d: [] if d == "nosuch.com" else
                        (["dns1.namecheaphosting.com"] if kind == "NS" else ["162.0.215.149"]))
    for k in ("CPANEL_HOST", "CPANEL_USER", "CPANEL_API_TOKEN"):
        monkeypatch.setenv(k, "x")
    monkeypatch.setattr(sys, "argv", ["inventory", "nosuch.com", "MoveInThailand.com"])

    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "| moveinthailand.com | addon | moveinthailand.com | WordPress | cPanel (editable) | 200 |" in out
    assert "| pattayahomepro.com | main | pattayahomepro.com | static site |" in out
    assert "| nosuch.com | not on this account |" in out and "no DNS" in out
    assert out.count("moveinthailand.com | addon") == 1, "an asked-for account domain is listed once"
