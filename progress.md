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
| 7 | First Live Demo: Island Explorer (Tourism) | ✅ Completed | 2026-11-01 | 2026-11-01 | 2026-11-02 |
| 8 | Second Live Demo: Lagon Bistro (Restaurant / Beach Bar) | ✅ Completed | 2026-11-01 | 2026-11-01 | 2026-11-02 |
| 9 | Third Live Demo: Drive Moris (Car Rental) | ✅ Completed | 2026-11-01 | 2026-11-01 | 2026-11-02 |
| 10 | Fourth Live Demo: Villa Select (Real Estate) | ✅ Completed | 2026-11-02 | 2026-11-02 | 2026-11-02 |
| 11 | Fifth Live Demo: Eco Lodge (Villa / Guesthouse) | ✅ Completed | 2026-11-02 | 2026-11-02 | 2026-11-02 |
| 12 | Sixth Live Demo: Street Food Co. (Food Truck / Takeaway) | ✅ Completed | 2026-11-02 | 2026-11-02 | 2026-11-02 |
| 13 | Project Brief, Quote-First Pricing and Deposits | ✅ Completed | 2026-11-05 | 2026-11-06 | 2026-11-07 |
| 14 | Services Page Redesign | ✅ Completed | 2026-11-07 | 2026-11-07 | 2026-11-09 |
| 15 | Demo Conversion Tour ("See why it converts") | 🟡 In progress | 2026-11-09 | — | — |

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
- 2026-11-09 — Phase 15 — Started — "See why it converts" mode on the 6 demos (owner approved the mock-up): floating "Get this website" badge and mini card, x-ray tour with hotspots and notes per demo, page blueprint, sticky mobile action bar and scroll nudge. Front end only (no admin, no tracking). Branch `phase/15-demo-tour`.
- 2026-11-09 — Phase 14 — Approved by owner — merged into `main` and pushed.
- 2026-11-09 — Phase 14 — Additions requested by owner before approval — Interactive home hero (owner approved the mock-up): generic headline and "Start my website" button; optional "See what we could build for you" business types (new `HeroBusiness` model in admin: label, features, package, ready-made demo, brief project type) showing typical features and the "From" price; demo preview in a browser window that tilts with the pointer, rotates through the demos until one is picked, and has floating feature tags. Works without JS (?business=…) and with reduced motion. Also: package cards list rounds of changes; team photos cropped from the top. Test: open `/en/` and `/fr/`, pick a business type, then click "Start my website".
- 2026-11-07 — Phase 14 — Ready for review — Services page redesigned (branch `phase/14-services-page`).
  - **Layout:** hero with "Get a Quote" and "See pricing"; one numbered section per service (01–09): group, title and summary on the left; description and "what you get" points on the right ("Label: text" lines show the label in bold); then 3 packages and the call-to-action band. Original wording, no copy from other agencies.
  - **New services** (owner's choice): Hosting & Email (Web Development), Branding & Print and Photo & Video (new "Brand & Content" group), with new icons. All 9 services have their own description, points and benefits in English and French (seed + local DB). Hosting copy makes no uptime guarantee.
  - Home "What we do" now shows 3 groups ("Websites, marketing and content, under one roof."). Service links pre-select the right project type in the brief (new types: Branding & print, Photo & video).
  - **How to test:** `/en/services/` and `/fr/services/` (desktop and phone), the new detail pages, "Get a Quote" on a service page. Edit points in admin → Services ("What you get", one per line). 249 tests pass; ruff clean.
- 2026-11-07 — Phase 14 — Started — Services page redesign (numbered service sections, packages, call to action), adding Hosting & Email, Branding & Print, and Photo & Video (owner's choice). Branch `phase/14-services-page`.
- 2026-11-07 — Phase 13 — Approved by owner — merged into `main` and pushed.
- 2026-11-06 — Phase 13 — Ready for review (update) — "From" prices at Mauritian market level and a founding client offer, after the owner reviewed `docs/pricing-draft.txt` (prices compared with 8 local agencies).
  - **Prices** (seed + local DB): Starter from MUR 12,000, Business from MUR 30,000, Online Store or Booking from MUR 60,000, Care Plan from MUR 1,200 / month. Still quote-first: buttons open the brief, no online checkout.
  - **Launch offer** (Site settings → "Launch offer", EN/FR, on/off): "Founding client offer: 20% off your website" for the first 5 clients, Care Plan first 2 months free with the price locked, in exchange for a testimonial and a case study. Shown above the packages on Pricing and Home.
  - Starter features match the draft (1–3 pages, 1 round of changes; Google setup is an extra). Step 3 now says the rest is paid in stages; footnote says prices are in MUR.
  - Also fixed broken French accents in the Odyssey Mauritius project text (local DB).
  - **How to test:** `/en/pricing/` and `/fr/pricing/`, Home packages section; turn the offer off in admin → Site settings and check it disappears. 242 tests pass; ruff clean.
- 2026-11-05 — Phase 13 — Ready for review — Quote-first pricing built (branch `phase/13-project-brief-and-deposits`).
  - **Project brief** (Contact page): 6 steps with progress, Back/Next and per-step checks; one normal form without JS. Captures project type, package, business, current site, pages, features, a demo to start from, inspiration, budget, timeline and contact. Package and demo pre-fill from links.
  - **Packages:** Starter Website, Business Website (Recommended), Online Store or Booking Site, Care Plan (monthly). No prices by default (optional "From" price in admin); buttons open the brief. AI marketing packages removed from Pricing (still on Services).
  - **Payment requests:** created in admin, one click from a quote request (client details and "50% deposit — …" pre-filled); private pay page; client picks PayPal / Juice / bank and pays through the existing order flow; amount set by staff on the server; "Email the payment link" admin action.
  - **Wording:** Pricing ("Tell us about your project. Get a tailored quote.", 3 steps), Home section, Contact page; English and French.
  - **Checks:** 240 tests pass (new tests for the brief and payment requests), ruff clean, migrations leads 0003 and pricing 0003.
  - **How to test:** /en/pricing/ → "Start your project" → fill the brief; in admin open the quote request → "Create a payment request" → save → "Email the payment link" or open the payment page.
- 2026-11-02 — Phase 12 — Approved — The owner approved Street Food Co. Merged into `main` and pushed. All six ready-made templates now have live demos (local ports 5002–5007); next is deployment to subdomains once the domain and hosting are confirmed.
- 2026-11-02 — Phase 12 — Ready for review — Street Food Co. demo built and tested locally (http://127.0.0.1:5007). All six ready-made cards now have live demos.
  - **Built:** `demos/street-food-co/`: Home, Menu, Order, Credits, 404. Fictional food truck; 13 dishes in 4 categories; weekly schedule across the island; 17 Wikimedia Commons photos, all credited.
  - **Conversion:** "Order ahead, skip the queue" everywhere; one-tap "Add" with a basket that follows you to the order page, −/+ steppers and a live total; "Today we're at…" in the hero; mobile order bar.
  - **Look:** sunshine yellow, pink, lime and ink; Lilita One + DM Sans; sticker-style cards and buttons with hard shadows; wiggling and spinning stickers, marquee, word-by-word headings.
  - **Checks:** 15/15 demo QA checks, no console errors. Mobile (throttled) LCP 1.5–2.1 s uncompressed, 1.1–1.6 s with gzip; CLS ≤ 0.02.
  - **Webmoris:** Street Food Co. card changed from "Coming soon" to "Available" (from MUR 20,000) with real screenshots; local Live demo URL http://127.0.0.1:5007/. Tests pass, ruff clean.
- 2026-11-02 — Phase 12 — Started — The owner wants six demos; building Street Food Co. (food truck / takeaway) for the last "Coming soon" card. Branch `phase/12-street-food-demo` from `main`.
- 2026-11-02 — Phases 7–11 — Approved — The owner approved all five live demos (Island Explorer, Lagon Bistro, Drive Moris, Villa Select, Eco Lodge). Merged into `main` and pushed. Still to do before they bring in enquiries: confirm the domain and hosting, deploy each demo to its subdomain, and switch the Live demo URLs in Webmoris admin from the local addresses.
- 2026-11-02 — Phase 11 — Ready for review — Eco Lodge demo built and tested locally (http://127.0.0.1:5006).
  - **Built:** `demos/eco-lodge/`: Home, Rooms, 5 room pages, Book, Credits, 404. Fictional lodge in the Chamarel hills; 19 Wikimedia Commons photos, all credited.
  - **Conversion:** "book direct and save" throughout: booking-site price crossed out next to the direct price, perks (10% off, breakfast, late check-out, free transfer from 3 nights), availability calendar per room, live summary showing the saving, mobile action bar.
  - **Look and motion:** forest green, terracotta and honey, Gloock + Outfit; hero camera dolly, dolly reveal of the Chamarel falls, word-by-word headings, counters, scroll zoom.
  - **Checks:** 22/22 demo QA checks, no console errors. Mobile (throttled) LCP 1.6–2.7 s uncompressed, 1.6 s for the home page with gzip; CLS 0.
  - **Webmoris:** Eco Lodge card changed from "Coming soon" to "Available" (from MUR 35,000) with real screenshots; local Live demo URL http://127.0.0.1:5006/. Tests pass, ruff clean.
- 2026-11-02 — Phase 11 — Started — Eco Lodge (nature lodge / guesthouse) demo, the second demo the owner picked. Built on branch `phase/11-eco-lodge-demo` (from Phase 10, still awaiting approval).
- 2026-11-02 — Phase 10 — Ready for review — Villa Select real estate demo built and tested locally (http://127.0.0.1:5005).
  - **Built:** `demos/villa-select/`: Home, Properties (filters), 9 property pages, Contact, Credits, 404. Fictional agency, 9 example listings across 5 real areas of Mauritius (prices in USD), 39 Wikimedia Commons photos, all credited.
  - **Look and motion:** deep emerald, champagne gold and coral, DM Serif Display + Manrope; hero camera dolly, pinned dolly reveal, word-by-word headings, price pins on the real Mauritius map, counting stats, places marquee, scroll zoom, magnetic buttons.
  - **Conversion:** hero search (area, type, budget), "Book a viewing" everywhere, sticky viewing request on property pages, monthly payment estimate, free 48-hour shortlist offer, mobile action bar.
  - **Checks:** 22/22 demo QA checks, no console errors. Mobile (throttled, uncompressed) LCP 1.7–2.7 s, CLS ≤ 0.02. Webmoris tests pass, ruff clean; the Villa Select card has real screenshots (local Live demo URL http://127.0.0.1:5005/).
- 2026-11-02 — Phase 10 — Started — The owner asked for more demo sites and chose Villa Select (real estate) then Eco Lodge (villa / guesthouse). Built on branch `phase/10-real-estate-demo` (from Phase 9, still awaiting approval).
- 2026-11-01 — Phase 9 — Ready for review (colour + VFX) — Richer colour and cinematic motion added to the Bright island design.
  - **Colour:** deeper lagoon blues, turquoise and a coral-to-sun gradient on buttons and accent words; dark lagoon bands for How it works, stats and page headers.
  - **Effects:** full-bleed hero with camera dolly in/out and mouse parallax (Belle Mare lagoon aerial), pinned dolly reveal of the lagoon photo, word-by-word headings, counting stats, destinations marquee, scroll zoom on trip photos, drawn step line, magnetic buttons, card lift on hover.
  - **Conversion:** hero search card with "from Rs 1,400/day", a mobile "Book now" bar on every page except Book.
  - **Checks:** 21/21 demo QA checks, no console errors; mobile (throttled) LCP 1.5–2.4 s uncompressed, CLS 0. Webmoris card screenshots refreshed.
- 2026-11-01 — Phase 9 — Changes requested — The owner wants richer colour and more visual effects (GSAP, zoom, dolly in/out) so the demo is more appealing and converts better. Keeping the Bright island structure.
- 2026-11-01 — Phase 9 — Ready for review (redesign) — Drive Moris rebuilt in the owner's chosen "Bright island" direction (http://127.0.0.1:5004).
  - **Look:** light backgrounds, lagoon blue with a coral accent for main actions, Plus Jakarta Sans in sentence case, full-colour photos with rounded corners. The dark duotone grade, WebGL night drive, road-sign type, garage stage and turntable were removed.
  - **Structure:** Home = search in the hero (dates + car), benefits, popular car cards (photo, seats, bags, gearbox, price, Book), how it works in 3 steps, coast route on the map (kept, restyled), day trips, FAQ accordion, call to action. Car pages have a sticky summary card; Book has 4 numbered steps and a live price summary.
  - **Checks:** 22/22 demo QA checks, no console errors. Mobile (throttled) LCP 1.3–1.9 s, CLS 0. Webmoris tests pass, ruff clean. Webmoris card screenshots refreshed.
- 2026-11-01 — Phase 9 — Changes requested — The owner doesn't like the layout, colour and structure; wants it more intuitive, professional and appealing. Redesign in progress.
- 2026-11-01 — Phase 9 — Ready for review — Drive Moris car rental demo built to the "Coast Road" creative direction and tested locally (http://127.0.0.1:5004).
  - **Built:** `demos/drive-moris/`: Home (KM 00–80), Fleet with filter, 8 car pages, Book (live trip ticket), Credits, 404. Content in `site.json`, `fleet.json`, `drives.json`; 24 Wikimedia Commons photos, all credited and graded with one duotone at build time.
  - **Effects:** shader night-drive hero (GPU desktops only, static SVG road elsewhere), pinned coast route drawn on the real OpenStreetMap map with an odometer, garage stage, drag-to-turn car view, odometer prices, sign and film reveals, lane-line progress bar, page-change "truck pass".
  - **Demo kit:** now lets a same-site GET form marked `data-demo-navigation` through (the home page quote bar); all other forms are still blocked (rechecked on Island Explorer and Lagon Bistro).
  - **Checks:** 23/23 demo QA checks, no console errors. Mobile (throttled) LCP 1.4–1.9 s uncompressed, CLS ≤ 0.04. Webmoris tests pass, ruff clean.
  - **Webmoris:** the Drive Moris card shows real screenshots; locally its Live demo URL is http://127.0.0.1:5004/.
  - **How to test:** open http://127.0.0.1:5004/, move the mouse over the hero and scroll slowly through the coast section; use the quote bar; on Book change dates, car and extras; drag the car on a car page (e.g. Suzuki Swift).
- 2026-11-01 — Phase 9 — Started — The owner approved the "Coast Road" creative direction and asked to start. Built on branch `phase/9-car-rental-demo` (from Phase 8, still awaiting approval).
- 2026-11-01 — Phase 8 — Ready for review — Lagon Bistro restaurant demo built and tested locally (http://127.0.0.1:5003).
  - **Built:** `demos/lagon-bistro/` (Eleventy + Tailwind, same setup as Island Explorer): Home, Menu, Book a table, Credits, 404. Content in `site.json` and `menu.json` (26 dishes, 5 sections); 31 Wikimedia Commons photos, all credited.
  - **Effects:** WebGL sunset hero (sea glitter, swaying palms, mouse ripples and glow; GPU only, fps watchdog), pinned noon-to-night scene with a running clock, pinned cocktail reel that takes each drink's colour, cursor-follow dish photos, scroll-velocity marquee, 3D tilt cards, split text, custom cursor, film grain. Reduced motion and no-JS both show all content.
  - **Checks:** 12/12 demo QA checks, no console errors. Mobile (throttled) LCP 2.0–2.6 s uncompressed, 2.1 s with gzip; CLS ≤ 0.04. Webmoris: 227 tests pass, ruff clean.
  - **Webmoris:** the Lagon Bistro ready-made card uses real screenshots (`apps/readymade/demo_screens/lagon-bistro/`); locally its Live demo URL is http://127.0.0.1:5003/.
  - **How to test:** open http://127.0.0.1:5003/ and scroll slowly through the home page; try the menu filter and hover dish names; submit the booking form (blocked); open the ready-made page on Webmoris.
  - **Open:** the template's "Pages included" list in admin still shows the generic seed pages; set it to Home, Menu, Book a table.
- 2026-11-01 — Phase 8 — Started — The owner asked for a restaurant / beach bar demo, as eye-catching as possible with GSAP and visual effects. Built on branch `phase/8-restaurant-demo` (from Phase 7, which is still awaiting approval).
- 2026-11-01 — Phase 7 — Real map of Mauritius + click-to-load Google Map — The owner asked for a more professional first map at the right locations.
  - **Base map:** generated from OpenStreetMap data (`npm run build:map`): the real coastline and islets, lagoon reefs, reservoirs, national parks, the airport, and the motorway and main roads. "© OpenStreetMap" is credited on the map and the Credits page.
  - **Locations:** every tour and meeting point was checked against OpenStreetMap. Corrections: the Île aux Cerfs boats leave from the Trou d'Eau Douce ferry jetty; Tamarin Beach was moved to the actual beach; the Le Morne hike now meets at the trailhead car park.
  - **Google Maps:** the "Interactive map" button swaps in the live Google Map at the exact spot, and "Back to overview" returns. Nothing loads from Google before the click. Without JS, the button opens Google Maps in a new tab. Needs `frame-src https://www.google.com` in the CSP (added to the nginx example).
  - Demo QA passes 9/9, the demo kit 3/3, no console errors.
- 2026-11-01 — Phase 7 — Meeting point map redesigned — On tour pages, the map is now a professional map card instead of the plain island outline.
  - **Map:** a light chart-style map with the lagoon, reef and depth contours, the national park, the motorway and town labels, a compass and a 10 km scale bar.
  - **Markers:** placed from real coordinates. The meeting point has a coral pin and label; the other tours are small dots that link to their pages. Town labels hide when they would collide with the pin.
  - **Details panel:** meeting time, hotel pick-up (or how to get there), the tour area, and "Google Maps" / "Directions" links that open in a new tab.
  - **Data:** `tours.json` now has `lat`/`lng`, `meet` and `pickup` instead of `mapX`/`mapY`/`meetingPoint`. Demo QA passes 9/9, the demo kit 3/3, no console errors.
- 2026-11-01 — Phase 7 — Demo listed on Webmoris — The Island Explorer ready-made card now uses real screenshots of the demo.
  - Screenshots are stored in `apps/readymade/demo_screens/island-explorer/`: a cover plus 4 gallery images (desktop + phone, moods, tour listing, tour page). `seed_demo` uses them; templates without a built demo keep their placeholders.
  - Locally, the template's Live demo URL is `http://127.0.0.1:5002/`. After deploying, change it in admin to the real subdomain.
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
