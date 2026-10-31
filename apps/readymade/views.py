from django.shortcuts import get_object_or_404, render
from django.utils.cache import patch_vary_headers

from .models import TemplateIndustry, WebsiteTemplate


def template_list(request):
    industries = TemplateIndustry.objects.filter(templates__is_published=True).distinct()
    active = industries.filter(slug=request.GET.get("industry")).first()

    templates = WebsiteTemplate.objects.published().select_related("industry")
    if active:
        templates = templates.filter(industry=active)

    context = {"industries": industries, "active_industry": active, "templates": templates}
    template_name = "readymade/list.html"
    if request.headers.get("HX-Request") and request.headers.get("HX-Target") == "template-grid":
        template_name = "readymade/partials/grid.html"
    response = render(request, template_name, context)
    patch_vary_headers(response, ("HX-Request", "HX-Target"))
    return response


def template_detail(request, slug):
    template = get_object_or_404(
        WebsiteTemplate.objects.published().select_related("industry").prefetch_related("images"),
        slug=slug,
    )
    others = (
        WebsiteTemplate.objects.published()
        .select_related("industry")
        .exclude(pk=template.pk)
        .order_by("-is_featured", "order")[:3]
    )
    return render(
        request, "readymade/detail.html", {"template": template, "other_templates": others}
    )
