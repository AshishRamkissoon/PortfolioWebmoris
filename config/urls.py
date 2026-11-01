from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.i18n import i18n_patterns
from apps.pricing.views import paypal_webhook

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # Fixed, language-independent URL registered in the PayPal dashboard.
    path("payments/paypal/webhook/", paypal_webhook, name="paypal_webhook"),
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
