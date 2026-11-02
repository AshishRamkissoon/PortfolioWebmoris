# Webmoris — Development Plan

> Based on [requirements.md](requirements.md) (captured 2026-10-31).
> 6 phases. Each phase ends with something working that can be demoed, plus tests, so it can be built, reviewed and merged on its own.
> Branch convention: `phase/<n>-<name>` → merge into `main` when the phase's exit criteria pass.

---

## Overview

| # | Phase | Main outcome | Depends on |
|---|---|---|---|
| 1 | Foundation & Design System | Django project, 3-language setup, Tailwind/GSAP build, base layout, site settings | — |
| 2 | Portfolio & Case Studies | Filterable project grid and case-study pages, managed in admin | 1 |
| 3 | Services, Ready-made Websites, About & Home | All content pages, plus a Home page that uses them | 2 |
| 4 | Lead Capture | Quote form, template inquiry, WhatsApp, Calendly, emails, leads pipeline in admin | 3 |
| 5 | Pricing & Payments | Service packages with PayPal (one-off + monthly) and the manual MCB Juice flow | 4 |
| 6 | Motion, 3D, SEO & Launch Readiness | Three.js hero, full GSAP polish, SEO, performance, security, translations, deploy docs | 1–5 |

---

## Key Technical Decisions (fixed up front)

- **Django 5.2 LTS or 6.x** (whichever is the latest stable at kickoff), Python 3.12+.
- **Project layout**
  ```
  config/            settings/{base,dev,prod}.py, urls.py, wsgi.py, asgi.py
  apps/core/         SiteSettings, TeamMember, static pages (about, legal), context processors, seed command
  apps/portfolio/    Project, ProjectCategory, ProjectImage
  apps/readymade/    WebsiteTemplate, TemplateIndustry, TemplateImage
  apps/services/     ServiceGroup, Service, ServiceFAQ
  apps/leads/        QuoteRequest, TemplateInquiry
  apps/pricing/      Package, PackageFeature, Order, PayPal integration
  templates/         base.html, partials/, components/
  frontend/          src/css (Tailwind), src/js (modules) → built into static/dist/
  locale/            en, fr, mfe
  ```
- **Frontend build**: npm with **Tailwind CSS** and **esbuild**, which bundle GSAP, ScrollTrigger, Lenis, Alpine.js, HTMX and Three.js. Three.js is loaded on demand as a separate chunk. The built files are collected by WhiteNoise.
- **Translations**: `django-modeltranslation` for model fields, and `gettext` for the text in templates.
  - Kreol uses the language code `mfe`, with the URL prefix **`/kr/`** and the switcher label "KR".
  - **Mismatch to resolve:** requirements §3 says `/cr/` while §9 says `/kr/` or `/mfe/`. This plan uses `/kr/`. Confirm before starting Phase 1.
- **Images**: `django-imagekit` generates WebP thumbnails/renditions.
- **Config**: `django-environ` with a `.env` file, and `.env.example` committed to the repo.
- **Testing**: `pytest-django` plus `factory_boy`. Each phase adds model, view and form tests. Payments use mocked PayPal responses.
- **Code quality**: `ruff` (lint + format) and `pre-commit`.

---

## Phase 1 — Foundation & Design System

**Goal:** a working skeleton. Every later phase only adds apps and pages on top of it.

### Tasks
1. **Repo & tooling**
   - `git init` inside `portfolio/`. The folder currently sits inside an unrelated parent repo, so it needs its own.
   - Add `.gitignore`, `pre-commit`, `ruff` and `pytest` configuration.
   - Create `requirements/{base,dev,prod}.txt` (or `pyproject.toml`).
2. **Django project**
   - Set up `config/` with split settings (`base` / `dev` / `prod`) and `django-environ`.
   - SQLite in dev, and `DATABASE_URL` for PostgreSQL in prod.
   - WhiteNoise, media settings, and a custom admin URL taken from an environment variable (`ADMIN_URL`).
