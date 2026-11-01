from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.i18n import i18n_patterns
from apps.core.sitemaps import SITEMAPS
from apps.core.views import robots_txt
from apps.pricing.views import paypal_webhook

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # Fixed, language-independent URL registered in the PayPal dashboard.
    path("payments/paypal/webhook/", paypal_webhook, name="paypal_webhook"),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

urlpatterns += i18n_patterns(
    path("portfolio/", include("apps.portfolio.urls")),
    path("services/", include("apps.services.urls")),
    path("ready-made-websites/", include("apps.readymade.urls")),
    path("contact/", include("apps.leads.urls")),
    path("pricing/", include("apps.pricing.urls")),
    path("", include("apps.core.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
