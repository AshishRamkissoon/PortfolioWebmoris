"""Language URL prefixes that may differ from the language code.

Kreol uses the ISO code ``mfe`` (for hreflang, html lang, .po files) but is served
under ``/kr/``. The mapping lives in ``settings.LANGUAGE_URL_PREFIXES``.
"""

from django.conf import settings
from django.urls import URLResolver
from django.urls.resolvers import LocalePrefixPattern
from django.utils.translation import get_language


def url_prefix_for(language_code):
    return settings.LANGUAGE_URL_PREFIXES.get(language_code, language_code)


def language_from_path(path):
    """Return the language code whose URL prefix starts ``path``, or None."""
    first_segment = path.lstrip("/").split("/", 1)[0]
    for code, _name in settings.LANGUAGES:
        if url_prefix_for(code) == first_segment:
            return code
    return None


class PrefixedLocalePattern(LocalePrefixPattern):
    @property
    def language_prefix(self):
        language_code = get_language() or settings.LANGUAGE_CODE
        if language_code == settings.LANGUAGE_CODE and not self.prefix_default_language:
            return ""
        return f"{url_prefix_for(language_code)}/"


def i18n_patterns(*urls, prefix_default_language=True):
    """Drop-in replacement for django.conf.urls.i18n.i18n_patterns using custom prefixes."""
    if not settings.USE_I18N:
        return list(urls)
    return [URLResolver(PrefixedLocalePattern(prefix_default_language), list(urls))]
