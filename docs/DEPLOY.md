# Deploying Webmoris

The project is host-agnostic. Pick one of the three options below. Every option needs the same environment variables and the same build steps.

## 1. Environment variables (`.env`)
Copy `.env.example` to `.env` on the server and fill it in.

**Required in production:**

| Variable | Example |
|---|---|
| `SECRET_KEY` | long random string: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `ALLOWED_HOSTS` | `webmoris.mu,www.webmoris.mu` |
| `CSRF_TRUSTED_ORIGINS` | `https://webmoris.mu` |
| `DATABASE_URL` | `postgres://webmoris:PASSWORD@localhost:5432/webmoris` |
| `EMAIL_URL` | `smtp+tls://USER:PASSWORD@smtp-relay.brevo.com:587` |
| `DEFAULT_FROM_EMAIL` | `Webmoris <hello@webmoris.mu>` |
| `ADMIN_URL` | a private path such as `studio-7f3k2/` (not `admin/`) |
| `CACHE_URL` | `dbcache://django_cache` (then run `createcachetable`) or `redis://localhost:6379/1` |
| `TRUSTED_PROXY_COUNT` | `1` behind Nginx or a PaaS router |

**Optional:**
- `LEADS_NOTIFY_EMAIL`, `ORDERS_NOTIFY_EMAIL`
- PayPal: `PAYPAL_*` (see the README)
- Turnstile: `TURNSTILE_*`
- Analytics: `ANALYTICS_PROVIDER`, `PLAUSIBLE_DOMAIN`, `GA4_MEASUREMENT_ID`
- `PRIVATE_MEDIA_ROOT`

The app refuses to start in production if `SECRET_KEY`, `ALLOWED_HOSTS` or `EMAIL_URL` is missing. That's deliberate, so a misconfigured server fails loudly instead of running insecurely or dropping lead emails.

## 2. Build (every deploy)
```bash
./scripts/build.sh
```
This script does the following:
1. Installs the Python and npm packages.
2. Builds the CSS, JS and fonts.
3. Runs `collectstatic` and `migrate`.
4. Runs `check --deploy`, and fails if there is any warning.

On the very first deploy, also run:
```bash
python manage.py createcachetable      # only if CACHE_URL uses dbcache://
python manage.py createsuperuser
```

## 3. Hosting options

### A. VPS (Ubuntu, Nginx, Gunicorn, PostgreSQL), recommended
1. Create a `webmoris` user. Put the code in `/srv/webmoris/app` and a virtualenv in `/srv/webmoris/venv`.
2. Install PostgreSQL and create the database and user.
3. Copy `deploy/webmoris.service` to `/etc/systemd/system/`, then run `systemctl enable --now webmoris`.
4. Copy `deploy/nginx.conf.example` to `/etc/nginx/sites-available/webmoris`, set the domain, enable the site, and run `certbot --nginx`.
5. `media/` is served by Nginx. `private_media/` (attachments, payment proofs) must **not** be under any Nginx `location`.

### B. PaaS (Render / Railway)
- Add a PostgreSQL add-on. It sets `DATABASE_URL`.
- The `Procfile` runs migrations on release and starts Gunicorn.
- Set the build command to `./scripts/build.sh`, or the equivalent steps.
- **Uploads need a persistent disk.** Mount a volume at `media/` and set `PRIVATE_MEDIA_ROOT` to a path on the volume. Otherwise uploads disappear on every deploy.

### C. cPanel (Setup Python App / Passenger)
- Create a Python 3.12+ app pointing to the project folder. The entry point is `passenger_wsgi.py`.
- Run the build steps in the cPanel terminal. If Node isn't available, run `npm run build` locally and upload `static/dist/`.
- Point `/media/` at the `media/` folder, and keep `private_media/` outside `public_html`.

## 4. After going live
- [ ] Log in at `https://<domain>/<ADMIN_URL>`. Replace all demo content, and delete the demo items marked "(demo)" or "DEMO".
- [ ] Fill in Site settings: contact details, WhatsApp, Calendly, Juice and bank details, social links, share image.
- [ ] Have a lawyer review the Privacy Policy and Terms. They must replace the demo text.
- [ ] PayPal: set up the live app and webhook, and create a plan for each monthly package (see the README).
- [ ] Send a test quote request and check that both emails arrive.
- [ ] Submit `https://<domain>/sitemap.xml` in Google Search Console.
- [ ] Check https://securityheaders.com (expect A or better) and run Lighthouse on Home, Portfolio and a case study.

## 5. Backups
Back up these three things together, daily:
- **The database:** `pg_dump -Fc webmoris > webmoris-$(date +%F).dump`
- **`media/`:** public images and videos.
- **`private_media/`:** client attachments and payment proofs. These contain personal data, so encrypt them and restrict access.

Keep copies off the server (for example a storage bucket with versioning), and test a restore now and then.

## 6. Housekeeping (cron)
```cron
# Remove expired sessions weekly
0 3 * * 0  cd /srv/webmoris/app && /srv/webmoris/venv/bin/python manage.py clearsessions
```
