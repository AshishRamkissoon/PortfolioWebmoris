from urllib.parse import urlparse

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from apps.portfolio.models import Project
from apps.readymade.models import WebsiteTemplate
from apps.services.models import Service

from .emails import send_lead_emails
from .forms import QuoteRequestForm, TemplateInquiryForm
from .models import QuoteRequest
from .spam import over_rate_limit, turnstile_enabled, turnstile_passed


def _safe_path(request, value):
    """The path of a URL on this site (for the "sent from page" field); empty otherwise."""
    parsed = urlparse(value or "")
    if parsed.netloc and parsed.netloc != request.get_host():
        return ""
    if parsed.scheme not in ("", "http", "https") or not parsed.path.startswith("/"):
        return ""
    return parsed.path[:200]


def _quote_initial(params):
    """Pre-fill the quote form from ?template=, ?project=, ?service= or ?type= links.

    Only slugs of published objects are used, so links can't inject arbitrary text."""
    types = QuoteRequest.ProjectType
    templates = WebsiteTemplate.objects.published()
    projects = Project.objects.published()
    services = Service.objects.published().select_related("group")

    if (slug := params.get("template")) and (template := templates.filter(slug=slug).first()):
        message = _("I'm interested in the ready-made website “%(name)s”.")
        return {"project_type": types.READYMADE, "message": message % {"name": template.name}}

    if (slug := params.get("project")) and (project := projects.filter(slug=slug).first()):
        message = _("I'd like a project like “%(name)s”.")
        return {"project_type": types.WEBSITE, "message": message % {"name": project.title}}

    if (slug := params.get("service")) and (service := services.filter(slug=slug).first()):
        is_ai = service.group.slug == "ai-marketing"
        return {
            "project_type": types.AI_MARKETING if is_ai else types.WEBSITE,
            "message": _("I'm interested in: %(name)s.") % {"name": service.title},
        }

    if params.get("type") in types.values:
        return {"project_type": params["type"]}
    return {}


def _handle_submission(request, form, scope, **extra):
    """Validate spam checks, save and notify. Returns True when the visitor should see success."""
    if form.is_spam:
        return True  # pretend it worked; nothing is saved or sent
    if over_rate_limit(request, scope):
        form.add_error(None, _("You've sent several messages already. Please try again later."))
        return False
    if not turnstile_passed(request):
        form.add_error(None, _("Please complete the spam check and try again."))
        return False

    lead = form.save(commit=False)
    lead.language = request.LANGUAGE_CODE
    lead.source_page = _safe_path(request, request.POST.get("source_page"))
    for field, value in extra.items():
        setattr(lead, field, value)
    lead.save()
    send_lead_emails(request, lead)
    return True


def _render_form(request, page_template, partial_template, context):
    template = partial_template if request.headers.get("HX-Request") else page_template
    context.setdefault(
        "turnstile_site_key", settings.TURNSTILE_SITE_KEY if turnstile_enabled() else ""
    )
    return render(request, template, context)


def contact(request):
    sent = request.GET.get("sent") == "1"
    if request.method == "POST":
        form = QuoteRequestForm(request.POST, request.FILES)
        if form.is_valid() and _handle_submission(request, form, "quote"):
            if not request.headers.get("HX-Request"):
                return redirect(f"{request.path}?sent=1")
            sent = True
    else:
        form = QuoteRequestForm(initial=_quote_initial(request.GET))

    context = {
        "form": form,
        "sent": sent,
        "source_page": _safe_path(
            request, request.POST.get("source_page") or request.META.get("HTTP_REFERER")
        ),
    }
    return _render_form(request, "leads/contact.html", "leads/partials/quote_form.html", context)


def template_inquiry(request, slug):
    template = get_object_or_404(WebsiteTemplate.objects.published(), slug=slug)
    sent = request.GET.get("sent") == "1"
    if request.method == "POST":
        form = TemplateInquiryForm(request.POST)
        if form.is_valid() and _handle_submission(
            request,
            form,
            "template",
            template=template,
            template_name=template.name,
            source_page=template.get_absolute_url(),
        ):
            if not request.headers.get("HX-Request"):
                return redirect(f"{request.path}?sent=1")
            sent = True
    else:
        form = TemplateInquiryForm(
            initial={
                "message": _("I'm interested in the “%(name)s” website for my business.")
                % {"name": template.name}
            }
        )

    context = {
        "form": form,
        "sent": sent,
        "template": template,
        "source_page": template.get_absolute_url(),
    }
    return _render_form(
        request, "leads/template_inquiry.html", "leads/partials/inquiry_form.html", context
    )


@staff_member_required
def quote_attachment(request, pk):
    """Staff-only download of a private quote attachment."""
    if not request.user.has_perm("leads.view_quoterequest"):
        raise Http404
    lead = get_object_or_404(QuoteRequest, pk=pk)
    if not lead.attachment:
        raise Http404
    return FileResponse(lead.attachment.open("rb"), as_attachment=True)
