# Webmoris — Progress Tracker

> Tracks progress against [plan.md](plan.md). Only Claude updates this file, following the rules in [CLAUDE.md](CLAUDE.md).
> Status values:
> - ⬜ Not started
> - 🟡 In progress: work has begun.
> - 🔵 Awaiting approval: the exit criteria are met and it's waiting for the owner to test.
> - ✅ Completed: the owner has tested and approved it.

## Phase Status

| # | Phase | Status | Started | Ready for review | Approved |
|---|---|---|---|---|---|
| 1 | Foundation & Design System | ✅ Completed | 2026-10-31 | 2026-10-31 | 2026-10-31 |
| 2 | Portfolio & Case Studies | ✅ Completed | 2026-10-31 | 2026-10-31 | 2026-10-31 |
| 3 | Services, Ready-made Websites, About & Home | ✅ Completed | 2026-10-31 | 2026-10-31 | 2026-10-31 |
| 4 | Lead Capture | ✅ Completed | 2026-10-31 | 2026-10-31 | 2026-10-31 |
| 5 | Pricing & Payments | ✅ Completed | 2026-10-31 | 2026-10-31 | 2026-10-31 |
| 6 | Motion, 3D, SEO & Launch Readiness | ✅ Completed | 2026-10-31 | 2026-10-31 | 2026-11-01 |
| 7 | First Live Demo: Island Explorer (Tourism) | 🔵 Awaiting approval | 2026-11-01 | 2026-11-01 | — |

## Open Decisions / Blockers
- [ ] Brand assets needed: logo, colours and fonts. Placeholder design tokens are in `frontend/src/css/main.css`.
- [ ] **Before launch (owner):**
  - Test on real devices: Safari on iPhone and Mac, Firefox, Android Chrome.
  - Run Lighthouse on the deployed site (production compression on).
  - Choose hosting and follow `docs/DEPLOY.md`.
  - Choose the analytics provider.
- [ ] Confirm the Webmoris domain and deploy the Island Explorer demo to a subdomain (see Phase 7).
- [ ] PayPal: a REST app (sandbox first), then live credentials, a webhook and a billing plan for each monthly package. Also real package prices and the PayPal USD/EUR prices.
- [ ] Real MCB Juice number/QR and bank details. The demo values say "DEMO".
- [ ] For production: an SMTP account (`EMAIL_URL`), the email address that receives lead notifications, and a Calendly/Cal.com booking link.
- [ ] Real Privacy Policy and Terms text needed, reviewed by a legal professional. The demo pages start with "DEMO TEXT".
- [ ] Real team members, About text, services, templates and prices needed to replace the demo content.
- [ ] Real portfolio projects needed. The 7 demo projects (client names end in "(demo)") should be deleted before launch.
- [ ] Demo values in Site settings need replacing: WhatsApp number, email, phone and stats.
- [x] Own git repository created in `portfolio/` (branch `main`, working branch `phase/1-foundation`).

## Activity Log
<!-- Newest entry first. Format: YYYY-MM-DD — Phase N — event — short note -->
- 2026-11-01 — Phase 7 — Ready for review — The demo is built and tested locally; deploying it needs the owner's domain and hosting.
  - **Built:** `demos/island-explorer/`, a static Eleventy 3 + Tailwind 4 site.
    - **Pages:** Home, Tours (filter), 6 tour pages, About, Contact, Credits and 404.
    - **Data-driven:** add a tour in `tours.json` and its card, page and map pin are generated.
  - **Visual effects:**
    - a WebGL "living lagoon" hero with mouse ripples (skipped on no-GPU renderers, switches itself off below ~30 fps)
    - a Ken Burns zoom and drifting waves
    - cross-page morph view transitions
    - split-text headlines, photo wipe reveals and parallax
    - a pinned sideways featured-tours slider and self-drawing timelines
    - a scrolling destinations ticker, magnetic buttons, a Flip-animated filter, a lightbox and a pulsing map pin
    - all of it respecting reduced motion
  - **Photos:** 27 freely licensed photos of the real places from Wikimedia Commons (CC0, CC BY, CC BY-SA), credited on `/credits/`. No identifiable people, no fake reviews (reviews are a labelled feature preview).
  - **Demo kit improvements:**
    - The kit now loads as the first element in `<body>`, so the bar is in place before first paint (no layout shift).
    - It exposes `--demo-bar-h` for fixed headers.
  - **Verified:**
    - 9/9 UI checks in headless Chrome with no console errors: bar, ripple guard, mobile, filter and deep link, lightbox, booking form blocked, robots.
    - Demo kit 8/8.
    - Core Web Vitals, uncompressed: mobile (4× CPU, Slow 4G) LCP 1.6–2.4 s, CLS ≤ 0.01; desktop LCP ≤ 1.5 s, CLS 0.
  - **Fixed along the way:**
    - Nunjucks async loops rendering cards outside the grid
    - layout shift from the demo bar and from the late headline font
    - unreadable labels on photos
    - an orphan gallery photo
    - an unrealistic island map, now drawn from coastline coordinates
    - the slider pinning under the header
  - **Still to do (owner):** confirm the real Webmoris domain (the demo links to `https://webmoris.mu`, set in `src/_data/site.json`), deploy to a subdomain using `demos/island-explorer/deploy/nginx.conf.example`, then paste the URL into the template's Live demo URL in admin.
  - **How to test:** `cd demos/island-explorer && npm install && npm run build`, then serve `_site/` (e.g. `python -m http.server 5002`) and open it in Chrome.
