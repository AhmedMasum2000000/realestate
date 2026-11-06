# Google Search Console

pattayahomepro.com is connected to Search Console through Google's official
APIs, using a service account. Everything runs from GitHub Actions.

| When | What happens |
|---|---|
| Once, by hand: **Search Console** workflow, mode `setup` | Proves ownership (a DNS TXT record added through cPanel, or a meta tag on the home page if DNS is elsewhere), adds the property, makes your Google account an owner, submits `sitemap.xml` |
| Every **Go live** run (mode `apply`) | Resubmits the sitemap so new and changed pages are picked up |
| Every Monday 09:00 Pattaya time | Resubmits the sitemap, then opens a GitHub issue labelled `search-console` with clicks, impressions, top searches, top pages, sitemap status and index status for key pages (the previous report is closed) |
| By hand: mode `submit` / `report` | The same two steps on demand |

State lives in `data/gsc.json` (which property, how it was verified, and the
meta token when that method is used). The site build reads it, so a meta tag,
once issued, stays on every future deploy — removing it would make Google drop
the verification.

There is no API to "request indexing" for ordinary pages (Google's Indexing
API only covers job postings and livestreams), so the sitemap is the lever.

## One-time setup

1. <https://console.cloud.google.com/> → create a project (any name).
2. APIs & Services → Library → enable **Google Search Console API** and
   **Site Verification API**.
3. IAM & Admin → Service Accounts → **Create service account** (any name, no
   roles needed) → open it → Keys → Add key → Create new key → **JSON**. A
   `.json` file downloads.
4. GitHub → this repo → Settings → Secrets and variables → Actions → New
   repository secret: name `GOOGLE_SERVICE_ACCOUNT_JSON`, value: the whole
   contents of that file.
5. Actions → **Search Console** → Run workflow → mode `setup`, owner: the Google
   account you sign in to Search Console with.

## Locally

```
export GOOGLE_SERVICE_ACCOUNT_JSON="$(cat key.json)"
bin/gsc status      # exit 0 once verified
bin/gsc submit
bin/gsc report
```
