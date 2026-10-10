# Move In Thailand website

Thirty editorial pages built around the visitor's visa question, with the original navy/burgundy brand, existing cPanel media, practical planning tools and a private WordPress enquiry desk.

## Content and editing

The production website is served by `wp-content/mu-plugins/mit-experience.php`. On first load it creates native WordPress page records under **Move In Thailand Pages**. Each page has an HTML content block, drafts, revisions, a preview link and editable search title/description. Existing WordPress editor permissions govern page editing. Only administrators can open **Move Enquiries** or change delivery settings. GitHub copy updates apply automatically while a page still matches its previous default; staff edits are preserved and flagged for review when a newer default exists.

The existing theme, original pages, uploads, accounts and unrelated plugins remain in place. New website navigation and footer are maintained in `mit/templates/base.html.j2`.

In **Settings → Move In Thailand**, an administrator can enter a verified public WhatsApp number, confirmed service fee labels and a notification inbox. Blank prices display **Written quote**. Blank WhatsApp hides the messaging link. The existing WordPress administrative inbox is the notification fallback; enquiries are still saved if a notification fails. No staff names, addresses, accreditation, success rates or testimonials were invented.

## Tools

- Visa Finder: purpose, age, work/family/study context and evidence planning; a starting shortlist with reasons and conditions, not an eligibility decision.
- Move budget: editable example inputs, monthly buffer, arrival costs and a downloadable estimate. Examples are not live market prices.
- Property ownership checklist: transaction-specific questions and official sources.
- Branded moving checklist PDF: no email gate.
- Enquiry form: persisted records, request deduplication, required enquiry consent, separate optional marketing consent, signed form bootstrap, limits and spam trap. Follow-up states and notes stay in WordPress. Initial records move to recoverable Trash after 180 days, except active service or a documented legal hold. WordPress's own Trash policy controls later deletion.

## Sources and media

`mit/content.py` keeps the official visa/ownership sources next to the editorial copy. The source check date is 8 October 2026. A factual review is needed when rules change; nobody is represented as having provided a lawyer's sign-off.

`mit/asset-provenance.json` records the media URLs and original file hashes. Branding and the beach photograph came from the Move In Thailand cPanel installation. Property photographs were verified in the same cPanel account's existing property partner installation before downloading their public bytes. Local fonts came from the existing repository. No new stock people are used as clients or staff.

## Local build

```powershell
python -m pip install -r mit/requirements.txt
python mit/build.py --preview --output .cache/mit-preview
python -m http.server 8765 --bind 127.0.0.1 --directory .cache/mit-preview
```

Production: `python mit/build.py`. The compiler checks all generated internal destinations. Assets are self-hosted; this release adds no analytics or advertising trackers.

## Deployment and restore

`.github/workflows/mit-website.yml` publishes changes on `codex/move-in-thailand-rebuild` using the existing cPanel secrets. It compiles the site, checks JavaScript/PHP syntax, stages the entire release outside the public website and switches only the two named website additions. Prior editorial files are retained in `~/mit-deployments/<release>/`. A failed public release check restores the previous editorial files.

To restore the original WordPress front end, rename `wp-content/mu-plugins/mit-experience.php` to `mit-experience.php.disabled` in cPanel. Content drafts and enquiries remain stored. Re-enable by restoring the `.php` filename. Existing WordPress, backup and access settings are not changed.

New pages appear in `/mit-sitemap.xml`, included in the existing All in One SEO sitemap index. Modification dates follow the published WordPress copy. The normal WordPress robots hook also advertises the sitemap when WordPress serves that response. The old `/about-2/`, `/contact-2/` and `/services-2/` paths redirect to their rebuilt equivalents. Other existing URLs continue through WordPress.

This release implements the website foundation. Ads, newsletters, social publishing, new translations, third-party CRM integrations, verified reviews and operational legal review are separate phases of the business plan.
