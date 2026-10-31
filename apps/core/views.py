from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from apps.portfolio.models import Project
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
            "show_pricing": False,  # enabled in Phase 5 with service packages
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


class PlaceholderView(TemplateView):
    """Stand-in for pages that later phases build out."""

    template_name = "pages/placeholder.html"
    title = ""

    def get_context_data(self, **kwargs):
        return super().get_context_data(title=self.title, **kwargs)
