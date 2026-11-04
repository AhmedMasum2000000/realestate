#!/usr/bin/env python3
"""One-time sign-in for the Search Console workflow (gsc-vps.yml).

Opens Google's sign-in page in your browser. After you approve, it saves
GSC_CLIENT_ID, GSC_CLIENT_SECRET and GSC_REFRESH_TOKEN straight into the
repo's GitHub secrets with `gh`. The values are never printed.

    python tools/gsc_auth.py [path\\to\\client_secret_....json]

Without a path it uses the newest client_secret_*.json in your Downloads.
The OAuth client must be of type "Desktop app".
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO = "AhmedMasum2000000/realestate"
SCOPES = [
    "https://www.googleapis.com/auth/siteverification",
    "https://www.googleapis.com/auth/webmasters",
]


def find_client_file() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    files = sorted((Path.home() / "Downloads").glob("client_secret_*.json"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise SystemExit("No client_secret_*.json in Downloads — download it from Google Cloud first.")
    return files[0]


def find_gh() -> str:
    gh = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
    if not Path(gh).exists() and not shutil.which("gh"):
        raise SystemExit("GitHub CLI not found — install it with: winget install --id GitHub.cli -e")
    return gh


def main() -> int:
    from google_auth_oauthlib.flow import InstalledAppFlow

    client_file = find_client_file()
    gh = find_gh()
    print(f"Using {client_file.name}")
    flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline",
                                  authorization_prompt_message="Sign in as almasum5495@gmail.com in the browser window …")
    if not creds.refresh_token:
        raise SystemExit("Google returned no refresh token — run again and approve both permissions.")
    cfg = flow.client_config
    values = {"GSC_CLIENT_ID": cfg["client_id"], "GSC_CLIENT_SECRET": cfg["client_secret"],
              "GSC_REFRESH_TOKEN": creds.refresh_token}
    for name, value in values.items():
        subprocess.run([gh, "secret", "set", name, "--repo", REPO], input=value, text=True,
                       check=True, capture_output=True)
        print(f"saved {name}")
    print("Done. You can delete the client_secret JSON from Downloads now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
