"""sitemap.xml with every public page in EN / FR / Kreol, plus hreflang alternates."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.portfolio.models import Project
from apps.readymade.models import WebsiteTemplate
from apps.services.models import Service

from .models import LegalPage


class _Multilingual(Sitemap):
    i18n = True
    alternates = True
    x_default = True


class StaticPagesSitemap(_Multilingual):
    changefreq = "monthly"

    def items(self):
        pages = [
            ("core:home", 1.0),
            ("portfolio:list", 0.9),
            ("services:list", 0.9),
            ("readymade:list", 0.8),
            ("pricing:list", 0.8),
            ("core:about", 0.6),
            ("leads:contact", 0.7),
        ]
        pages += [
            (f"core:{kind}", 0.2) for kind in LegalPage.objects.values_list("kind", flat=True)
        ]
        return pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]


class ProjectSitemap(_Multilingual):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Project.objects.published()

    def lastmod(self, project):
        return project.updated_at


class ServiceSitemap(_Multilingual):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Service.objects.published()


class TemplateSitemap(_Multilingual):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return WebsiteTemplate.objects.published()


SITEMAPS = {
    "pages": StaticPagesSitemap,
    "projects": ProjectSitemap,
    "services": ServiceSitemap,
    "templates": TemplateSitemap,
}
