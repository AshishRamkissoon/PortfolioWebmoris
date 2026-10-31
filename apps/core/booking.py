"""Calendly / Cal.com booking links: only these hosts may be embedded (iframe)."""

from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

BOOKING_HOSTS = {"calendly.com": "calendly", "cal.com": "cal"}


def booking_provider(url):
    """ "calendly" / "cal" for an https link on those hosts (or subdomains), else None."""
    parsed = urlparse(url or "")
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        return None
    for domain, provider in BOOKING_HOSTS.items():
        if host == domain or host.endswith(f".{domain}"):
            return provider
    return None


def booking_embed_url(url):
    """Dark-themed embeddable version of a booking link; empty for anything else."""
    provider = booking_provider(url)
    if not provider:
        return ""
    separator = "&" if "?" in url else "?"
    if provider == "calendly":
        colors = "background_color=0b0d14&text_color=eef0f6&primary_color=22e3ff"
        return f"{url}{separator}hide_gdpr_banner=1&{colors}"
    return f"{url}{separator}embed=true&theme=dark"


def validate_booking_url(url):
    if url and not booking_provider(url):
        raise ValidationError(_("Use an https:// Calendly or Cal.com booking link."))
