from django.urls import path

from . import views
from .models import LegalPage

app_name = "core"


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("privacy/", views.legal_page, {"kind": LegalPage.Kind.PRIVACY}, name="privacy"),
    path("terms/", views.legal_page, {"kind": LegalPage.Kind.TERMS}, name="terms"),
]