3. **Multilingual setup**
   - `LANGUAGES = [en, fr, mfe]`. Register custom `LANG_INFO` for `mfe`, falling back to `fr`.
   - `LocaleMiddleware` plus `i18n_patterns` with the `/kr/` prefix mapped to `mfe`.
   - Install `django-modeltranslation`.
   - Build a language switcher that keeps the visitor on the equivalent page.
4. **Core app**
   - `SiteSettings` singleton holding the stats values, WhatsApp number, Calendly URL, contact details, social links, announcement bar, SEO defaults, and the Juice/bank details (filled in Phase 5).
   - A context processor that exposes these settings to every template.
5. **Frontend pipeline**
   - Set up `package.json` with Tailwind and esbuild, plus `npm run dev` (watch) and `npm run build` scripts.
   - **Design tokens**: dark palette, neon/gradient accents, a display font and a body font, spacing, and radii. Placeholder values are used until brand assets arrive.
   - Base JS modules:
     - Lenis smooth scroll.
     - A GSAP reveal utility (`data-reveal` attribute).
     - Alpine.js and HTMX.
     - A `prefers-reduced-motion` guard.
6. **Base layout & global components**
   - `base.html`: SEO meta block, OG tags block, and hreflang placeholder.
   - **Header**: sticky glassmorphism style, nav links, language switcher, CTA button, and an animated mobile menu.
   - **Footer** and the **announcement bar**, which can be turned on and off in admin.
   - **Floating WhatsApp button**, with a pre-filled message per language.
   - Custom 404 and 500 pages.
   - Placeholder routes for every sitemap URL.
7. **Seed command**: `python manage.py seed_demo` creates the `SiteSettings` record. Later phases extend it with their own demo data.
8. **Docs**: README covering setup, running the dev server and frontend watch, and building assets.

### Exit criteria
- `runserver` shows a styled dark layout with header and footer at `/en/`, `/fr/` and `/kr/`, and the language switcher works.
- `SiteSettings` can be edited in admin, and the changes appear in the footer and the WhatsApp button.
- `npm run build` produces minified CSS and JS. GSAP reveal works and turns off under reduced motion.
- The test suite runs green: settings, i18n URLs, context processor.

---

## Phase 2 — Portfolio & Case Studies

**Goal:** the main trust-building feature: real work, shown well.

### Tasks
1. **Models**: `ProjectCategory`, `Project` and `ProjectImage`, per requirements §8.
   - Translatable fields are registered with modeltranslation.
   - `metrics` is a JSON list of `{label, value}` pairs, e.g. "+120% traffic".
   - `is_featured`, `order` and `is_published` flags.
2. **Admin**
   - Inline gallery for screenshots (desktop/mobile type, drag-or-number ordering) with image previews.
   - Prepopulated slugs, list filters, and a list-editable `order` column.
3. **Image pipeline**: imagekit renditions (card thumbnail, gallery, hero) in WebP, with lazy loading and `srcset`.
4. **Portfolio grid (`/portfolio/`)**
   - Category filter tabs; HTMX swaps the grid without a full reload, and the URL updates (`?category=`) so filters can be bookmarked.
   - GSAP Flip or stagger transition when the filter changes.
   - Project cards: thumbnail, title, client, tags, and one-line description.
     - Hover reveal/zoom, plus an overlay with **View Case Study**, **Live Site** and **Video** buttons.
   - **Video modal** (Alpine.js) that plays a YouTube/Vimeo embed or an uploaded MP4.
   - "Load more" pagination using HTMX.
5. **Case study page (`/portfolio/<slug>/`)**
   - Hero image and meta details: client, industry, year, services, tech stack tags.
   - Challenge / Solution / Results sections, with animated metric highlights.
   - Screenshot gallery with a desktop/mobile toggle and a lightbox (e.g. GLightbox or a small Alpine component).
   - Video section and **Live site** button.
   - Previous/next project navigation, related projects (same category), and a CTA to the quote form (a placeholder link until Phase 4).
