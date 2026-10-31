from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import HomeView, PlaceholderView

app_name = "core"


def placeholder(route, name, title):
    return path(route, PlaceholderView.as_view(title=title), name=name)


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    # Placeholders — replaced by their own apps in Phases 3–5.
    placeholder("ready-made-websites/", "readymade", _("Ready-made Websites")),
    placeholder("services/", "services", _("Services")),
    placeholder("pricing/", "pricing", _("Pricing")),
    placeholder("about/", "about", _("About")),
    placeholder("contact/", "contact", _("Contact")),
    placeholder("privacy/", "privacy", _("Privacy Policy")),
    placeholder("terms/", "terms", _("Terms & Conditions")),
]
