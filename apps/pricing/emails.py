import logging

from django.conf import settings
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _

from apps.core.emails import send_templated_email
from apps.core.models import SiteSettings

logger = logging.getLogger(__name__)


def _context(request, order):
    return {
        "order": order,
        "site_settings": SiteSettings.load(),
        "order_url": request.build_absolute_uri(order.get_absolute_url()),
        "admin_url": request.build_absolute_uri(
            reverse("admin:pricing_order_change", args=[order.pk])
        ),
        "site_url": request.build_absolute_uri("/"),
    }


def _team_address():
    return (
        settings.ORDERS_NOTIFY_EMAIL
        or settings.LEADS_NOTIFY_EMAIL
        or SiteSettings.load().contact_email
    )


def _safely(send):
    """Emails never break a payment flow: the order state is already saved."""

    def wrapper(request, order, *args):
        try:
            send(request, order, *args)
        except Exception:
            logger.exception("Order email %s failed for order id=%s", send.__name__, order.pk)

    return wrapper


@_safely
def notify_team(request, order, event):
    """event: "new" (manual order placed), "proof" (proof uploaded) or "paid"."""
    to = _team_address()
    if not to:
        return
    subjects = {
        "new": f"New order {order.reference} — {order.package_name} (awaiting payment)",
        "proof": f"Payment proof uploaded for {order.reference} — please verify",
        "paid": f"Order {order.reference} paid — {order.package_name}",
    }
    context = {**_context(request, order), "event": event}
    with translation.override(settings.LANGUAGE_CODE):
        send_templated_email(subjects[event], "order_team", context, [to], [order.email])


@_safely
def send_order_received(request, order):
    """Manual (Juice / bank) orders: payment instructions and the link to upload proof."""
    with translation.override(order.language):
        subject = _("Your order %(ref)s — payment instructions") % {"ref": order.reference}
        send_templated_email(subject, "order_received", _context(request, order), [order.email])


@_safely
def send_payment_confirmed(request, order):
    with translation.override(order.language):
        subject = _("Payment confirmed — order %(ref)s") % {"ref": order.reference}
        send_templated_email(subject, "order_paid", _context(request, order), [order.email])
