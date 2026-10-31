from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.i18n import i18n_patterns

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("portfolio/", include("apps.portfolio.urls")),
    path("services/", include("apps.services.urls")),
    path("ready-made-websites/", include("apps.readymade.urls")),
    path("contact/", include("apps.leads.urls")),
    path("", include("apps.core.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
