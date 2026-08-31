# Domain + WordPress provisioning

Automation for standing up and configuring the eight property sites on one
cPanel account: creates the domain, database and WordPress install, applies
branding, registers a property-listing content type, and imports listings from
a CSV export.

Built to be run **one site at a time**, and to be safe to re-run: every step
checks what is already there before changing anything.

## The sites

States below are what `bin/survey` found on 2026-08-29, not assumptions.
See [docs/SITE-SURVEY.md](docs/SITE-SURVEY.md) for the detail.

| Domain | State | What is actually there |
| --- | --- | --- |
| pattayahomespro.com | live | Real-estate site, published listings |
| secondpassportpro.com | live | Visa / immigration site |
| moveinthailand.com | live | Relocation site |
| secondhomethailand.com | live | Installed but unfinished |
| mysecondhomepro.com | live | Installed but unfinished |
| propertiesshare.com | new | Does not resolve |
| thaihomespro.com | new | **Exposed CMS installer — see the survey** |
| pattayahomepro.com | live | Real-estate site, published listings |

`live` means WordPress is already installed and we only configure it.
`new` means the domain and WordPress still have to be created.

### The rule for live sites

**A `live` site inherits nothing from the `defaults:` block.** Only settings
written on that site's own entry are applied; everything else is left exactly
as it is.

This exists because the defaults describe how to *build* a site, and applying
them to one that is already running would change things nobody asked to
change. On `pattayahomespro.com` — a working site with the `real-estate-golden`
theme, a `wdk-listing` plugin and published listings — the defaults would have:

- replaced its theme with Astra,
- installed and activated four plugins on production,
- rewritten every URL by forcing `/%postname%/` permalinks with a hard flush,
- renamed the site to a title that was guessed rather than observed,
- and de-indexed it from Google.

So on a live site: no theme change, no plugin installs, no permalink change,
no indexing change, and no rename — unless you write that setting on the site
yourself. A `new` site still gets the full defaults.

The toolkit also refuses to install its listing content type if the site
already runs a plugin registering a `listing` post type, rather than
colliding with it.

And it does not trust `state:` blindly. If a domain marked `new` turns out to
have WordPress installed, provisioning stops and asks a human to reconcile it
rather than writing over the site. Four of these eight domains were originally
mis-labelled `new`, so this guard is not hypothetical.

## Quick start

```bash
pip install -r requirements.txt

./bin/control --live                   # where does everything stand?
cp config/.env.example config/.env     # then fill it in -- see SETUP.md
./bin/check                            # prove the credentials work
./bin/provision thaihomespro.com       # dry run: prints the plan, changes nothing
./bin/provision thaihomespro.com --apply
```

**Dry run is the default.** Nothing is created, changed or deleted until you
add `--apply`. Read the plan first; it is short.

## Commands

| Command | What it does |
| --- | --- |
| `bin/control` | **Start here.** Every site's status, links, blockers and next command in one view. `--live` re-checks each domain, `--json` for tooling, `--next` for one line per site. |
| `bin/survey` | Checks what is actually served at each domain, from its public homepage. No credentials. |
| `bin/check` | Preflight. Validates config, tests cPanel + SSH, reports per-site readiness. Read-only. |
| `bin/inspect-csv <file>` | Shows how a listings CSV will be read: which columns were understood, which were not, and a preview of the first rows. Touches no server. |
| `bin/provision <domain>` | Provisions one site. Add `--apply` to make it real. |
| `bin/provision --all` | Every site in one pass. Prefer one at a time. |

Useful flags on `provision`:

- `--no-listings` — skip the CSV import (when only settings changed)
- `--sideload-images` — pull each listing's first photo into the media library.
  Slow, and shared hosting may throttle it, so it is off by default.

## What a run actually does

1. **Domain** — creates the addon domain in cPanel if it is not already there.
2. **Database** — creates the database and user, grants privileges. Names are
   derived from the domain, so they are stable across runs.
3. **WordPress** — downloads core, writes `wp-config.php`, runs the install.
   Skipped entirely if WordPress is already installed.
