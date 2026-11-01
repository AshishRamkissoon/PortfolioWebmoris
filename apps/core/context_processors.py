from django.conf import settings

from .models import SiteSettings


def site(request):
    return {
        "site_settings": SiteSettings.load(),
        "analytics": {
            "provider": settings.ANALYTICS_PROVIDER,
            "plausible_domain": settings.PLAUSIBLE_DOMAIN,
            "plausible_script": settings.PLAUSIBLE_SCRIPT_URL,
            "ga4_id": settings.GA4_MEASUREMENT_ID,
        },
    }