- 2026-11-01 — Phase 7 planned — Island Explorer tourism demo: a static Eleventy + Tailwind site on a subdomain with free licensed stock photos (see plan.md).
  - Demo support built ahead of it:
    - a "Live demo" badge on template cards that have a demo URL
    - the reusable `demo_kit/`: a "Demo by Webmoris" bar linking to the template's enquiry form, all forms blocked with a friendly notice, a noindex meta tag, a strict-CSP-safe script, and a publishing checklist in its README
  - The kit was tested in headless Chrome under a strict CSP (8/8 checks).
- 2026-11-01 — Post-launch change — In-progress projects, so the portfolio stays honest while the first 2 client projects are under way.
  - **Status field:** projects are Completed or In progress, editable from the admin list (migration `portfolio 0003`).
  - **Pages:** in-progress projects get a violet badge, and their case studies hide results, metrics and the live-site link, with a short note instead. Structured data marks them `Incomplete`.
  - **Home heading:** "Work in progress / What we're building now" until 3 projects are completed, then "Selected work / Projects we're proud of".
  - **Verified:** 225 tests passing, plus screenshots of the two-in-progress scenario.
- 2026-11-01 — Post-launch change — Kreol removed at the owner's request; the site is now English and French only.
  - **Routing:** switched back to Django's built-in language routing, deleting the custom `/kr/` prefix code (`apps/core/i18n.py`, `apps/core/middleware.py`).
  - **Database:** migrations drop every `*_mfe` translation column; existing Kreol leads and orders are moved to French.
  - **Files and docs:** `locale/mfe/` and the Kreol demo text are deleted; tests, README, CLAUDE.md and requirements.md are updated.
  - **Old URLs:** `/kr/` addresses now return 404.
- 2026-11-01 — Post-launch change — Owner requests:
  - **Stats removed:** the stats counters bar is gone from Home and About, along with its Site settings fields (migrations 0006–0007), the count-up animation code and the demo values. requirements.md is updated to match.
  - **Comment fix:** a multi-line `{# #}` comment that was showing on pages is removed, with a test that catches this in future.