4. **Settings** — title, tagline, timezone, pretty permalinks. Search-engine
   indexing is left **off** until you set `public: true` in `config/sites.yml`.
5. **Theme and plugins** — installs the theme, builds a child theme so your
   edits survive updates, installs and activates the plugin list.
6. **Starter pages** — creates Home, Properties, About, Contact and Blog,
   makes Home the homepage instead of the post feed, and builds a navigation
   menu assigned to the theme's primary location. Without this a freshly
   provisioned site shows a sample post and nothing else. Live sites get none
   of it — pages are never added to a site that already has content.
7. **Branding** — uploads the logo and sets it as the site logo and favicon.
8. **Listing content type** — installs `wp/mu-plugin/casa-listings.php` as a
   must-use plugin, registering the `listing` post type with locations,
   property types and features.
9. **Listings** — parses the CSV and imports it. Listings are matched on their
   reference, so re-importing an updated export **updates** rows rather than
   duplicating them.
10. **SSL** — asks AutoSSL to issue certificates for anything newly created.

## Hosts

Sites do not have to be on the same server. `hosts:` in `config/sites.yml`
names each one, and each site says which it is on.

A host is one of two kinds:

| kind | Can do | Needs |
| --- | --- | --- |
| `cpanel` | Everything, including creating domains and databases | cPanel API token + SSH |
| `ssh` | Everything WP-CLI can do on a site that already exists | SSH only |

**Most of the work needs no control panel.** Settings, theme, plugins, logo,
the listing content type and the CSV import all run over SSH and WP-CLI, which
work the same on cPanel, Hostinger, Plesk or a plain VPS. cPanel is required
for exactly two things: creating a domain that does not exist yet, and creating
a database for a fresh WordPress install.

Seven of these eight domains already exist, so for them cPanel is needed for
nothing but requesting an SSL certificate.

If a site is on a host with no cPanel API, mark that host `kind: ssh`. The
toolkit then skips the two steps it cannot do, says so plainly, and runs the
rest. It refuses only one thing: installing WordPress from scratch on a host
where it cannot create a database.

Credentials are per host. `SSH_KEY_PATH` applies everywhere;
`SSH_KEY_PATH_HOSTINGER` overrides it for the host named `hostinger`.

## Configuration

Everything you routinely change lives in `config/sites.yml`: titles, taglines,
logo paths, which CSV feeds which site, plugins, theme.

Credentials live in `config/.env`, which is gitignored and never committed.

To feed one shared export into several sites, filter it per site:

```yaml
  - domain: pattayahomespro.com
    listings:
      csv: "data/listings-all.csv"
      filter:
        location: pattaya       # only rows whose location contains "pattaya"
```

If a column is read wrongly, map it explicitly — run `bin/inspect-csv` first to
see the exact header text:

```yaml
    listings:
      csv: "data/listings-all.csv"
      columns:
        price: "Asking Price (THB)"
        size_sqm: "Interior (sqm)"
```

## Layout

```
bin/           the three commands
config/        sites.yml (edit this) and .env (credentials, gitignored)
src/rep/       the implementation
  config.py      loads and validates sites.yml / .env
  cpanel.py      cPanel UAPI client -- domains, databases, SSL
  ssh.py         SSH/SFTP transport
  wordpress.py   WP-CLI driver -- install and configure
  listings.py    CSV parsing and column matching
  survey.py      fingerprints a public site (theme, plugins, installers)
  provision.py   orchestrates the steps above
wp/            code that runs inside WordPress
  mu-plugin/     listing post type, taxonomies, display helpers, styles
  templates/     archive, single and card templates for listings
data/          your CSV exports (gitignored)
assets/logos/  your logo files (gitignored)
tests/         run with: python3 -m pytest tests/
```

## Safety notes

- Dry run by default; `--apply` is always required to change anything.
- Generated passwords are written to `secrets/credentials.txt` (gitignored,
  mode 0600). Move them into a password manager and delete the file.
- The toolkit never deletes a domain, database or site. Removal is manual, on
  purpose.
- New sites launch with indexing disabled so Google does not index a
  half-finished site. Flip `public: true` per site when you are ready.
