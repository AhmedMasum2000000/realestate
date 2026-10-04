"""bin/go-live against a simulated cPanel: order of operations and the undo path."""

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def load_golive():
    loader = SourceFileLoader("golive", str(ROOT / "bin" / "go-live"))
    spec = importlib.util.spec_from_loader("golive", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class FakeCpanel:
    def __init__(self, *a, dry_run=True, **k):
        self.dry_run = dry_run
        self.calls = []
        self.files = ["public_html", "public_html.wp-20260101-000000"]

    def docroot(self, domain):
        return "public_html"

    def full_backup(self):
        self.calls.append(("backup",))

    def mkdir(self, parent, name):
        self.calls.append(("mkdir", f"{parent}/{name}"))

    def upload(self, local, remote):
        self.calls.append(("upload", remote))

    def extract(self, archive, dest):
        self.calls.append(("extract", dest))

    def rename(self, src, dst):
        self.calls.append(("rename", src, dst))

    def _api2(self, module, fn, params, mutating):
        self.calls.append((fn, params.get("op")))

    def _call(self, module, fn, params=None, mutating=False):
        return {"data": [{"file": f} for f in self.files]}


@pytest.fixture
def golive(monkeypatch, tmp_path):
    mod = load_golive()
    fake = {}

    def factory(*a, **k):
        fake["cp"] = FakeCpanel(*a, **k)
        return fake["cp"]

    monkeypatch.setattr(mod, "CpanelClient", factory)
    monkeypatch.setattr(mod, "load_env", lambda: {
        "CPANEL_HOST": "h", "CPANEL_USER": "u", "CPANEL_API_TOKEN": "t"})
    monkeypatch.setattr(mod, "build", lambda out: (out.mkdir(parents=True),
                                                   (out / "index.html").write_text("x")))
    return mod, fake


def run(mod, monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["go-live", *argv])
    return mod.main()


def test_backup_and_new_folder_come_before_the_swap(golive, monkeypatch):
    mod, fake = golive
    assert run(mod, monkeypatch, "--apply") == 0
    kinds = [c[0] for c in fake["cp"].calls]
    assert kinds.index("backup") < kinds.index("rename")
    assert kinds.index("extract") < kinds.index("rename")
    renames = [c for c in fake["cp"].calls if c[0] == "rename"]
    # WordPress is moved aside first, then the new site is moved in. Never deleted.
    assert renames[0][1] == "public_html" and ".wp-" in renames[0][2]
    assert renames[1][2] == "public_html" and ".new-" in renames[1][1]


def test_uploaded_archive_is_removed_from_the_public_folder(golive, monkeypatch):
    mod, fake = golive
    run(mod, monkeypatch, "--apply")
    assert ("fileop", "unlink") in fake["cp"].calls


def test_undo_restores_the_newest_wordpress_copy(golive, monkeypatch):
    mod, fake = golive
    assert run(mod, monkeypatch, "--apply", "--undo") == 0
    renames = [c for c in fake["cp"].calls if c[0] == "rename"]
    assert renames[-1] == ("rename", "public_html.wp-20260101-000000", "public_html")


def test_missing_credentials_stop_before_any_call(golive, monkeypatch):
    mod, fake = golive
    monkeypatch.setattr(mod, "load_env", lambda: {})
    assert run(mod, monkeypatch, "--apply") == 1
    assert "cp" not in fake
