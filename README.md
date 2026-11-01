# Webmoris — Agency Website

Django site for Webmoris (web development + AI marketing, Mauritius), available in English and French.
See [requirements.md](requirements.md), [plan.md](plan.md) and [progress.md](progress.md).

## Requirements
- Python 3.12+
- Node.js 20+
- GNU gettext, only to edit translations (Git for Windows already includes it)

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements/dev.txt
npm install
copy .env.example .env            # macOS/Linux: cp; then edit values
python manage.py migrate
python manage.py seed_demo        # demo content, safe to re-run
python manage.py createsuperuser
pre-commit install
```

## Run locally
Use two terminals:
```bash
npm run dev                       # Tailwind + esbuild in watch mode → static/dist/
python manage.py runserver
```
- Site: http://127.0.0.1:8000/ (redirects to `/en/` or `/fr/`)
- Admin: `http://127.0.0.1:8000/<ADMIN_URL>`, which defaults to `/manage-webmoris/`. `/admin/` is intentionally disabled.

## Content
- **Portfolio:** in admin, go to Portfolio → Projects.
  - Each project has a cover image, translated text in EN/FR tabs, result metrics, screenshots marked Desktop or Mobile, and an optional YouTube/Vimeo link or MP4 file.
  - Only *published* projects appear on the site, and *featured* ones go on the home page.
  - Set **status** to *In progress* for unfinished work. Those projects get an "In progress" badge, and their results, metrics and live-site link stay hidden.
  - While there are fewer than 3 completed projects, the home section reads "What we're building now". From 3 onwards it switches to "Projects we're proud of" (`SHOWCASE_MIN_COMPLETED` in `apps/core/views.py`).
- **Uploads:** files are renamed to random names. Images must be JPG, PNG or WebP (max 10 MB) and videos MP4 or WebM (max 50 MB). Resized WebP versions are generated automatically into `media/CACHE/`.
- **Demo content:** `seed_demo` adds 7 demo projects whose clients are marked "(demo)". Delete them in admin once real projects are in.

## Leads (quote requests and template enquiries)
- In admin, go to **Leads**. Update the status (New → Contacted → Quoted → Won/Lost) and add internal notes, or select leads and use "Export selected to CSV".
- **Emails:** each lead sends a notification to `LEADS_NOTIFY_EMAIL` (or the contact email in Site settings) and an auto-reply to the visitor in their language. In development, both emails print in the `runserver` console.
- **Attachments:** stored in `PRIVATE_MEDIA_ROOT` (default `private_media/`), never served publicly. Staff download them from the lead's admin page. Back this folder up together with the database.
- **Spam protection:** a hidden honeypot field, rate limiting (`LEADS_RATE_LIMIT` per hour per visitor), and optional Cloudflare Turnstile (`TURNSTILE_SITE_KEY` / `TURNSTILE_SECRET_KEY`). In production:
  - set `CACHE_URL` to a shared cache (e.g. `dbcache://django_cache`, then run `createcachetable`) so limits apply across workers
  - set `TRUSTED_PROXY_COUNT=1` behind Nginx
- **Booking:** paste an `https://calendly.com/...` or `https://cal.com/...` link into Site settings. It is embedded on the Contact page.

## Pricing & payments
- **Packages:** in admin, go to Pricing & orders → Packages.
  - Each package has a **price** in MUR, shown on the site and used for Juice and bank transfers.
  - It also has an optional **PayPal price** in USD or EUR, because PayPal can't charge MUR. Leave it empty to hide PayPal for that package.
  - Untick "can be bought online" to show "Request a quote" instead.
- **MCB Juice and bank:** fill the Juice number, QR code and bank details in Site settings.
  - The customer pays, then uploads a receipt or enters a reference, and the order shows "Payment being verified".
  - Check the payment, then select the order and run **"Mark Juice / bank payment as verified"**. This marks it paid and emails the customer.
- **PayPal setup:**
  1. At developer.paypal.com, create a REST app (Sandbox first) and set `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` and `PAYPAL_MODE=sandbox`.
  2. Add a webhook pointing to `https://<your-domain>/payments/paypal/webhook/` for these events:
     - `PAYMENT.CAPTURE.COMPLETED`, `.DENIED` and `.REFUNDED`
     - `BILLING.SUBSCRIPTION.ACTIVATED`, `.CANCELLED` and `.EXPIRED`

     Put its ID in `PAYPAL_WEBHOOK_ID`. Webhooks are rejected unless PayPal confirms their signature.
  3. **Monthly packages:** create a Product and a Billing Plan in PayPal, then paste the plan ID (`P-…`) into the package.
  4. Test with PayPal sandbox buyer accounts, then switch to `PAYPAL_MODE=live` with live credentials.
- **Security:**
  - Prices always come from the server. The browser only asks the server to create or capture a payment.
  - Every PayPal result is checked: reference, amount, currency, plan.
  - An order is marked paid exactly once, even if the browser and the webhook arrive together.
  - Order pages use an unguessable link, and payment proofs are stored privately.

## Quality checks
```bash
pytest
ruff check . && ruff format --check .
```

## Translations
- Languages are `en` (default) and `fr`, served under `/en/` and `/fr/`.
- After changing UI text:
  ```bash
  python manage.py makemessages -l fr --ignore=.venv --ignore=node_modules --ignore=static
  # edit locale/<lang>/LC_MESSAGES/django.po
  python manage.py compilemessages --ignore=.venv --ignore=node_modules
  ```
- After running `makemessages`, check for entries marked `#, fuzzy`. These are gettext's guesses from similar strings, they are often wrong, and Django ignores them. Fix them and delete the flag: `msgattrib --only-fuzzy locale/fr/LC_MESSAGES/django.po`.
- The compiled `.mo` files are committed, so servers don't need GNU gettext.
- Content stored in the database (for example site settings) is translated in admin, using the EN / FR tabs.

## Production
See **[docs/DEPLOY.md](docs/DEPLOY.md)**. It covers the environment variables, `scripts/build.sh`, the three hosting options (VPS, PaaS, cPanel), a go-live checklist and backups.

## Security notes
- **Content-Security-Policy:**
  - Django's built-in CSP middleware sets it on every response.
  - Inline scripts need `nonce="{{ csp_nonce }}"`.
  - Alpine uses its CSP-safe build, so `x-*` expressions must stay simple (call component methods; no arrow functions or template literals in templates).
  - Iframes are created in JS, not bound with Alpine.
- **New third parties** (embeds, scripts) must be added to `SECURE_CSP` in `config/settings/base.py`, or the browser will block them.
- **`robots.txt`** deliberately never mentions the admin URL.
