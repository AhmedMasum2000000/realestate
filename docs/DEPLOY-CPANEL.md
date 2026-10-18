# Publishing to cPanel

Two ways to get the site onto your hosting. Pick one.

**Automatic** is the one you want if you'd rather never think about this again:
add five secrets to GitHub once, and every change republishes on its own.

---

## Option A — automatic, on every push

Set this up once and you are done.

### 1. Get an SSH key

In cPanel: **Security → SSH Access → Manage SSH Keys → Generate a New Key**.
Leave the passphrase **empty** (a passphrase cannot be typed by a robot).
Then click **Manage → Authorize** on the key you just made.

Click **View/Download** on the *private* key and copy the whole thing,
including the `-----BEGIN ...-----` and `-----END ...-----` lines.

### 2. Put it into GitHub

In the repository: **Settings → Secrets and variables → Actions → New repository secret**.

| Secret | Value | Required |
|---|---|---|
| `SSH_HOST` | your server address, e.g. `server123.web-hosting.com` | yes |
| `SSH_USER` | your cPanel username — not your email | yes |
| `SSH_PRIVATE_KEY` | the private key from step 1, pasted whole | yes |
| `SSH_PORT` | only if your host uses something other than 22 | no |
| `DEPLOY_DOCROOT` | only if not `public_html` — see below | no |

Your server address is on the cPanel home page under **General Information →
Shared IP Address**, or in the welcome email from your host.

### 3. That's it

Every push to `main` republishes the site. To publish right now without
changing anything, go to **Actions → Deploy to cPanel → Run workflow**.

The run fails loudly and changes nothing if a secret is missing or the build
does not pass its checks.

---

## Option B — publish by hand

```bash
cp config/.env.example config/.env     # then fill in the SSH section
bin/deploy-cpanel                      # dry run: prints every step, changes nothing
bin/deploy-cpanel --apply              # publish
```

`config/.env` is gitignored. Keep the credentials there; never paste them into
a chat window or a commit.

---

## What the document root should be

`DEPLOY_DOCROOT` is where the files land, relative to your home directory.

| Situation | Value |
|---|---|
| pattayahomepro.com is the **main** domain on the account | `public_html` |
| it is an **addon domain** | usually `public_html/pattayahomepro.com` |

cPanel → **Domains** lists the exact document root for each domain. Use that.

Getting this wrong publishes the site to the wrong folder — it does not break
anything, but nothing appears at the domain either.

---

## What a deploy actually does

1. Builds the site from `data/catalog.json` and `data/enrichment.json`.
2. Runs `bin/check-site` and `bin/check-layout`. **A failure here stops the
   deploy** — a broken build never reaches the live site.
3. Packs the build into one gzipped archive. Uploading ~1,700 files
   individually over SFTP takes minutes; one archive takes seconds.
4. Uploads it, extracts it into a staging folder.
5. Renames the current document root to `public_html.bak-<timestamp>` and
   renames the new one into place. A rename is near-instant, so visitors never
   see a half-written site.
6. Deletes all but the two most recent backups.

## Rolling back

```bash
bin/deploy-cpanel --apply --rollback
```

Restores the most recent backup. The version it replaces is kept as
`public_html.rollback`, so this is reversible too.

---

## If something goes wrong

**`Permission denied (publickey)`** — the key was generated but not authorized.
cPanel → SSH Access → Manage SSH Keys → **Authorize**.

**`Connection refused` or a timeout** — some hosts use a non-standard SSH port
(2222 is common) or require you to whitelist the connecting IP. GitHub Actions
runners do not have a fixed IP, so if your host enforces IP whitelisting, use
Option B from a machine whose IP you can whitelist.

**Nothing appears at the domain** — almost always `DEPLOY_DOCROOT` pointing at
the wrong folder. Check cPanel → Domains for the real document root.

**SSH is not available at all** — some shared plans disable it. Tell me and I
will add an FTP path instead; it is slower and less safe, but it works
everywhere.