6. **Seed data**: 6–8 demo projects with placeholder images across all categories, in EN (with FR/KR stub translations).

### Exit criteria
- Admin can create a project with a gallery and video. It appears in the grid, filters correctly, and the case study page shows every section.
- Unpublished projects stay hidden. Featured projects can be queried for use on Home.
- The grid works without JS, falling back to full page reloads when filtering.
- Tests cover models, filtered listing, the detail page, 404 for unpublished projects, and the HTMX partial responses.

---

## Phase 3 — Services, Ready-made Websites, About & Home

**Goal:** all the content pages are complete, and the Home page brings them together.

### Tasks
1. **Services app**
   - Models: `ServiceGroup` (Web Development, AI Marketing), `Service` and `ServiceFAQ`.
   - `/services/` overview grouped by service group.
   - `/services/<slug>/` detail pages: benefits, deliverables, related projects (M2M to `Project`), an accordion FAQ, and a CTA.
   - Seed data covers the Web Development services plus **AI Content & Social Media** and **AI Chatbots**.
2. **Ready-made websites app**
   - Models: `TemplateIndustry`, `WebsiteTemplate` and `TemplateImage`.
   - `/ready-made-websites/` catalog: cards in the style of the reference site, an "Available" / "Coming soon" badge, a "Starting from" price, and an HTMX industry filter (reusing the Phase 2 component).
   - Detail page: features, page list, screenshots, **Live demo** button, and optional video.
     - The **Inquire / Customize** button is a placeholder until Phase 4.
3. **About page**
   - `TeamMember` model and admin.
   - `/about/` sections: agency story, mission and values, team grid, process steps, a tech logo strip, and stats counters.
4. **Reusable components**: stats counter (animated count-up on scroll), process timeline, CTA band, and section heading with split-text reveal.
5. **Home page**
   - **Hero**: headline, both CTAs, and a **static or CSS-gradient placeholder** where the Three.js visual will go in Phase 6.
   - Stats counters.
   - Featured projects, shown as a GSAP horizontal-scroll slider on desktop and a swipeable stack on mobile.
   - Services teaser and ready-made websites teaser (3–6 templates).
   - Process section.
   - **Pricing teaser**: the slot is reserved and hidden until Phase 5.
   - Final CTA band.
6. **Legal pages**: `/privacy/` and `/terms/` as admin-editable flat pages (or a simple `Page` model).

### Exit criteria
- Every page in the sitemap except checkout renders real or seed content in all 3 languages.
- All content on these pages can be edited in admin.
- Home shows featured projects and templates driven by admin flags.
- Responsive at mobile, tablet and desktop widths. Basic keyboard navigation works.
- Tests cover listing and detail views for services and templates, home context, and the about page.

---

## Phase 4 — Lead Capture

**Goal:** turn visitors into leads that the owner can track.

### Tasks
1. **Models**
   - `QuoteRequest`: contact info, project type, budget range, timeline, message, attachment, language, source page, status, and internal notes.
   - `TemplateInquiry`: a link to the template, contact info, business name, message, language, and status.
   - Shared lead status choices: New, Contacted, Quoted, Won, Lost.
2. **Quote form (`/contact/`)**
   - Django form with server-side validation, submitted via HTMX with inline errors and a success state.
   - The project type can be pre-filled from a query string (e.g. from a case study or service CTA).
   - File attachments are validated for type (pdf/doc/images/zip) and size (e.g. ≤ 10 MB).
3. **Template inquiry**: an Alpine modal on the template detail page, with the form pre-filled with the template name.
   - Wire up the Phase 3 placeholder buttons.
4. **Spam protection**
   - Honeypot field and `django-ratelimit` on the form endpoints.
   - Optional Cloudflare Turnstile, enabled through an environment variable.
