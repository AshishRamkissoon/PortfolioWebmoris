from django import template
from django.conf import settings
from django.template.defaultfilters import floatformat
from django.urls import translate_url
from django.utils.translation import get_language

from ..booking import booking_embed_url
from ..models import FAQ, TrustPromise

register = template.Library()


@register.simple_tag(takes_context=True)
def language_links(context):
    """The current page in every language, for the switcher and hreflang tags."""
    request = context["request"]
    current = get_language()
    path = request.get_full_path()
    origin = f"{request.scheme}://{request.get_host()}"
    links = []
    for code, name in settings.LANGUAGES:
        url = translate_url(path, code)
        links.append(
            {
                "code": code,
                "label": code.upper(),
                "name": name,
                "url": url,
                "absolute_url": request.build_absolute_uri(url),
                "canonical_url": origin + translate_url(request.path, code),
                "active": code == current,
            }
        )
    return links


@register.filter
def lines(value):
    """Split a one-item-per-line text field into a list, skipping blank lines."""
    return [line.strip() for line in str(value or "").splitlines() if line.strip()]


@register.filter
def label_split(item):
    """ "Fast loading: clean code" -> ("Fast loading:", "clean code"); ("", item) without a label.

    The label keeps its colon, so French spacing ("Bases SEO :") is preserved."""
    label, sep, text = str(item).partition(": ")
    if sep and text and 0 < len(label) <= 60:
        return (label + ":", text)
    return ("", str(item))


@register.filter(name="booking_embed_url")
def booking_embed_url_filter(url):
    return booking_embed_url(url)


@register.simple_tag(takes_context=True)
def whatsapp_url(context, message=None):
    """WhatsApp link; pages can pass a more specific pre-filled message."""
    site_settings = context.get("site_settings")
    return site_settings.whatsapp_link_for(message) if site_settings else ""


@register.filter
def money(amount, currency=""):
    """ "MUR 25,000" / "USD 549.50", grouped for the active language."""
    if amount is None or amount == "":
        return ""
    return f"{currency} {floatformat(amount, '-2g')}".strip()


@register.inclusion_tag("components/promises.html", takes_context=True)
def trust_promises(context, layout="grid"):
    """The promises from admin: a section with cards ("grid") or a compact side list ("list")."""
    return {"promises": TrustPromise.objects.filter(is_active=True), "layout": layout}


FAQ_PAGES = {"pricing": "on_pricing", "contact": "on_contact"}


@register.inclusion_tag("components/faq.html", takes_context=True)
def faq_section(context, page):
    """The general FAQs picked for a page in admin, with FAQPage structured data."""
    faqs = FAQ.objects.filter(is_active=True, **{FAQ_PAGES[page]: True})
    return {
        "faqs": list(faqs),
        "request": context.get("request"),
        "csp_nonce": context.get("csp_nonce", ""),
    }
