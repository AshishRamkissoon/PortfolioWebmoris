from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.middleware.locale import LocaleMiddleware
from django.urls import get_script_prefix, is_valid_path
from django.utils import translation
from django.utils.cache import patch_vary_headers

from .i18n import language_from_path, url_prefix_for


class PrefixedLocaleMiddleware(LocaleMiddleware):
    """LocaleMiddleware that understands prefixes from settings.LANGUAGE_URL_PREFIXES."""

    def process_request(self, request):
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        i18n_patterns_used, prefixed_default_language = is_language_prefix_patterns_used(urlconf)
        language = language_from_path(request.path_info) if i18n_patterns_used else None
        if not language:
            if i18n_patterns_used and not prefixed_default_language:
                language = settings.LANGUAGE_CODE
            else:
                language = translation.get_language_from_request(request, check_path=False)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()
        path_language = language_from_path(request.path_info)
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        i18n_patterns_used, prefixed_default_language = is_language_prefix_patterns_used(urlconf)

        if (
            response.status_code == 404
            and not path_language
            and i18n_patterns_used
            and prefixed_default_language
        ):
            # The prefix may be missing: redirect to the prefixed URL if it exists.
            prefix = url_prefix_for(language)
            language_path = f"/{prefix}{request.path_info}"
            path_valid = is_valid_path(language_path, urlconf)
            path_needs_slash = not path_valid and (
                settings.APPEND_SLASH
                and not language_path.endswith("/")
                and is_valid_path(f"{language_path}/", urlconf)
            )
            if path_valid or path_needs_slash:
                script_prefix = get_script_prefix()
                language_url = request.get_full_path(force_append_slash=path_needs_slash).replace(
                    script_prefix, f"{script_prefix}{prefix}/", 1
                )
                redirect = self.response_redirect_class(language_url)
                patch_vary_headers(redirect, ("Accept-Language", "Cookie"))
                return redirect

        if not (i18n_patterns_used and path_language):
            patch_vary_headers(response, ("Accept-Language",))
        response.headers.setdefault("Content-Language", language)
        return response