- 2026-11-01 — Phase 6 — Completed — Approved by owner; committed on `phase/6-launch-readiness` and merged into `main`. **All 6 phases of plan.md are complete.** Next: the owner's launch items under Open Decisions, then the post-v1 features in plan.md.
- 2026-10-31 — Phase 6 — Ready for review — All code exit criteria met. The remaining items need the owner (see Open Decisions).
  - **Built:**
    - **Three.js hero:** a particle wave in a separate lazy chunk, only on capable devices (WebGL2, at least 768 px wide, motion allowed, no data-saver, enough CPU and memory). It pauses off-screen and when the tab is hidden, with the CSS glow as fallback.
    - **Motion:** magnetic call-to-action buttons and 3D tilt on project cards (mouse devices only).
    - **Accessibility:** focus trapped inside pop-ups.
    - **Performance:** headlines and hero images are no longer hidden while JavaScript loads; the first project cards load eagerly.
    - **SEO:**
      - canonical URLs and `hreflang` (with `x-default`) that ignore query strings
      - a default share image setting
      - `sitemap.xml` with 84 URLs in 3 languages
      - `robots.txt` that never reveals the admin URL
      - JSON-LD: Organization, CreativeWork, Service, Product/Offer
    - **Analytics:** Plausible (cookieless) or GA4 (only after cookie consent), plus conversion events for leads, purchases, WhatsApp clicks and Calendly bookings.
    - **Security:**
      - Django's built-in CSP: per-request nonces, no `unsafe-eval` or `unsafe-inline` for scripts, `frame-ancestors 'none'`.
      - CSP-safe Alpine build, with all template expressions moved into components.
      - `htmx.config.allowEval = false`.
      - Video players built only from allow-listed origins.
      - Self-hosted fonts, so no Google Fonts requests.
    - **Deployment:** `Procfile`, `gunicorn.conf.py`, `passenger_wsgi.py`, `scripts/build.sh`, `deploy/` (Nginx and systemd examples) and `docs/DEPLOY.md` (env vars, 3 hosting options, go-live checklist, backups).
  - **Verified:**
    - 234 tests passing and `ruff` clean.
    - `check --deploy --fail-level WARNING` clean.
    - **Headless Chrome:** 16 interactive UI checks pass with no console errors or CSP violations (menu, HTMX filter, video pop-up, lightbox with focus trap, enquiry dialog, quote form, checkout).
    - **Lighthouse:** Accessibility 100 and SEO 100 on every page tested; Best Practices 81.
      - The 81 comes only from a harmless deprecation notice inside the vendor Alpine CSP build.
      - Lighthouse 12/13 can't record performance traces with the installed Chrome (`NO_NAVSTART`), so I measured Core Web Vitals directly instead.
    - **Core Web Vitals:** mobile (4× CPU, Slow 4G, no compression) LCP 1.5–1.8 s and CLS ≤ 0.04; desktop LCP ≈ 0.9–1.1 s. Production compression cuts the JS from 276 KB to about 95 KB.
    - **Visual QA:** screenshots of desktop and mobile pages in EN/FR/KR. Fixed along the way:
      - section intro text leaking into later sections (regression-tested)
      - a missing-glyph box in placeholder images
      - an orphan template card on Home
  - **How to test:**
    1. Open the Home page on a desktop browser to see the 3D wave, and move the mouse over it.
    2. Hover the "Get a Quote" buttons and the project cards.
    3. Visit `/sitemap.xml` and `/robots.txt`.
    4. Check the `Content-Security-Policy` response header in DevTools → Network.
    5. Read `docs/DEPLOY.md`.
