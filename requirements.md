# Webmoris — Agency Portfolio Website: Requirements

> Status: Requirements captured on 2026-10-31. Source of truth for the development plan.
> Owner: Ashish Ramkissoon (Webmoris)

---

## 1. Project Overview

**Webmoris** is a web development and AI marketing agency based in Mauritius. It needs its own website that:

1. **Showcases past work** (portfolio and case studies) so prospective clients gain trust and confidence.
2. **Presents services**: website development and AI marketing.
3. **Sells ready-made websites** through an inquiry-based catalog.
4. **Generates leads** through a quote form, WhatsApp and calendar booking.
5. **Sells fixed-price service packages** online (PayPal and MCB Juice).

### 1.1 Goals
- Build credibility through real projects, live links, screenshots, videos, results and stats.
- Show technical skill through the website itself: dark, bold design with GSAP scroll animations and Three.js 3D effects.
- Turn visitors into leads (quote requests, bookings, WhatsApp chats, package purchases).
- Let the owner manage all content through Django admin, with no code changes needed to add projects, templates, services or prices.

### 1.2 Target audience
- Small and medium businesses in Mauritius (EN, FR and Kreol speakers) and international clients.
- Businesses needing a new website, a redesign, or AI-powered marketing.

---

## 2. Reference Website Analysis

**Reference:** https://nicolaipalmkvist.com/#full

**What it is:** a template marketplace ("Nicolai's Template Club") selling Elementor templates. It is built with **WordPress + Elementor + GSAP/ScrollTrigger**. It is a store, not an agency portfolio.

### 2.1 Elements to ADOPT
| Reference element | Webmoris adaptation |
|---|---|
| Collection anchors / category tabs (All, Full Site, Hero Sections, GSAP…) | **Filterable project grid** (e.g. All, Business Websites, E-commerce, Landing Pages, AI Marketing) |
| Template cards: thumbnail, title, one-line description, *Live demo* / *Video* / *Import* buttons | **Project cards**: thumbnail, title, short description, category, *View Case Study* / *Live Site* / *Video* buttons |
| Template catalog with "Free" / "Coming soon" statuses | **Ready-made Websites catalog**: template cards with live demo, "starting from" price, status (*Available* / *Coming soon*), and an *Inquire* button |
| GSAP effects: snap scroll, ScrollTrigger reveals, horizontal scroll sliders, hover effects, rotating sliders, glassmorphism menu | Used across the site for a "wow" effect that shows agency skill |
| Hero social proof ("Join 1,400+ users") | **Animated stats counters** (projects delivered, years of experience, happy clients, etc.) |
| Announcement top bar (promo) | Optional, admin-toggleable **announcement bar** (e.g. promotion on a package) |

### 2.2 Elements NOT adopted
- Membership / "Template Club" subscription and sign-in area.
- Downloadable template imports.
- Newsletter signup (not selected for v1).
- WordPress/Elementor stack (Webmoris uses Django).

### 2.3 Gaps the reference doesn't cover (added for Webmoris)
- Case study detail pages.
- Services + pricing pages.
- About + team + process.
- Quote request form, WhatsApp button, calendar booking.
- Multilingual support (EN/FR/Kreol).
- Online payment for service packages.

---

## 3. Sitemap

```
/                         Home
/portfolio/               Portfolio grid (filterable)
/portfolio/<slug>/        Case study detail
/ready-made-websites/     Ready-made website catalog (inquiry only)
/ready-made-websites/<slug>/  Template detail + inquiry form
/services/                Services overview (Web Dev + AI Marketing)
/services/<slug>/         Service detail
/pricing/                 Service packages (purchasable online)
/pricing/<slug>/checkout/ Package checkout (PayPal / MCB Juice)
/about/                   About, team, process
/contact/                 Quote request form + calendar booking + WhatsApp
/privacy/ /terms/         Legal pages
```
All public URLs are prefixed by language: `/en/`, `/fr/`, `/cr/` (Kreol; see §9).

---

## 4. Functional Requirements

### 4.1 Home page
- **Hero**: bold headline and sub-headline, primary CTA (*Get a Quote*), secondary CTA (*View Our Work*), and a **Three.js 3D background/visual** with a static fallback on low-end devices.
- **Animated stats counters**: e.g. projects delivered, years in business, clients served, countries. Values are editable in admin and count up on scroll.
- **Featured projects**: a curated selection from the portfolio, shown as a GSAP horizontal-scroll slider or grid.
- **Services teaser**: Web Development and AI Marketing cards linking to the service pages.
- **Ready-made websites teaser**: 3–6 featured templates.
- **Process section**: steps such as Discover, Design, Develop, Launch, Grow, animated on scroll.
- **Pricing teaser**: highlighted packages.
- **Final CTA band**: quote / book a call / WhatsApp.

