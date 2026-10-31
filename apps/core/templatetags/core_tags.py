from django import template
from django.conf import settings
from django.urls import translate_url
from django.utils.translation import get_language

from ..i18n import url_prefix_for

register = template.Library()

LANGUAGE_LABELS = {"en": "EN", "fr": "FR", "mfe": "KR"}


@register.simple_tag(takes_context=True)
def language_links(context):
    """The current page in every language, for the switcher and hreflang tags."""
    request = context["request"]
    current = get_language()
    path = request.get_full_path()
    links = []
    for code, name in settings.LANGUAGES:
        url = translate_url(path, code)
        links.append(
            {
                "code": code,
                "label": LANGUAGE_LABELS.get(code, url_prefix_for(code).upper()),
                "name": name,
                "url": url,
                "absolute_url": request.build_absolute_uri(url),
                "active": code == current,
            }
        )
    return links
