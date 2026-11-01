"""Gunicorn settings (used by the Procfile and the systemd unit). Tunable via env vars."""

import multiprocessing
import os

bind = os.environ.get("GUNICORN_BIND", f"0.0.0.0:{os.environ.get('PORT', '8000')}")
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
timeout = 30  # PayPal calls use a 20 s timeout
graceful_timeout = 30
max_requests = 1000  # recycle workers to keep memory in check
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
# Trust X-Forwarded-* only from the local reverse proxy.
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1")