- 2026-10-31 — Phase 6 — Started — branch `phase/6-launch-readiness`.
- 2026-10-31 — Phase 5 — Completed — Approved by owner; committed on `phase/5-pricing-payments` and merged into `main`.
- 2026-10-31 — Phase 5 — Ready for review — Exit criteria met except the live PayPal sandbox run, which needs the owner's PayPal credentials.
  - **Built:** the `pricing` app.
    - **Packages:** MUR price plus an optional USD/EUR PayPal price (PayPal doesn't accept MUR), one-off or monthly, "popular" highlight, and "Request a quote" when a package can't be bought online.
    - **Pages:** `/pricing/` and a Home pricing teaser.
    - **Checkout:** shows only the payment methods that are actually available.
    - **Order page:** reached through an unguessable link, never cached.
    - **PayPal one-off:** server creates and captures the payment, then verifies the reference, amount and currency.
    - **PayPal monthly:** the server checks the subscription with PayPal (status, plan and order reference).
    - **Webhook** at `/payments/paypal/webhook/`: signature verified, each event applied once (de-duplicated), handles capture completed/denied/refunded and subscription activated/cancelled/expired.
    - **MCB Juice and bank:** instructions with the order reference, proof upload (stored privately), then "Payment being verified".
    - **Admin:** "Mark Juice / bank payment as verified" (sends the confirmation), cancel/refund actions, proof preview, webhook log.
    - **Emails:** payment instructions, payment confirmed, and team notifications (new order, proof uploaded, paid).
  - **Security:**
    - Prices are set on the server and tampered fields are ignored (tested).
    - The PayPal order ID comes from our database, never the browser.
    - Atomic "mark paid once" stops duplicate confirmations when the browser and webhook race.
    - Webhooks are verified with PayPal, with no CSRF token needed.
    - Staff cannot mark PayPal orders paid by hand.
  - **Changes from plan:**
    - `PackageFeature` became a one-per-line `features` field, as with services.
    - Packages have a separate PayPal price because PayPal can't charge MUR.
  - **Verified:**
    - 217 tests passing (all PayPal API calls mocked), `ruff` clean.
    - A live Juice checkout on the dev server worked end to end.
    - **Not verified:** a real PayPal sandbox payment. It needs PayPal credentials (see README → Pricing & payments).
  - **How to test:**
    1. Open `/en/pricing/` and click "Buy now" on Business Website.
    2. Pay with MCB Juice, upload a screenshot on the order page, then in admin open Pricing & orders → Orders, select the order and run "Mark Juice / bank payment as verified". The confirmation email prints in the server console.
    3. For PayPal: add sandbox credentials to `.env` and restart the server; a PayPal button appears for packages that have a PayPal price.
- 2026-10-31 — Phase 5 — Started — branch `phase/5-pricing-payments`.
- 2026-10-31 — Phase 4 — Completed — Approved by owner; committed on `phase/4-lead-capture` and merged into `main`.
- 2026-10-31 — Phase 4 — Ready for review — All exit criteria met.
  - **Built:** the `leads` app.
    - **Quote form** (`/contact/`):
      - pre-filled from `?template=`, `?project=`, `?service=` or `?type=` links
      - optional attachment
      - submits through HTMX, with a no-JS fallback
    - **Template enquiry:** opens in a pop-up on the template page, with a full page as no-JS fallback.
    - **Emails:** a team notification (Reply-To set to the visitor) and an auto-reply in the visitor's language.
    - **Calendly/Cal.com:** embedded on the Contact page; only those hosts and https links are accepted.
    - **WhatsApp:** template and project pages pre-fill a message about that item.
    - **Admin:** status pipeline, notes, CSV export, and staff-only attachment downloads.
    - **Links:** every "Get a Quote" link points to the form, pre-filled where it makes sense.
  - **Security:**
    - Honeypot field and per-visitor rate limit. Only a salted hash of the IP is used, kept in the cache.
    - Optional Turnstile check.
    - Attachments are kept in private storage with an extension allow-list and a 10 MB limit.
    - The auto-reply never repeats visitor text, so the form can't be used to relay spam.
    - Header-injection and formula-injection guards.
    - Only same-site pages are recorded as the source page.
    - An email failure never loses a saved lead.
  - **Verified:** 182 tests passing, `ruff` clean, live page checks in EN/FR/KR.
  - **How to test:**
    1. Submit `/en/contact/`. The emails print in the server console.
    2. Submit with a field missing to see the inline errors.
    3. On a ready-made template, click "Customise this website" and send an enquiry.
    4. In admin under Leads, change a status and export to CSV.
    5. Put a real Calendly link and WhatsApp number in Site settings and check the Contact page.
- 2026-10-31 — Phase 4 — Started — branch `phase/4-lead-capture`.
- 2026-10-31 — Phase 3 — Completed — Approved by owner; committed on `phase/3-content-pages` and merged into `main`.
- 2026-10-31 — Phase 3 — Ready for review — All exit criteria met.
  - **Built:**
    - **Services app:** groups, services and FAQs; list and detail pages with benefits, deliverables, related projects, an FAQ accordion and links to other services.
    - **Ready-made websites app:** industries, templates and screenshots; catalog with an HTMX industry filter, status badges and "From MUR …" prices (formatted for each language). The detail page shows features, included pages, gallery, video and demo link.
    - **About page:** story, mission, values, team (initials when there's no photo), process and tools.
    - **Legal pages:** Privacy and Terms, editable in admin.
    - **Home page:** stats that count up, featured projects in a pinned horizontal scroll (swipe on mobile), service groups, featured templates, process and a CTA band. The pricing slot is reserved for Phase 5.
    - **Shared components:** section heading with split-text animation, CTA band, stats, process, filter tabs and icons.
  - **Verified:** 148 tests passing, `ruff` clean, all pages checked live in EN/FR/KR. Admin text is HTML-escaped everywhere (tested).
  - **Demo content:**
    - 6 services, 6 templates, about text and 5 process steps.
    - 3 team members marked "(demo)".
    - Legal pages that start with "DEMO TEXT".
    - Demo templates have no demo URL on purpose.
  - **How to test:**
    1. Scroll the Home page on desktop (the featured projects should slide sideways) and on mobile (swipe).
    2. Open Services and a service page, and expand the FAQs.
    3. On Ready-made Websites, filter by industry and open a template.
    4. Open About and Privacy.
    5. Switch to FR or KR.
    6. In admin, edit About page, Team members, Process steps, Services, Website templates and Legal pages.
- 2026-10-31 — Phase 3 — Started — branch `phase/3-content-pages`; demo content for services, templates, team and legal pages until real content arrives.
- 2026-10-31 — Phase 2 — Completed — Approved by owner; committed on `phase/2-portfolio` and merged into `main`.
- 2026-10-31 — Phase 2 — Ready for review — All exit criteria met.
  - **Built:** the `portfolio` app.
    - **Models:** categories, projects, result metrics and screenshots (Desktop or Mobile), all translatable.
    - **Admin:** image previews, inline metrics and screenshots, editable order, published and featured flags.
    - **Images:** WebP renditions generated with imagekit.
    - **Portfolio grid** (`/portfolio/`):
      - category tabs that filter through HTMX, with a full-page fallback without JS and bookmarkable `?category=` links
      - "Load more" pagination
      - hover overlay with View Case Study, Live Site and Video buttons, plus a video pop-up
    - **Case study page:** hero, details, metrics, Challenge/Solution/Results, tech tags, screenshot tabs with a lightbox (arrow keys and Esc work), video, a quote call-to-action, previous/next links and related projects.
    - **Seed data:** 7 demo projects with generated images.
  - **Security:**
    - Uploads get random names and type/size limits; SVG and executables are rejected.
    - Only YouTube (privacy-enhanced mode) and Vimeo can be embedded.
  - **Changes from plan:** result metrics are a separate translatable model rather than a JSON field, so each label can be translated.
  - **Verified:** 111 tests passing, `ruff` clean, live check of all pages, HTMX partials and WebP images.
  - **How to test:**
    1. Open `/en/portfolio/` and click the category tabs. The grid changes without a page reload, and the URL updates.
    2. Hover a card and open a case study.
    3. Click a screenshot, then use ← → and Esc.
    4. Switch to FR or KR.
    5. In admin, under Portfolio → Projects:
       - add a YouTube link to a project and check the Video button and pop-up
       - unpublish a project and check it disappears
       - upload your own cover image
- 2026-10-31 — Phase 2 — Started — branch `phase/2-portfolio`; building with demo projects until real ones are provided.
- 2026-10-31 — Phase 1 — Completed — Approved by owner; committed on `phase/1-foundation` and merged into `main`.
- 2026-10-31 — Phase 1 — Ready for review — All exit criteria met.
  - **Built:**
    - Django 6.1.2 project with split settings, environment variables and WhiteNoise.
    - EN/FR/KR pages with the URLs `/en/`, `/fr/` and `/kr/`. Kreol uses the `mfe` code, with a draft translation.
    - The `SiteSettings` singleton in admin, editable per language.
    - Tailwind v4 + esbuild pipeline with the dark design tokens, Lenis smooth scrolling and GSAP scroll reveals, which switch off under reduced motion.
    - Glass sticky header with a mobile menu and language switcher, plus the footer, announcement bar, WhatsApp button, and 404/500 pages.
    - Placeholder routes for all list pages, the `seed_demo` command, and the README.
  - **Verified:**
    - 69 tests passing, `ruff` clean.
    - `check --deploy` clean with production settings.
    - Live smoke test passed.
  - **How to test:** follow the README "Setup" and "Run locally" steps, then:
    1. Open `/`. It should redirect to `/en/`.
    2. Switch EN/FR/KR in the header.
    3. In admin at `/manage-webmoris/`, edit Site settings (announcement bar, WhatsApp number, contact email) and check the footer and WhatsApp button update.
    4. Turn on "reduce motion" in your OS and check the page still shows everything without animation.
    5. Shrink the window to test the mobile menu.
- 2026-10-31 — Phase 1 — Started — git repo initialized; building the Django skeleton, i18n, and frontend pipeline.
- 2026-10-31 — Setup — Planning done — requirements.md, plan.md and CLAUDE.md created; Phase 1 not started yet.
