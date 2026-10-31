"""Spam protection for public forms: rate limiting and optional Cloudflare Turnstile.

The honeypot field lives on the forms (see forms.SpamProtectedForm).
"""

import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import salted_hmac

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
RATE_LIMIT_WINDOW = 60 * 60  # seconds


def client_ip(request):
    """Visitor IP, trusting X-Forwarded-For only for the configured number of proxies."""
    proxies = settings.TRUSTED_PROXY_COUNT
    if proxies:
        forwarded = [ip.strip() for ip in request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")]
        forwarded = [ip for ip in forwarded if ip]
        if len(forwarded) >= proxies:
            return forwarded[-proxies]
    return request.META.get("REMOTE_ADDR", "")


def over_rate_limit(request, scope):
    """Count one submission for this visitor; True once they exceed the hourly limit.

    Only a salted hash of the IP is used as the cache key; the IP itself is never stored.
    """
    digest = salted_hmac("leads.rate-limit", client_ip(request), algorithm="sha256").hexdigest()
    key = f"leads:rate:{scope}:{digest}"
    cache.add(key, 0, RATE_LIMIT_WINDOW)
    try:
        count = cache.incr(key)
    except ValueError:  # expired between add() and incr()
        cache.set(key, 1, RATE_LIMIT_WINDOW)
        count = 1
    return count > settings.LEADS_RATE_LIMIT


def turnstile_enabled():
    return bool(settings.TURNSTILE_SITE_KEY and settings.TURNSTILE_SECRET_KEY)


def turnstile_passed(request):
    """Verify the Turnstile token. Fails open on network errors so real leads are not lost."""
    if not turnstile_enabled():
        return True
    token = request.POST.get("cf-turnstile-response", "")
    if not token:
        return False
    data = urllib.parse.urlencode(
        {"secret": settings.TURNSTILE_SECRET_KEY, "response": token, "remoteip": client_ip(request)}
    ).encode()
    try:
        with urllib.request.urlopen(TURNSTILE_VERIFY_URL, data=data, timeout=5) as response:  # noqa: S310
            return bool(json.load(response).get("success"))
    except (OSError, ValueError):
        logger.warning("Turnstile verification unavailable; accepting submission.")
        return True