5. **Emails**
   - The admin gets a notification with the lead details and a link to it in admin.
   - The client gets an auto-reply **in their chosen language**.
   - Templates are HTML plus plain text, and the SMTP backend is configured through environment variables (dev uses the console backend).
6. **Calendly**: an embed on `/contact/` and a "Book a call" CTA, using the URL from `SiteSettings`.
7. **WhatsApp**: refine the pre-filled messages per page context (e.g. "I'm interested in <template>").
8. **Admin pipeline**
   - Lead list view with status filters, date hierarchy, and inline editing of status and notes.
   - A **CSV export** action.
9. **Wire up all CTAs** across the site (case studies, services, Home CTA band) so they point to the contact or inquiry flows.

### Exit criteria
- Submitting the quote form and a template inquiry saves a record, sends both emails (visible in the console backend), and shows a success message in the visitor's language.
- Spam and rate limits block repeated or bot submissions. Invalid files are rejected.
- Admin can filter leads by status, update them, and export CSV.
- Tests cover form validation, honeypot, rate limit, email sending (via `mail.outbox`), the CSV export and attachment validation.

---

## Phase 5 — Pricing & Payments

**Goal:** service packages can be bought online with PayPal or MCB Juice.

### Tasks
1. **Models**
   - `Package`: name, slug, price, currency (MUR, optionally EUR/USD), billing type (one-off/monthly), features, `is_popular`, `is_purchasable`, `paypal_plan_id`, and order.
   - `PackageFeature`.
   - `Order`: package, customer details, amount, currency, payment method, status (Pending / Pending verification / Paid / Failed / Cancelled / Refunded), transaction reference, proof-of-payment file, and timestamps.
2. **Pricing page (`/pricing/`)**
   - Package cards with a "popular" highlight and a one-off/monthly toggle or grouping.
   - Packages that aren't purchasable show **Request a quote**, linking to the Phase 4 form with the package pre-filled.
   - Enable the Home pricing teaser.
3. **Checkout (`/pricing/<slug>/checkout/`)**
   - A customer details form creates the `Order` (status Pending), then the visitor picks a payment method.
   - **PayPal one-off**:
     - The PayPal JS SDK buttons call server endpoints: create order → capture order.
     - Amount and currency always come from the server, never from the client.
   - **PayPal monthly**: PayPal Subscriptions using `paypal_plan_id`, which can be created manually in PayPal or via a management command.
   - **PayPal webhooks**: verify the signature, then update the order status for capture, subscription activated/cancelled and refunds. The handler is idempotent.
   - **MCB Juice / bank transfer**:
     - Show the Juice number/QR and bank details from `SiteSettings`, plus the order reference.
     - The customer uploads proof of payment or enters a transaction reference, and the order moves to **Pending verification**.
4. **Admin**
   - Order list with status filters.
   - A **"Mark as paid (verified)"** action for Juice/bank orders, which triggers the confirmation email.
   - A proof-of-payment preview.
5. **Emails**
   - Order received / payment confirmed / payment failed for the client, in their language.
   - New order and Juice proof uploaded notifications for the admin.
6. **Success, cancel and pending pages**, with a short order summary.
7. **Configuration**
   - PayPal client ID, secret, mode (sandbox/live) and webhook ID come from environment variables.
   - Document the sandbox test accounts in the README.

### Exit criteria
- In PayPal **sandbox**, a one-off purchase and a monthly subscription both complete, and the order shows Paid in admin with the transaction reference.
- The webhook updates status correctly, and fake or unsigned webhook requests are rejected.
- The Juice flow works end to end: order → proof upload → admin marks it paid → client gets the email.
- The price cannot be tampered with from the client.
- Tests cover order creation, mocked PayPal create/capture, webhook verification and idempotency, Juice upload validation, and the admin action.

---

## Phase 6 — Motion, 3D, SEO & Launch Readiness

**Goal:** the "wow" layer and production quality.