### 4.2 Portfolio (filterable project grid)
- Grid of project cards: thumbnail, title, client name, category tag(s), one-line description.
- **Category filter tabs** (e.g. All / Business / E-commerce / Landing Page / AI Marketing). Categories are managed in admin.
- Filtering without a full page reload (Alpine.js or HTMX), with GSAP transitions when filtering.
- Hover effects on cards (image zoom/reveal, overlay with buttons).
- Card buttons: **View Case Study**, **Live Site** (if a URL exists), **Video** (if a video exists, opens a modal).
- Projects can be marked **featured** (shown on Home) and **ordered** manually.
- Pagination or "Load more" once there are many projects.

### 4.3 Case study detail page
- Hero image, title, client, industry, year, services provided, tech stack tags.
- Sections: **The Challenge**, **The Solution**, **The Results** (with optional metric highlights, e.g. "+120% traffic").
- **Screenshot gallery**: desktop and mobile screenshots, with a lightbox.
- **Video walkthrough**: YouTube/Vimeo embed or uploaded MP4.
- **Live site link** button.
- Previous/next project navigation, plus related projects.
- CTA: "Want a website like this? Get a quote."

### 4.4 Ready-made websites (inquiry only — no online purchase)
- Catalog grid styled like the reference's template cards: thumbnail, name, industry (e.g. restaurant, tourism, car rental, real estate), short description, **"Starting from" price**, status badge (*Available* / *Coming soon*).
- Filter by industry/category.
- Detail page: description, included features list, page list, screenshots, **Live demo** link (demo hosted on a subdomain), optional video.
- **Inquire / Customize this website** button that opens an inquiry form pre-filled with the template name: name, email, phone/WhatsApp, business name, message, preferred language.
- Model: **done-for-you**. Webmoris customizes the template for the client after the inquiry; there is no checkout for templates.
- Inquiries are saved in the DB, sent to the admin by email, and appear in Django admin with a status (New / Contacted / Quoted / Won / Lost).

### 4.5 Services
- Two service groups:
  - **Web Development**: business websites, e-commerce, landing pages, redesigns, maintenance/hosting (final list editable in admin).
  - **AI Marketing**:
    - **AI Content & Social Media**: AI-generated posts, captions, images and video for social media.
    - **AI Chatbots**: website and WhatsApp chatbots for client businesses.
- Each service has a detail page: description, benefits, deliverables, related projects, FAQ, and CTA.

### 4.6 Pricing / Service packages (purchasable online)
- Package cards: name, price (MUR and optionally EUR/USD), billing type (**one-off** or **monthly**), features list, "popular" highlight.
- Examples (final content to be provided): Starter Website, Business Website, AI Social Media Monthly, AI Chatbot Setup.
- **Buy** button leads to a checkout page:
  - **PayPal** (PayPal Checkout / Orders API; PayPal Subscriptions for monthly packages).
  - **MCB Juice / local payment**: shows the Juice number/QR code and bank transfer details. The client uploads proof of payment or enters a reference. The order stays *Pending verification* until an admin confirms it manually.
- An **Order** record stores customer details, package, amount, currency, payment method, status (Pending / Paid / Failed / Cancelled / Refunded) and transaction reference.
- Confirmation emails go to the client and the admin.
- Packages that need a discussion can show **"Request a quote"** instead of **Buy**.

### 4.7 About
- Agency story, mission and values, and a Mauritius base.
- **Team members**: photo, name, role, short bio, social links (managed in admin).
- Process/methodology and tools/tech used (logo strip of technologies).
- Stats counters (reused component).

### 4.8 Contact & lead capture
- **Quote request form**: name, email, phone/WhatsApp, company, **project type** (website / e-commerce / AI marketing / ready-made template / other), **budget range**, **timeline**, message, optional file attachment, preferred language.
  - Saved to the DB (Lead model with status pipeline) and emailed to the admin, with an auto-reply to the client.
  - Spam protection: honeypot plus rate limiting (optionally reCAPTCHA/Turnstile).
- **Floating WhatsApp button** on all pages (click-to-chat with a pre-filled message per page/language). The number is configurable in admin/settings.
- **Calendar booking**: embedded Calendly (or Cal.com) for discovery calls. The URL is configurable in admin.
- Contact details: email, phone, address/map (optional), and social links.

