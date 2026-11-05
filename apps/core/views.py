from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.portfolio.models import Project
from apps.pricing.models import Package
from apps.readymade.models import WebsiteTemplate
from apps.services.views import published_groups

from .models import AboutPage, LegalPage, ProcessStep, TeamMember

# Below this many completed projects, Home presents the work as "in progress"
# instead of claiming a showcase of finished projects.
SHOWCASE_MIN_COMPLETED = 3


def home(request):
    return render(
        request,
        "pages/home.html",
        {
            "featured_projects": Project.objects.featured().prefetch_related("categories")[:6],
            "has_showcase": Project.objects.completed().count() >= SHOWCASE_MIN_COMPLETED,
            "service_groups": published_groups(),
            "featured_templates": WebsiteTemplate.objects.featured().select_related("industry")[:3],
            "process_steps": ProcessStep.objects.all(),
            "packages": Package.objects.published().order_by("order")[:3],
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


@require_GET
def robots_txt(request):
    # Never list the admin URL here: this file is public and would reveal it.
    lines = [
        "User-agent: *",
        "Disallow: /*/pricing/order/",
        "Disallow: /*/pricing/*/checkout/",
        "Disallow: /*/contact/ready-made/",
        "Disallow: /payments/",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}{reverse('sitemap')}",
    ]
    lines.append("")
    return HttpResponse("\n".join(lines), content_type="text/plain")
