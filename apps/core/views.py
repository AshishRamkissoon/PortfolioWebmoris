from django.shortcuts import get_object_or_404, render

from apps.portfolio.models import Project
from apps.pricing.models import Package
from apps.readymade.models import WebsiteTemplate
from apps.services.views import published_groups

from .models import AboutPage, LegalPage, ProcessStep, TeamMember


def home(request):
    return render(
        request,
        "pages/home.html",
        {
            "featured_projects": Project.objects.featured().prefetch_related("categories")[:6],
            "service_groups": published_groups(),
            "featured_templates": WebsiteTemplate.objects.featured().select_related("industry")[:6],
            "process_steps": ProcessStep.objects.all(),
            "packages": Package.objects.published().order_by("-is_popular", "order")[:3],
        },
    )


def about(request):
    return render(
        request,
        "pages/about.html",
        {
            "about": AboutPage.load(),
            "team": TeamMember.objects.filter(is_active=True),
            "process_steps": ProcessStep.objects.all(),
        },
    )


def legal_page(request, kind):
    page = get_object_or_404(LegalPage, kind=kind)
    return render(request, "pages/legal.html", {"page": page})