### 4.9 Global elements
- **Header**: logo, nav (Portfolio, Ready-made Sites, Services, Pricing, About, Contact), language switcher (EN/FR/KR), CTA button. Glassmorphism sticky menu inspired by the reference, and an animated mobile menu.
- **Footer**: short about text, quick links, services, contact info, social links, legal links, copyright.
- **Announcement bar** (optional, admin-toggleable).
- Custom 404/500 pages in the site style.
- Cookie consent banner (if analytics are used).

---

## 5. Admin / Content Management (Django admin)
All content is manageable without code:
- **Portfolio**: Project, ProjectCategory, ProjectImage (gallery, desktop/mobile type, order), video URL/file, results metrics, featured flag, order, publish status.
- **Ready-made Websites**: Template, TemplateCategory/Industry, images, features, starting price, demo URL, status.
- **Services**: ServiceGroup, Service, FAQ items.
- **Pricing**: Package, PackageFeature, Order (with payment status and manual verification for Juice).
- **Team**: TeamMember.
- **Leads**: QuoteRequest / TemplateInquiry with status pipeline, notes, CSV export.
- **Site settings** (singleton): stats counter values, WhatsApp number, Calendly URL, contact email/phone, social links, announcement bar text/toggle, SEO defaults, Juice number/QR, bank details.
- All translatable fields are editable per language (EN/FR/KR).
- Image uploads automatically generate optimized sizes/WebP.

---

## 6. Design & UX Requirements
- **Style: dark, bold, animated.** Dark background, large bold typography, neon/gradient accents, and a techy AI feel. Final palette and fonts to be decided; brand assets are partially available.
- **Animations (GSAP + ScrollTrigger)**:
  - Section reveal on scroll (fade/slide/split-text headings).
  - Horizontal scroll slider for featured projects.
  - Card hover effects (image reveal/zoom, tilt).
  - Animated counters.
  - Smooth scrolling (e.g. Lenis), page transition effects, filter transitions.
  - Optional snap scroll on the home hero sections.
- **Three.js**: interactive 3D hero visual (e.g. particles, abstract shapes, or a globe hinting at the Mauritius/global reach).
  - Must be lazy-loaded and performance-guarded, with a static image/CSS fallback on mobile/low-power devices.
- Respect `prefers-reduced-motion` (disable heavy animations).
- Fully **responsive** (mobile-first), with touch-friendly sliders.
- Accessibility: semantic HTML, sufficient contrast on the dark theme, keyboard navigation, alt text, focus states (WCAG 2.1 AA target).

---

## 7. Technical Requirements

### 7.1 Stack
- **Backend**: Python 3.12+, **Django** (latest stable, 5.x/6.x), PostgreSQL (SQLite allowed in local dev).
- **Frontend**: Django templates + **Tailwind CSS**, **GSAP + ScrollTrigger**, **Three.js**, Alpine.js and/or HTMX for interactivity (filters, modals, forms).
- **Translations**: Django i18n (`gettext`) for static strings plus **django-modeltranslation** (or django-parler) for model content.
- **Media**: Pillow, with image optimization/thumbnails (e.g. django-imagekit or sorl-thumbnail) and WebP output.
- **Payments**: PayPal REST SDK / Checkout JS (Orders + Subscriptions). MCB Juice handled as manual verification.
- **Email**: SMTP provider (e.g. Brevo, Mailgun, or Gmail SMTP) via Django email backend.
- **Static files**: WhiteNoise. Media is stored locally, with an optional S3-compatible storage later.

### 7.2 Hosting & deployment
- Hosting **not decided yet**, so the project must be **deployment-agnostic**:
  - Settings split (`base` / `dev` / `prod`) with environment variables (`django-environ` / `.env`).
  - PostgreSQL-ready, WhiteNoise for static files, Gunicorn-ready.
  - Works on a VPS (Nginx + Gunicorn), a PaaS (Render/Railway), or a cPanel Passenger setup.
- HTTPS enforced in production, with secure cookies and HSTS.

### 7.3 SEO & performance
- Per-page SEO title/meta description (translatable), Open Graph/Twitter cards, canonical URLs.
- `hreflang` tags for EN/FR/KR, `sitemap.xml`, `robots.txt`.
- Schema.org structured data (Organization, LocalBusiness, CreativeWork for projects, Product/Offer for packages).
- Performance target: Lighthouse ≥ 90 performance on desktop and ≥ 80 on mobile despite the animations. Lazy-load images, video and Three.js, and defer non-critical JS.
- Analytics: Google Analytics 4 or Plausible (configurable). Conversion events for form submits, WhatsApp clicks, bookings and purchases.

