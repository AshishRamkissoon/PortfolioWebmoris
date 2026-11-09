from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

from apps.core.models import SiteSettings
from apps.core.templatetags.core_tags import money

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
    whatsapp_message = _("Hello, I'm interested in the ready-made website “%(name)s”.") % {
        "name": template.name
    }
    return render(
        request,
        "readymade/detail.html",
        {"template": template, "other_templates": others, "whatsapp_message": whatsapp_message},
    )


@require_GET
def demo_badge(request, slug):
    """Public data for the "Get this website" badge on a live demo (another domain).

    Only what is already public on the site: the starting price and the WhatsApp link,
    both managed in admin. No cookies, so the demos can read it with a plain CORS request.
    """
    template = get_object_or_404(WebsiteTemplate.objects.published(), slug=slug)
    site_settings = SiteSettings.load()
    data = {"price": None, "whatsapp": None}
    for lang, _name in settings.LANGUAGES:
        with translation.override(lang):
            if template.starting_price is not None:
                data["price"] = data["price"] or {}
                data["price"][lang] = money(template.starting_price, "MUR")
            message = _("Hi Webmoris! I'm interested in the %(name)s website.") % {
                "name": template.name
            }
            link = site_settings.whatsapp_link_for(message)
            if link:
                data["whatsapp"] = data["whatsapp"] or {}
                data["whatsapp"][lang] = link
    response = JsonResponse(data)
    response["Access-Control-Allow-Origin"] = "*"
    response["Cache-Control"] = "public, max-age=300"
    return response
