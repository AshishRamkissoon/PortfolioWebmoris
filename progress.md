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
| 5 | Pricing & Payments | 🟡 In progress | 2026-10-31 | — | — |
| 6 | Motion, 3D, SEO & Launch Readiness | ⬜ Not started | — | — | — |

## Open Decisions / Blockers
- [ ] Kreol URL prefix: proceeding with `/kr/` (plan default). Owner to confirm; easy to change later in one setting.
- [ ] Kreol UI translations are a draft; they need review by a native speaker (Phase 6).
- [ ] Brand assets needed: logo, colours and fonts. Placeholder design tokens are in `frontend/src/css/main.css`.
- [ ] For production: an SMTP account (`EMAIL_URL`), the email address that receives lead notifications, and a Calendly/Cal.com booking link.
- [ ] Real Privacy Policy and Terms text needed, reviewed by a legal professional. The demo pages start with "DEMO TEXT".
- [ ] Real team members, About text, services, templates and prices needed to replace the demo content.
- [ ] Real portfolio projects needed. The 7 demo projects (client names end in "(demo)") should be deleted before launch.
- [ ] Demo values in Site settings need replacing: WhatsApp number, email, phone and stats.
- [x] Own git repository created in `portfolio/` (branch `main`, working branch `phase/1-foundation`).

## Activity Log
<!-- Newest entry first. Format: YYYY-MM-DD — Phase N — event — short note -->
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
