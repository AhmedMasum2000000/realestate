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

## Motion and the home story

The home page opens with a pinned, scroll-scrubbed story (coast, temple, city, home) drawn on a canvas from WebP frames, with one GSAP master timeline driving the frames, headline exits, taglines and the closing visa/home panels. Other motion: the glass header hides on scroll down and returns on scroll up; sections enter as they scroll into view; the route comparison bars fill; the statement resolves letter by letter; the stats count up; the closing call to action has a slow ambient glow.

- `tools/mit_story.py` renders `mit/media/move-in-thailand-story.mp4` (and a vertical cut) from four repository photographs and extracts 24 fps WebP frames at quality 85 into `mit/assets/frames/`. With a filmed brand video: `python tools/mit_story.py --video brand.mp4`. Needs ffmpeg.
- GSAP 3.15.0, ScrollTrigger and SplitText (GSAP standard licence, free for commercial use) and Lenis 1.3.26 (MIT) are self-hosted in `mit/assets/vendor/`; `mit/assets/motion.js` holds all motion code.
- Craft layer: Lenis smooth scrolling for mouse and trackpad only (touch keeps native scrolling); headline lines rise from masks; photos wipe in and drift with a slow parallax; a burgundy line draws through the home process steps; a topic marquee follows scroll speed and direction; the footer wordmark rises in and lifts under the pointer; guides show a reading-progress line; a trailing cursor ring becomes a labelled disc over clickable cards; buttons are magnetic with a navy fill; cards tilt slightly; menu labels roll on hover; pages cross-fade with the header held still where the browser supports view transitions; fine film grain sits over the dark sections.
- Story layer: key messages are wrapped in `<mark class="hl">` (`hl-dark` on dark backgrounds). The hero's core message (`data-hl-load`) is painted on arrival; every other mark is painted as it scrolls into view and unpainted when you scroll back, so the eye follows one promise to the next. Paint progress is the registered CSS property `--hl`; without scripts every mark shows fully painted. `data-rotator` cycles words (hero reason, closing call to action); `data-tick` counts the hero numbers; wide screens get a chapter rail on the home page. The menu button folds into a close mark, FAQ answers slide in, buttons ripple and spring on press.
- Always on: the page keeps moving while left alone: a ticking Pattaya clock (seconds), rotating words, drifting points of light and a breathing scene in the hero, a sheen on "Thailand.", a falling scroll cue, gleams across painted highlights and primary buttons, light running through the comparison bars, drifting brand-tinted shapes behind sections, counter-turning rings, floating icons and chips, typewriter notes, the marquee and a slow wave through the footer wordmark (paused off-screen). Entrances, headline lines, photo wipes, counters and the scrambled statement replay each time they come back into view.
- Reduced motion: visitors whose device asks for less motion get a gentle mode (`motion-lite`): no movement across the screen, but highlights still paint, words cross-fade, numbers count, the clock ticks and notes type.
- `tools/mit_live_check.py` (workflow "Move In Thailand live check") confirms on desktop, an iPhone profile and a reduced-motion visitor that the page keeps changing while idle, alongside the story, header and layout checks.
- Copy rules: persuasive but checkable. Time and effort claims refer to the tools as built (Visa Finder: 4 questions, no contact details). No testimonials, client counts, response times or guarantees are invented.
- Pointer effects run only for a mouse or trackpad, and the system cursor is never hidden. Above-the-fold headlines and photos carry a CSS failsafe that shows them after 2.6 seconds even if a script never runs.
- Phones load every second frame and slow or data-saving connections every fourth; the player blends between loaded frames. Frame 1 doubles as the poster, so the first paint does not wait for the sequence.
- With reduced motion, or if the scripts fail, the hero is a static photograph with the same copy and the closing panels sit below it. Nothing starts hidden that the script has not taken responsibility for showing.
- Another agency's watermark on the villa photograph (CP3302) is cropped out in `tools/mit_story.py`; do not reuse the uncropped image.

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