### 7.4 Security
- CSRF protection, form validation, file upload type/size limits.
- Rate limiting on forms, plus honeypot/captcha.
- PayPal webhook signature verification. Payment status is never trusted from the client side.
- Admin at a non-default URL, with strong passwords (optional 2FA).

---

## 8. Data Model (initial outline)
- `Project` (title, slug, client, industry, year, category M2M, short_description, challenge, solution, results, metrics JSON, tech_stack, live_url, video_url/video_file, cover_image, is_featured, order, is_published, SEO fields)
- `ProjectCategory` (name, slug, order)
- `ProjectImage` (project FK, image, type desktop/mobile, caption, order)
- `WebsiteTemplate` (name, slug, industry FK, description, features, pages, starting_price, currency, demo_url, video_url, cover_image, status, is_featured, order)
- `TemplateImage`, `TemplateIndustry`
- `ServiceGroup`, `Service` (group FK, title, slug, icon, summary, body, deliverables), `ServiceFAQ`
- `Package` (name, slug, price, currency, billing one-off/monthly, features, is_popular, is_purchasable, paypal_plan_id, order)
- `Order` (package FK, customer details, amount, currency, payment_method paypal/juice/bank, status, transaction_ref, proof_of_payment file, timestamps)
- `TeamMember` (name, role, photo, bio, social links, order)
- `Lead` / `QuoteRequest` (contact info, project_type, budget, timeline, message, attachment, language, source page, status, notes)
- `TemplateInquiry` (template FK + contact info, status)
- `SiteSettings` (singleton: stats, WhatsApp, Calendly, contacts, socials, announcement, payment details, SEO defaults)

---

## 9. Multilingual Requirements
- Languages: **English (default)**, **French**, **Mauritian Kreol**.
- Mauritian Creole has the ISO 639-3 code `mfe`, which Django does not support out of the box. A custom language entry must be added to `LANGUAGES` with a custom locale, falling back to French/English for Django's built-in strings. The URL prefix is configurable, e.g. `/kr/` or `/mfe/`.
- All UI strings and all content models must be translatable.
- The language switcher keeps the user on the equivalent page.
- WhatsApp pre-filled messages and email auto-replies are sent in the visitor's language.

---

## 10. Content Status
- Content is **partially available**: some logos, projects, screenshots and prices exist.
- Development uses **seed/demo data** (management command or fixtures) for anything missing, and all of it is replaceable via admin.
- Content to collect from the owner: logo and brand colours (if any), the project list with screenshots/live URLs/videos, team photos and bios, service package names and prices, the WhatsApp number, the Calendly URL, the MCB Juice number/QR, contact details, and translations (FR/Kreol).

---

## 11. Out of Scope for v1 (Future Enhancements)
- **AI chatbot on the Webmoris site** (lead-capturing assistant). Planned for a later phase.
- Blog / resources section.
- Newsletter signup.
- Client testimonials, client logo strip, and Google reviews integration (not selected for v1; strongly recommended later for trust).
- Before/after comparison slider on case studies.
- Online checkout for ready-made websites (v1 is inquiry only).
- Downloadable templates / membership area (the reference site's model).
- Stripe card payments.
- Client portal (project progress, invoices).

---

## 12. Acceptance Criteria (v1)
- [ ] All pages in the sitemap are built, responsive and available in EN/FR/Kreol.
- [ ] The portfolio grid filters by category without a page reload, with animated transitions.
- [ ] Case studies show the challenge/solution/results, a screenshot gallery with lightbox, a video and a live link.
- [ ] Ready-made website catalog with live demo links and a working inquiry form (saved and emailed).
- [ ] Quote form, WhatsApp floating button and Calendly booking all working.
- [ ] Service packages purchasable via PayPal (one-off and monthly), and the MCB Juice manual-verification flow works end to end.
- [ ] Dark, bold design with GSAP scroll animations and a Three.js hero, with `prefers-reduced-motion` and mobile fallbacks.
- [ ] All content editable through Django admin, and seed data command available.
- [ ] SEO basics (meta, OG, hreflang, sitemap, schema) and Lighthouse targets met.
- [ ] Deployment-agnostic production settings documented (`.env.example`, README deploy notes).
