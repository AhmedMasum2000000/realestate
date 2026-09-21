# Search strategy — what will work, and what will get the sites penalised

Two of the five goals as stated carry real risk to the three sites that
currently rank. This sets out why, and what the version that works looks like.

## 1. Cross-linking the eight sites to each other

**As asked:** external backlinks placed strategically between all eight sites.

**The problem:** eight sites under one owner, linking to each other to pass
ranking signal, is a private blog network. Google's spam policies name "link
schemes" explicitly, and cross-site linking between properties you control is
the textbook example. Detection is not hard — shared hosting IP, shared
registrant, shared analytics, near-identical templates, reciprocal footer
links. This portfolio has all five.

The downside is not "it doesn't help". It is a manual action or algorithmic
devaluation applied across the network, including `pattayahomespro.com`,
`secondpassportpro.com` and `moveinthailand.com`, which have existing rankings
to lose.

**What works instead:**

- **Editorial cross-links only, where a reader genuinely benefits.** A Pattaya
  listing page discussing retirement visas can link to the visa site once, in
  the body, because that is where a reader would want it. That is a normal
  link between related businesses.
- **Never site-wide.** Footer or nav links to all seven siblings on every page
  is the pattern that gets caught.
- **Real external links** come from outside your control: property portals
  (DDproperty, Hipflat, FazWaz), expat communities, local press, chambers of
  commerce, developers and suppliers you actually work with, and PR. These are
  slower and they are the ones that hold.
- **Internal linking is unlimited and risk-free.** Within one site you can link
  as aggressively as you like. That is already built: breadcrumbs, related
  properties by area and type, and browse-by chips on every listing page.

## 2. All eight sites ranking on page one for the same keyword

**As asked:** total dominance — every site of yours on a single results page.

**Why it cannot happen:** Google's site diversity update (June 2019) generally
limits a single domain to about two results per page, and treats owned networks
as one entity where it can detect them. A results page showing eight sites with
the same owner is precisely the outcome that update exists to prevent.

Pursuing it also creates a problem you already have. `pattayahomespro.com` and
`pattayahomepro.com` are near-identical names selling the same thing to the
same city. Pointed at the same keywords they do not stack — they split the
signal and compete with each other. That is keyword cannibalisation, and it is
the most likely reason a site plateaus.

**What dominance actually looks like:** each site owns a distinct search intent,
so they never appear in the same auction. Suggested split:

| Site | Owns | Example queries |
| --- | --- | --- |
| pattayahomespro.com | Pattaya **buying** | pattaya condo for sale, buy villa pattaya |
| pattayahomepro.com | Pattaya **renting + commercial** | pattaya condo rental, bar for sale pattaya |
| thaihomespro.com | Thailand **outside** Pattaya | bangkok apartment, chiang mai house |
| secondhomethailand.com | **Second-home** intent | holiday home thailand, second home visa |
| mysecondhomepro.com | **Buying abroad**, advisory | buying property abroad, foreign ownership |
| secondpassportpro.com | **Residency / citizenship** | second passport, golden visa |
| moveinthailand.com | **Relocation** | move to thailand, thailand retirement visa |
| propertiesshare.com | **Fractional ownership** | fractional property, shared holiday home |

Eight sites each ranking first for their own cluster beats eight sites fighting
over one term. It is also the only version that survives contact with the
algorithm.

## 3. The architecture decision that actually matters

The preview is a client-rendered React app in a single file, because an
artifact is one file. **Do not ship that to production.** A client-only React
build sends an empty `<div>` and a script bundle; Google renders JavaScript,
but it queues it, and every property page competes for that render budget.

For a site whose first goal is search, use **Next.js with static generation**:

- Every property page pre-rendered to real HTML at build time.
- Area and type pages generated from the taxonomy, each with its own title,
  meta description and content.
- `next/image` for property photos, which is where the Core Web Vitals score
  is won or lost.
- JSON-LD on every listing page, which is what produces price, bedroom and
  image detail in the results themselves.

The React components in `previews/react/` port to Next.js pages almost
unchanged — the work is the data layer and routing, not the interface.

## 4. What to build, in order

1. **Fix cannibalisation first.** Decide which of the two Pattaya domains owns
   buying and which owns renting, before writing any more content. Everything
   else compounds on this.
2. **One site to Next.js**, with the listing import driving static generation.
3. **JSON-LD** (`RealEstateListing`, `Organization`, `BreadcrumbList`) — the
   highest-return technical work available.
4. **Area and guide pages** — the pages that actually rank for the long tail.
5. **External links**, earned, over months.

Steps 1 to 4 are entirely within your control and carry no risk. Step 5 is the
slow one, and there is no shortcut to it that does not put the portfolio at
risk.
