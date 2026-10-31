# Webmoris — Agency Website

Django site for Webmoris (web development + AI marketing, Mauritius), available in English, French and Kreol.
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
- Site: http://127.0.0.1:8000/ (redirects to `/en/`, `/fr/` or `/kr/`)
- Admin: `http://127.0.0.1:8000/<ADMIN_URL>`, which defaults to `/manage-webmoris/`. `/admin/` is intentionally disabled.

## Quality checks
```bash
pytest
ruff check . && ruff format --check .
```

## Translations
- Languages are `en`, `fr` and `mfe` (Kreol). Kreol is served under `/kr/`, set by `LANGUAGE_URL_PREFIXES` in `config/settings/base.py`.
- After changing UI text:
  ```bash
  python manage.py makemessages -l fr -l mfe --ignore=.venv --ignore=node_modules --ignore=static
  # edit locale/<lang>/LC_MESSAGES/django.po
  python manage.py compilemessages --ignore=.venv --ignore=node_modules
  ```
- The compiled `.mo` files are committed. Django only enables a language once its `.mo` file exists, so Kreol depends on them.
- Content stored in the database (for example site settings) is translated in admin, using the EN / FR / MFE tabs.

## Production (host-agnostic)
- Settings: `DJANGO_SETTINGS_MODULE=config.settings.prod`. This is the default for `wsgi.py` and `asgi.py`.
- Required environment variables:
  - `SECRET_KEY`
  - `ALLOWED_HOSTS`
  - `DATABASE_URL` (PostgreSQL)
  - `EMAIL_URL`
  - `ADMIN_URL`
  - `CSRF_TRUSTED_ORIGINS`
- Build:
  ```bash
  pip install -r requirements/prod.txt
  npm ci && npm run build
  python manage.py collectstatic --noinput
  python manage.py migrate
  python manage.py check --deploy
  ```
- Serve with `gunicorn config.wsgi`. WhiteNoise serves static files. Full deploy guides (VPS, PaaS, cPanel) arrive in Phase 6.
