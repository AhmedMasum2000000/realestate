# Site survey — 2026-08-29

What is actually being served at each of the eight domains, read from their
public homepages with `bin/survey`. No cPanel access was involved; this is all
visible to anyone.

Re-run it any time with `./bin/survey`.

## Results

| Domain | What is there | WordPress | Theme |
| --- | --- | --- | --- |
| pattayahomespro.com | Live real-estate site, real listings | 7.1 | `nexproperty` |
| secondpassportpro.com | Live visa/immigration site | 7.1 | `second-passport-pro-theme-v3` |
| moveinthailand.com | Live relocation site | yes | `kadence` |
| secondhomethailand.com | **Installed but unfinished** — was serving a cleaning-service template | yes | `blocksy` |
| mysecondhomepro.com | **Installed but unfinished** — placeholder content | 6.9.7 | `tourze-lite` |
| propertiesshare.com | **Does not resolve** | — | — |
| thaihomespro.com | **Exposed CMS installer** | no | — |
| pattayahomepro.com | Live real-estate site, real listings | 7.1 | `hello-elementor` |

## Three things that need a decision

### 1. thaihomespro.com is serving a public installer — deal with this first

The domain returns a page titled **"System configuration"**: the setup screen
of a CodeCanyon PHP CMS, asking for admin credentials, a MySQL host, database
name, user and password.

It is reachable by anyone. Whoever loads it can finish the installation, which
means choosing the admin account and pointing it at a database. Depending on
what the server allows, that is anything from a defaced site to a foothold on
the hosting account.

It is not urgent because of what it *is* — it is urgent because it is *public
and unfinished*. Either finish the install, delete the files, or block access
to the directory. Any of the three closes it.

This is also the domain originally suggested as the safe one to start with. It
is not; it needs clearing before provisioning touches it.

### 2. Five domains were mis-labelled as empty

`sites.yml` originally marked five domains `state: new`. Four of them already
have WordPress:

- **pattayahomepro.com** is a fully live real-estate site with published
  listings priced in baht. Provisioning it as `new` would have installed a
  different theme over it, activated four plugins on production, rewritten
  every URL and de-indexed it.
- **secondhomethailand.com** and **mysecondhomepro.com** have real but
  unfinished installs.

All are now `state: live`, so they inherit nothing and change nothing.

The code no longer relies on that config being right: if a domain marked `new`
turns out to have WordPress installed, provisioning stops and asks a human to
reconcile it, rather than writing over the site.

**propertiesshare.com does not resolve at all** — the domain is either
unregistered or its nameservers are not pointed at the host. DNS has to resolve
before AutoSSL can issue a certificate for it.

### 3. At least two sites may not be on cPanel at all

`secondpassportpro.com` and `mysecondhomepro.com` both run the
**`hostinger-reach`** plugin, which Hostinger installs on its own hosting.
Hostinger's panel is hPanel, not cPanel, and it has a different API.

If some of these sites are on Hostinger and others on a cPanel host, one set of
credentials will not reach all eight. Worth confirming before wiring anything
up — it changes what the automation has to talk to.

## The two real-estate sites use different listing plugins

- pattayahomespro.com — `essential-real-estate` + `wpdirectorykit`
- pattayahomepro.com — `essential-real-estate` + `wpdirectorykit`, on Elementor

Both already have a listings system with its own database schema. Importing a
CSV into an existing plugin's schema is a different job from importing into the
content type in this repo, and the toolkit deliberately refuses to install its
own `listing` type over one that already exists.

So before any import: which plugin should own the listings on each site?
