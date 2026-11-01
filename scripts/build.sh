#!/usr/bin/env bash
# Production build: run on the server (or CI) from the project root, with .env in place.
set -euo pipefail
export DJANGO_SETTINGS_MODULE=config.settings.prod

pip install -r requirements/prod.txt
npm ci
npm run build
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py check --deploy --fail-level WARNING
echo "Build complete."
