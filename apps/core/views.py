import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_GET

from apps.portfolio.models import Project
from apps.pricing.models import Package
from apps.readymade.models import WebsiteTemplate
from apps.services.views import published_groups

from .models import AboutPage, HeroBusiness, LegalPage, ProcessStep, SiteSettings, TeamMember
from .templatetags.core_tags import money


def hero_businesses():
    """Business types for the hero picker, as plain data for the template and the script."""
    contact = reverse("leads:contact")
    items = []
    for business in HeroBusiness.objects.filter(is_active=True).select_related(
        "package", "template"
    ):
        package, template = business.package, business.template
        has_price = package is not None and package.is_published and package.price is not None
        has_demo = template is not None and template.is_published and bool(template.cover_image)
        items.append(
            {
                "slug": business.slug,
                "label": business.label,
                "features": business.feature_list[:3],
                "price": money(package.price, package.currency) if has_price else "",
                "image": template.cover_card.url if has_demo else "",
                "demo_name": template.name if has_demo else "",
                "demo_url": template.get_absolute_url() if has_demo else "",
                "quote_url": f"{contact}?{urlencode({'type': business.project_type})}",
            }
        )
    return items


def projects_first(site_settings, has_showcase):
    """Whether the projects section comes right after the hero (Site settings → Home sections)."""
    position = site_settings.home_projects_position
    if position == site_settings.ProjectsPosition.AUTO:
        return has_showcase
    return position == site_settings.ProjectsPosition.TOP


def home(request):
    site_settings = SiteSettings.load()
    texts = site_settings.hero_texts
    # Below this many finished projects, the work is presented as "in progress".
    has_showcase = Project.objects.completed().count() >= site_settings.showcase_min_completed
    businesses = hero_businesses()
    selected = next((b for b in businesses if b["slug"] == request.GET.get("business")), None)
    # Until a visitor picks a business type, the preview shows the first demo.
    preview = (
        selected
        if selected and selected["image"]
        else next((b for b in businesses if b["image"]), None)
    )
    return render(
        request,
        "pages/home.html",
        {
            "hero_businesses": businesses,
            "hero_selected": selected,
            "hero_preview": preview,
            "hero_quote_url": selected["quote_url"] if selected else reverse("leads:contact"),
            "hero_text": texts,
            # A real face next to the call to action (Site settings → team badge).
            "hero_director": site_settings.hero_badge_person(),
            # Read by the hero script from an auto-escaped data attribute (no inline script).
            "hero_json": json.dumps(
                {
                    "businesses": businesses,
                    "defaultFeatures": texts["tags"],
                }
            ),
            "featured_projects": Project.objects.featured().prefetch_related("categories")[:6],
            "has_showcase": has_showcase,
            "projects_first": projects_first(site_settings, has_showcase),
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
