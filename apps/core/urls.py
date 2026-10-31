from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views
from .models import LegalPage

app_name = "core"


def placeholder(route, name, title):
    return path(route, views.PlaceholderView.as_view(title=title), name=name)


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("privacy/", views.legal_page, {"kind": LegalPage.Kind.PRIVACY}, name="privacy"),
    path("terms/", views.legal_page, {"kind": LegalPage.Kind.TERMS}, name="terms"),
    # Placeholder — replaced by the pricing app in Phase 5.
    placeholder("pricing/", "pricing", _("Pricing")),
]
