import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _

from apps.core.models import SiteSettings

logger = logging.getLogger(__name__)


def _send(subject, template, context, to, reply_to=None):
    message = EmailMultiAlternatives(
        subject=" ".join(str(subject).split()),  # never allow newlines in headers
        body=render_to_string(f"emails/{template}.txt", context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        reply_to=reply_to or [],
    )
    message.attach_alternative(render_to_string(f"emails/{template}.html", context), "text/html")
    message.send()


def send_lead_emails(request, lead):
    """Notify the team and auto-reply to the visitor in their language.

    The auto-reply contains only our own text, never what the visitor typed: otherwise the
    form could be abused to send arbitrary content to any address through our mail server.
    The lead is already saved, so an email failure is logged (without personal data)
    rather than shown to the visitor.
    """
    site_settings = SiteSettings.load()
    opts = lead._meta
    context = {
        "lead": lead,
        "lead_kind": opts.verbose_name,
        "site_settings": site_settings,
        "admin_url": request.build_absolute_uri(
            reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[lead.pk])
        ),
        "site_url": request.build_absolute_uri("/"),
    }

    notify_to = settings.LEADS_NOTIFY_EMAIL or site_settings.contact_email
    try:
        if notify_to:
            with translation.override(settings.LANGUAGE_CODE):
                _send(
                    f"New {opts.verbose_name}: {lead.name}",
                    "lead_notification",
                    context,
                    [notify_to],
                    reply_to=[lead.email],
                )
        with translation.override(lead.language):
            _send(
                _("We received your message — %(site)s") % {"site": site_settings.site_name},
                "lead_auto_reply",
                context,
                [lead.email],
            )
    except Exception:
        logger.exception("Sending emails failed for %s id=%s", opts.model_name, lead.pk)