### Tasks
1. **Three.js hero**
   - An interactive 3D visual: particles, abstract shapes, or a globe hinting at Mauritius and global reach.
   - Loaded lazily as its own chunk, and started only on capable devices (checks on `deviceMemory`, `hardwareConcurrency`, viewport size and reduced motion).
   - Static image/CSS fallback on mobile and low-power devices. Rendering pauses when the hero is off-screen.
2. **GSAP polish pass**
   - Split-text headings and page transitions.
   - Card tilt on hover, magnetic CTA buttons, and refined horizontal scroll.
   - Optional snap scroll on the Home hero sections.
   - Tune performance (`will-change`, cleaning up ScrollTriggers between pages).
3. **Accessibility audit (WCAG 2.1 AA)**: contrast on the dark theme, focus states, keyboard traps in modals, alt text, ARIA on tabs and accordions, and a skip link.
4. **SEO**
   - Per-object SEO title and meta (translatable) with fallbacks from `SiteSettings`.
   - OG/Twitter cards, canonical URLs and `hreflang` alternates.
   - `django.contrib.sitemaps` with all languages, plus `robots.txt`.
   - JSON-LD structured data: Organization/LocalBusiness, CreativeWork (projects), Service, and Product/Offer (packages).
5. **Performance**
   - Hit the Lighthouse targets: ≥ 90 on desktop and ≥ 80 on mobile.
   - Preload critical fonts, use responsive images everywhere, defer non-critical JS, and cache headers via WhiteNoise.
6. **Analytics & consent**
   - GA4 or Plausible, chosen through an environment variable.
   - Conversion events for quote submits, template inquiries, WhatsApp clicks, Calendly bookings and purchases.
   - Cookie consent banner, shown only when the analytics provider needs one.
7. **Security hardening**
   - `prod` settings: HTTPS redirect, HSTS, secure cookies, CSP header (`django-csp`) that allows GSAP/PayPal/Calendly/YouTube.
   - Admin on a custom URL, with optional 2FA (`django-otp`).
   - `manage.py check --deploy` passes cleanly.
8. **Translations**
   - Run `makemessages` and complete the FR and Kreol `.po` files (UI strings).
   - Fill the FR/KR fields for all seed and real content, and review emails and WhatsApp messages in each language.
9. **Real content load**: swap the placeholders for the owner's logo, brand colours, projects, team, prices and contact details (see requirements §10).
10. **Deployment readiness** (hosting still undecided)
    - `.env.example`, Gunicorn config, and a `Procfile` for PaaS.
    - Sample Nginx and systemd configs for a VPS.
    - Notes for cPanel Passenger (`passenger_wsgi.py`).
    - A production build script: `npm run build` → `collectstatic` → `migrate`.
    - PostgreSQL backup notes.
11. **Final QA**
    - Cross-browser (Chrome, Safari, Firefox, Edge) and real-device mobile testing.
    - Go through the full v1 acceptance checklist (requirements §12).

### Exit criteria
- Every checkbox in requirements §12 is ticked.
- Lighthouse targets are met on Home, Portfolio and a case study page, on both mobile and desktop.
- `check --deploy` is clean, the test suite is green, and the site is ready to deploy on whichever host is picked.

---

## Cross-Phase Practices
- **Definition of done for every phase**:
  - Migrations are committed.
  - Admin is configured for the new models.
  - Seed data is extended.
  - New UI strings are wrapped for translation.
  - Tests are added and green, and `ruff` is clean.
  - README is updated.
- **Design consistency**: new UI reuses the Phase 1 tokens and components; no one-off styles.
- **Progressive enhancement**: core content and forms work without JS. HTMX, Alpine, GSAP and Three.js are layered on top.
- **Content requests**: at the start of each phase, ask the owner for that phase's real content (projects for Phase 2, services, templates and team for Phase 3, prices and Juice details for Phase 5) so it can replace the seed data as early as possible.

---

## Phase 7 — First Live Demo: "Island Explorer" (Tourism)

