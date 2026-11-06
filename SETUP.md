# What I need from you

Four things. Nothing here should be pasted into a chat window — it all stays on
your own machine, in `config/.env`, which is gitignored.

---

## 1. cPanel details

In `config/.env`:

```
CPANEL_HOST=server123.yourhost.com
CPANEL_USER=your_cpanel_username
CPANEL_API_TOKEN=...
```

**Get the API token** (not your password):

1. Log into cPanel
2. **Security → Manage API Tokens → Create**
3. Name it `provisioning`, leave the expiry blank
4. Copy the token — cPanel shows it exactly once

`CPANEL_HOST` is the hostname you log into, without `https://` and without
`:2083`. If you log in at `https://server42.hostgator.com:2083`, the host is
`server42.hostgator.com`.

**Are all eight domains on one cPanel account?** If they are spread across
several accounts, tell me — the setup changes, and it is a small change.

## 2. SSH access

Installing WordPress needs SSH. Most cPanel plans include it; some hosts leave
it switched off until you ask.

In cPanel, look for **Security → SSH Access → Manage SSH Keys**. Generate a
key, authorize it, download the private key, and point `.env` at it:

```
SSH_KEY_PATH=C:/Users/Zakaria/.ssh/id_ed25519
```

If your host does not offer SSH, say so — there is a fallback path using
cPanel's WordPress Toolkit, but it does less.

## 3. The listings CSV

Drop your export into `data/`, then:

```bash
./bin/inspect-csv data/listings-all.csv
```

It prints which columns it understood and which it did not, without touching
any server. Send me that output and I will fix the mapping for your exact file.

Then point the sites at it in `config/sites.yml`:

```yaml
    listings:
      csv: "data/listings-all.csv"
```

**The files you referenced never reached me.** `HANDOFF.md`, the two
`listings-all.csv` files, `The Property Listing By Casa Pattaya.csv`, and
`Tha.7z` were all Windows paths on your own PC (`C:\Users\Zakaria\...`,
`D:\Tha.7z`). This session runs in a cloud container with no access to your
disk, so nothing was attached. Upload them into this conversation and I will
build the exact mapping for your columns.

## 4. Logos

Drop the image files into `assets/logos/`, then name them per site in
`config/sites.yml`:

```yaml
  - domain: pattayahomespro.com
    logo: "assets/logos/pattayahomespro.png"
```

PNG with a transparent background works best. Same caveat as above — the logos
you mentioned did not reach this session.

---

## Things I need you to decide

**Theme.** The default is Astra (free, fast, works with any page builder), with
a child theme so your edits survive updates. If you already use a theme on the
three live sites, tell me its name and I will match it.

**Are the three live sites really live?** `pattayahomespro.com`,
`secondpassportpro.com` and `moveinthailand.com` are marked `state: live`, so
the toolkit will configure them but never reinstall. If any of them is actually
an empty domain, change its state to `new` in `config/sites.yml`.

`pattayahomespro.com` is confirmed live — it runs the `real-estate-golden`
theme with a `wdk-listing` plugin and has published listings. Because of that
it now changes nothing by default. If you want something applied to it, write
it on that site's entry in `config/sites.yml` and it will be applied.

**Which plugin owns the listings on pattayahomespro.com?** It already has
`wdk-listing` managing properties. Importing your CSV into *that* plugin's
schema is a different job from importing into ours, and the toolkit will stop
rather than guess. Tell me which one you want to keep and I will wire the
import to it.

**Which site do we do first?** You said one at a time. I would start with a
`new` one — `thaihomespro.com` — because a mistake there costs nothing, unlike
on a live site.

---

## What I cannot do from here

This session runs in an isolated cloud container. It has no route to your
cPanel server, and I would not log into your hosting on your behalf even with
credentials — that is your account, and an automated change to a live site
should have you watching it.

So the split is: **I write and test the automation, you run it.** You run
`bin/check`, paste me the output, and I fix whatever it reports. That loop is
fast, and it keeps you in control of every change to a live site.

Everything in this repo is tested — 84 tests, `python3 -m pytest tests/`.
