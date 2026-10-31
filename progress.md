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
| 3 | Services, Ready-made Websites, About & Home | ⬜ Not started | — | — | — |
| 4 | Lead Capture | ⬜ Not started | — | — | — |
| 5 | Pricing & Payments | ⬜ Not started | — | — | — |
| 6 | Motion, 3D, SEO & Launch Readiness | ⬜ Not started | — | — | — |

## Open Decisions / Blockers
- [ ] Kreol URL prefix: proceeding with `/kr/` (plan default). Owner to confirm; easy to change later in one setting.
- [ ] Kreol UI translations are a draft; they need review by a native speaker (Phase 6).
- [ ] Brand assets needed: logo, colours and fonts. Placeholder design tokens are in `frontend/src/css/main.css`.
- [ ] Real portfolio projects needed. The 7 demo projects (client names end in "(demo)") should be deleted before launch.
- [ ] Demo values in Site settings need replacing: WhatsApp number, email, phone and stats.
- [x] Own git repository created in `portfolio/` (branch `main`, working branch `phase/1-foundation`).

## Activity Log
<!-- Newest entry first. Format: YYYY-MM-DD — Phase N — event — short note -->
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