**Goal:** a polished, clickable demo of the "Island Explorer" ready-made website. Visitors can try it before enquiring, which proves Webmoris's quality while the portfolio is still small.

**Decisions** (owner, 2026-11-01):
- **Industry:** tourism and excursions.
- **What it is:** a demo only, not the product handed to clients. It's a lightweight static site.
- **Hosting:** a subdomain of the Webmoris domain.
- **Photos:** free licensed stock (Unsplash / Pexels).

### Tech
- **[Eleventy (11ty)](https://www.11ty.dev/) + Tailwind CSS**, generating plain HTML. Tours live in one `tours.json` file, and every page is built from it, so adding a tour means adding one entry.
- **JavaScript:** small vanilla JS only (mobile menu, gallery, tour filter), with no framework.
- **Demo kit:** `demo_kit/demo-kit.js` on every page. It adds the "Demo by Webmoris" bar, blocks all forms, and adds `noindex`.
- **Location in the repo:** `demos/island-explorer/`. The build output (`_site/`) is deployed as static files.
- **Language:** English first. French can follow once the demo brings in enquiries.

### Fictional brand and content
- **Brand:** "Island Explorer" (Mauritius tours). The name, team, phone (`+230 5000 0000`) and email (`hello@example.com`) are all invented.
- **6 tours** across 3 categories:
  - **Sea:** catamaran to Île aux Cerfs, dolphin swim at Tamarin Bay.
  - **Land:** Chamarel and Black River Gorges, Le Morne hike.
  - **Culture:** Port Louis market and street food, south coast and tea route.
- **Each tour:** duration, price per person (MUR), group size, what's included, itinerary, meeting point, and 4–6 photos.
- **Banned:** no fake reviews, ratings, guest counts or "best in Mauritius" claims. The reviews area is a clearly labelled *feature preview* ("Your Google reviews appear here").

### Pages
1. **Home:**
   - hero with a search-style "Find a tour" bar
   - featured tours
   - why book with us: safety, small groups, hotel pick-up
   - how booking works in 3 steps
   - FAQ, a reviews feature preview, and a call to action
2. **Tours:** a grid filtered by category and duration, with a price "from".
3. **Tour detail:** gallery, key facts, itinerary timeline, what's included and excluded, and a meeting point (static map image, no third-party embed). Ends with a **booking request form**: date, guests, hotel, name, email. The demo kit blocks it.
4. **About:** fictional story, guides (illustrations or no faces), and safety commitments.
5. **Contact:** a form (blocked) and a WhatsApp button that opens the *Webmoris* enquiry link, not a fake number.

### Steps
1. **Setup:** Eleventy, Tailwind and the demo kit; base layout, header and footer; deploy script.
2. **Content:** write the tour copy, pick the photos, record each photo's source and licence in `CREDITS.md`, and optimise them (WebP, responsive sizes).
3. **Pages:** build all 5 pages mobile-first, with accessible forms and the gallery.
4. **QA:**
   - Lighthouse (mobile ≥ 90), real phone check, no console errors
   - every form blocked, `noindex` and `X-Robots-Tag` in place
   - go through the demo-kit checklist
5. **Deploy and link:**
   - Nginx server block for the subdomain (e.g. `tours.demo.<domain>`) with the `X-Robots-Tag` header.
   - Paste the URL into the template's **Live demo URL** in Webmoris admin, which turns on the "Live demo" badge and button.
   - Update the template's features and pages list to match the demo.

### Exit criteria
- The demo is live on the subdomain, with all 5 pages on mobile and desktop.
- No form can send data; the demo bar links to the Island Explorer enquiry form on Webmoris.
- Search engines are blocked by both the header and `robots.txt`.
- `CREDITS.md` covers every image, and the content has no real people, businesses or fake social proof.
- On Webmoris, the Island Explorer template shows the "Live demo" badge and opens the demo in a new tab.

---

## Phase 8 — Second Live Demo: "Lagon Bistro" (Restaurant / Beach Bar)

**Goal:** a demo of the "Lagon Bistro" ready-made website that is as eye-catching as possible, so restaurant owners want one. Builds on Phase 7's setup (Eleventy, Tailwind, demo kit, photo pipeline).

**Decisions** (owner, 2026-11-01):
- **Industry:** restaurant / beach bar, the largest small-business market in Mauritius.
- **Style:** GSAP and visual effects front and centre.
- Same rules as Phase 7: static site, subdomain, licensed photos with credits, demo kit on every page.

### Fictional brand and content
- **Brand:** "Lagon Bistro", a beach kitchen and bar on the west coast (Flic en Flac), known for sunsets. Phone and email are invented.
- **Menu:** about 24 dishes in 5 sections (street-food starters, grill, Creole curries, desserts, cocktails), each with a price in MUR and dietary tags.
- **Opening times:** lunch, sunset happy hour, dinner.
- **Banned:** no fake reviews, ratings, awards or "best in Mauritius" claims.

### Pages
1. **Home:** a WebGL sunset hero, the story, signature dishes, a day-to-night section, cocktails, a gallery, events, the location map and a reservation call to action.
2. **Menu:** the full menu with section filters, dietary tags and photo previews.
3. **Reserve:** a booking form (blocked by the demo kit), opening hours and a WhatsApp button that leads to the Webmoris enquiry form.
4. **Credits** and **404**.

### Visual effects
- WebGL hero with a shimmering sunset sea and a mouse-driven ripple (skipped on weak devices).
- Kinetic split-text headlines, a rotating "open daily" badge and a scroll-velocity marquee.
- Menu items that reveal a floating photo following the cursor on desktop.
- A pinned "day to night" section where the sky changes from lunch to sunset to night as you scroll.
- A pinned cocktail carousel whose background takes each drink's colour.
- Clip-path photo reveals, parallax, magnetic buttons, a custom cursor on desktop and subtle film grain.
- Everything respects `prefers-reduced-motion` and works without JavaScript.

### Exit criteria
- All pages work on mobile and desktop with no console errors; forms are blocked by the demo kit.
- Mobile LCP ≤ 2.5 s and CLS ≤ 0.1 locally; effects switch off for reduced motion.
- Every photo is credited; no real people's reviews or fake social proof.
- On Webmoris, the Lagon Bistro template shows real screenshots and the "Live demo" button (local URL until deployed).

---

## Phase 9 — Third Live Demo: "Drive Moris" (Car Rental)

**Goal:** a car rental demo following [docs/drive-moris-creative-direction.md](docs/drive-moris-creative-direction.md). After review the owner chose the light "Bright island" direction over the first dark "Coast Road" build. It replaces the placeholder on the Drive Moris ready-made card.

**Decisions** (owner, 2026-11-01): build the creative direction as written; same stack and rules as Phases 7–8 (static site, subdomain, licensed photos with credits, demo kit, no fake social proof).

### Pages
Home (search, benefits, popular cars, how it works, coast route on the map, day trips, FAQ, call to action), Our cars (filter), one page per car, Book a car (4 steps with a live price summary), Credits, 404.

### Exit criteria
- All pages work on mobile and desktop with no console errors; forms are blocked by the demo kit.
- Every page is complete without JavaScript and with reduced motion.
- Mobile LCP ≤ 2.5 s and CLS ≤ 0.1 locally.
- Every photo is credited; no reviews, ratings or real company names.
- On Webmoris, the Drive Moris template shows real screenshots and the "Live demo" button (local URL until deployed).

---

## Future Phases (post-v1, from requirements §11)
- AI chatbot on the Webmoris site (lead capture).
- Testimonials, client logo strip and Google reviews. **Recommended first**, because they help most with trust.
- Blog/resources and newsletter.
- Before/after slider on case studies.
- Stripe card payments, online checkout for ready-made websites, and a client portal.
