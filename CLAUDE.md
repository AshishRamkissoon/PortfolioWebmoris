# CLAUDE.md — Webmoris Portfolio

Agency site for **Webmoris** (web development + AI marketing, Mauritius). It has a portfolio with case studies, a catalog of ready-made websites (inquiry only), services, packages paid through PayPal or MCB Juice, and lead capture. It is available in English and French.

## Source of truth
- [requirements.md](requirements.md): what to build (scope, data model, acceptance criteria in §12). Out-of-scope items are listed in §11; don't build them unless asked.
- [plan.md](plan.md): the 6 build phases, their tasks and exit criteria. Work one phase at a time, on a `phase/<n>-<name>` branch. Don't start the next phase until the current one meets its exit criteria.
- [progress.md](progress.md): current status of each phase. **Read it at the start of every session.**
- If the code and these docs disagree, ask. Don't guess.

## Progress tracking (progress.md)
- **Starting a phase:** set its status to 🟡 In progress, fill in the Started date, and add a log entry.
- **Exit criteria met:** set the status to 🔵 Awaiting approval, fill in the Ready for review date, and log what was built and how to test it. Then ask the owner to test it.
- **Owner explicitly approves:** set the status to ✅ Completed, fill in the Approved date, and log the approval. Never mark a phase Completed without the owner's explicit approval.
- **Owner reports problems:** set the status back to 🟡 In progress and log the issues.
- Log blockers and decisions under "Open Decisions / Blockers". Log entries go newest first, with absolute dates.

## Stack & layout
- Django (5.2 LTS / 6.x), Python 3.12+, PostgreSQL (SQLite in dev), WhiteNoise.
- Tailwind + esbuild, GSAP/ScrollTrigger, Lenis, Alpine.js, HTMX, Three.js (lazy-loaded chunk only).
- Apps in `apps/`: `core`, `portfolio`, `readymade`, `services`, `leads`, `pricing`. Settings in `config/settings/{base,dev,prod}.py`.
- i18n: `django-modeltranslation` for model fields, and `gettext` for every UI string. Languages are `en` and `fr` (URL prefixes `/en/` and `/fr/`).

## Commands (once Phase 1 is in place)
- `python manage.py runserver` · `npm run dev` / `npm run build`
- `pytest` · `ruff check . && ruff format .`
- `python manage.py seed_demo` · `makemessages -l fr` / `compilemessages`

## Conventions
- All site content must be editable in Django admin; never hardcode it in templates. Global values go in the `SiteSettings` singleton.
- Progressive enhancement: pages and forms must work without JS. HTMX, Alpine, GSAP and Three.js are layered on top.
- Animations must respect `prefers-reduced-motion`. Three.js only starts on capable devices and has a static fallback.
- Reuse the Phase 1 design tokens and components; no one-off styles.
- Every change needs: a migration, admin registration, an update to the seed data, translatable strings, tests, and a clean `ruff`.

## Security rules (non-negotiable)
- **Secrets**: never commit `.env`, keys, PayPal credentials or SMTP passwords. All of them are read from environment variables via `django-environ`. Keep `.env.example` updated with placeholder values only.
- **Payments**:
  - Prices and currency always come from the server-side `Package`, never from the client.
  - Mark an order Paid only after a server-side PayPal capture or a verified webhook.
  - Verify the signature of every PayPal webhook and make the handlers idempotent.
  - Juice/bank orders become Paid only through the admin's manual verification.
- **Forms**:
  - Keep CSRF on everywhere. Never use `csrf_exempt`, except on the PayPal webhook endpoint, which relies on signature verification instead.
  - Validate everything server-side with Django forms.
  - Every public form gets a honeypot and rate limiting.
- **Uploads** (attachments, proof of payment):
  - Use an allow-list of extensions and MIME types, with size limits (≤ 10 MB).
  - Rename uploaded files.
  - Never serve uploads as executable or HTML.
  - Proof-of-payment files must not be publicly listable.
- **Output**:
  - Rely on Django's auto-escaping. No `|safe` or `mark_safe` on user or admin input unless it has been sanitized.
  - Add `rel="noopener noreferrer"` to external links.
- **CSP** (Django built-in, strict):
  - Inline `<script>` tags need `nonce="{{ csp_nonce }}"`.
  - Alpine is the CSP build, so `x-*` attributes only call component methods or read simple properties.
  - New third-party hosts must be added to `SECURE_CSP`. Never add `'unsafe-eval'` or `'unsafe-inline'` to `script-src`.
- **Database**: use the ORM only. Raw SQL is allowed only with parameterized queries.
- **Production**:
  - `DEBUG=False`, a strict `ALLOWED_HOSTS`, HTTPS redirect, HSTS, secure/HttpOnly cookies.
  - CSP via `django-csp`, allowing only the needed third parties: PayPal, Calendly, YouTube/Vimeo, analytics.
  - `manage.py check --deploy` must pass cleanly.
- **Admin**: lives on a custom URL from the `ADMIN_URL` environment variable (not `/admin/`), with strong passwords and optional 2FA.
- **Privacy**:
  - Never log personal data from leads or orders, or any payment details.
  - Lead emails must not leak other leads' data.
  - Analytics stay behind cookie consent.
- **Dependencies**: pin versions, add only well-maintained packages, and check for known vulnerabilities before adding one.
