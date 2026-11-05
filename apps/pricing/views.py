import json
import logging
import re

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.core.models import SiteSettings
from apps.core.spam import over_rate_limit
from apps.core.uploads import private_file_response

from . import emails, paypal
from .forms import (
    CheckoutForm,
    PaymentMethodForm,
    ProofOfPaymentForm,
    available_methods,
    payment_request_methods,
)
from .models import Order, Package, PaymentRequest, PayPalWebhookEvent

logger = logging.getLogger(__name__)

PAYPAL_ID = re.compile(r"^[A-Z0-9-]{6,40}$")
MAX_WEBHOOK_BYTES = 64 * 1024


def package_list(request):
    packages = Package.objects.published()
    return render(
        request,
        "pricing/list.html",
        {
            "packages": packages,
            "one_off": [p for p in packages if not p.is_monthly],
            "monthly": [p for p in packages if p.is_monthly],
            "steps": [
                (_("Send your brief"), _("A few quick questions about your business and project.")),
                (
                    _("Get a fixed quote"),
                    _("Clear scope, price and timeline, usually within a day."),
                ),
                (_("Pay a deposit, we start"), _("The balance is due when your site goes live.")),
            ],
        },
    )


@never_cache  # personal details: never store in shared caches
def checkout(request, slug):
    package = get_object_or_404(
        Package.objects.published(), slug=slug, is_purchasable=True, price__isnull=False
    )
    methods = available_methods(package, SiteSettings.load())

    posted = request.method == "POST"
    form = CheckoutForm(request.POST if posted else None, methods=methods)
    if posted and methods and form.is_valid():
        if form.is_spam:
            return redirect("pricing:list")
        if over_rate_limit(request, "order"):
            form.add_error(None, _("Too many orders from your connection. Please try again later."))
        else:
            order = _create_order(request, form, package)
            return redirect(order)

    return render(
        request,
        "pricing/checkout.html",
        {
            "package": package,
            "form": form,
            "methods": methods,
            "paypal_available": Order.Method.PAYPAL in methods,
        },
    )


def _create_order(request, form, package):
    order = form.save(commit=False)
    order.package = package
    order.package_name = package.name
    order.billing = package.billing
    order.language = request.LANGUAGE_CODE
    # The price always comes from the package on the server, never from the browser.
    if order.payment_method == Order.Method.PAYPAL:
        order.amount, order.currency = package.paypal_price, package.paypal_currency
    else:
        order.amount, order.currency = package.price, package.currency
    order.save()
    if order.is_manual:
        emails.send_order_received(request, order)
        emails.notify_team(request, order, "new")
    return order


@never_cache  # personal details: never store in shared caches
def pay(request, token):
    """A client's private link for a deposit or balance set by staff (PaymentRequest)."""
    payment_request = get_object_or_404(PaymentRequest, access_token=token)
    paid = payment_request.paid_order
    pending = payment_request.orders.filter(status=Order.Status.PENDING_VERIFICATION).first()
    methods = payment_request_methods(payment_request, SiteSettings.load())
    open_for_payment = payment_request.is_active and not paid and not pending

    posted = request.method == "POST" and open_for_payment
    form = PaymentMethodForm(request.POST if posted else None, methods=methods)
    if posted and methods and form.is_valid():
        if over_rate_limit(request, "order"):
            form.add_error(
                None, _("Too many attempts from your connection. Please try again later.")
            )
        else:
            return redirect(
                _order_for_request(request, payment_request, form.cleaned_data["payment_method"])
            )

    return render(
        request,
        "pricing/pay.html",
        {
            "payment_request": payment_request,
            "form": form,
            "methods": methods,
            "paid_order": paid,
            "pending_order": pending,
            "open_for_payment": open_for_payment,
        },
    )


def _order_for_request(request, payment_request, method):
    """Reuse the client's unpaid order for this method, or start one. The amount always
    comes from the payment request on the server."""
    existing = payment_request.orders.filter(
        payment_method=method, status__in=[Order.Status.PENDING, Order.Status.FAILED]
    ).first()
    if existing:
        return existing
    if method == Order.Method.PAYPAL:
        amount, currency = payment_request.paypal_amount, payment_request.paypal_currency
    else:
        amount, currency = payment_request.amount, payment_request.currency
    order = Order.objects.create(
        payment_request=payment_request,
        package_name=payment_request.description,
        billing=Package.Billing.ONE_OFF,
        name=payment_request.name,
        email=payment_request.email,
        phone=payment_request.phone,
        company=payment_request.company,
        language=request.LANGUAGE_CODE,
        payment_method=method,
        amount=amount,
        currency=currency,
    )
    if order.is_manual:
        emails.send_order_received(request, order)
        emails.notify_team(request, order, "new")
    return order


@never_cache  # personal details: never store in shared caches
def order_detail(request, token):
    order = get_object_or_404(Order.objects.select_related("package"), access_token=token)
    proof_form = None
    if order.is_manual and order.awaiting_payment:
        posted = request.method == "POST"
        proof_form = ProofOfPaymentForm(
            request.POST if posted else None, request.FILES if posted else None, instance=order
        )
        if posted and proof_form.is_valid():
            order = proof_form.save(commit=False)
            order.status = Order.Status.PENDING_VERIFICATION
            order.save()
            emails.notify_team(request, order, "proof")
            return redirect(order)

    return render(
        request,
        "pricing/order.html",
        {
            "order": order,
            "proof_form": proof_form,
            "show_paypal": order.payment_method == Order.Method.PAYPAL
            and order.awaiting_payment
            and paypal.is_configured(),
            "paypal_client_id": settings.PAYPAL_CLIENT_ID,
        },
    )


def _paypal_order(token):
    order = get_object_or_404(Order.objects.select_related("package"), access_token=token)
    if order.payment_method != Order.Method.PAYPAL or not paypal.is_configured():
        raise Http404
    return order


def _paid_response(request, order, won):
    if won:
        emails.send_payment_confirmed(request, order)
        emails.notify_team(request, order, "paid")
    # ?just_paid=1 lets the page record the purchase conversion once.
    return JsonResponse({"status": "paid", "redirect": f"{order.get_absolute_url()}?just_paid=1"})


@require_POST
def paypal_create(request, token):
    order = _paypal_order(token)
    if not order.awaiting_payment or order.is_monthly:
        return JsonResponse({"error": _("This order can't be paid this way.")}, status=409)
    try:
        order.paypal_order_id = paypal.create_order(order)
    except paypal.PayPalError:
        return JsonResponse({"error": _("PayPal is unavailable. Please try again.")}, status=502)
    order.save(update_fields=["paypal_order_id", "updated_at"])
    return JsonResponse({"id": order.paypal_order_id})


@require_POST
def paypal_capture(request, token):
    order = _paypal_order(token)
    if order.is_paid:
        return _paid_response(request, order, won=False)
    if not order.paypal_order_id:
        return JsonResponse({"error": _("Payment not started.")}, status=409)
    try:
        response = paypal.capture_order(order.paypal_order_id)  # id from our DB, not the browser
    except paypal.PayPalError:
        return JsonResponse(
            {"error": _("We couldn't confirm your payment. Please try again.")}, status=502
        )

    capture_id = paypal.completed_capture(response, order)
    if not capture_id:
        logger.warning("PayPal capture not completed for order id=%s", order.pk)
        return JsonResponse(
            {
                "error": _(
                    "Your payment wasn't completed. Please try again or choose another method."
                )
            },
            status=402,
        )
    return _paid_response(request, order, order.mark_paid(capture_id))


@require_POST
def paypal_subscription(request, token):
    order = _paypal_order(token)
    if order.is_paid:
        return _paid_response(request, order, won=False)
    try:
        subscription_id = json.loads(request.body or b"{}").get("subscriptionID", "")
    except ValueError:
        return HttpResponseBadRequest()
    if not PAYPAL_ID.match(str(subscription_id)) or not (order.package and order.is_monthly):
        return HttpResponseBadRequest()

    try:
        subscription = paypal.get_subscription(subscription_id)
    except paypal.PayPalError:
        return JsonResponse(
            {"error": _("We couldn't confirm your subscription. Please try again.")}, status=502
        )
    if not paypal.subscription_is_active_for(subscription, order, order.package.paypal_plan_id):
        return JsonResponse({"error": _("Your subscription wasn't activated.")}, status=402)

    order.paypal_subscription_id = subscription_id
    order.save(update_fields=["paypal_subscription_id", "updated_at"])
    return _paid_response(request, order, order.mark_paid(subscription_id))


@csrf_exempt  # PayPal can't send our CSRF token; every event is verified with PayPal instead
@require_POST
def paypal_webhook(request):
    if len(request.body) > MAX_WEBHOOK_BYTES:
        return HttpResponseBadRequest()
    try:
        event = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest()
    if not paypal.verify_webhook(request.headers, event):
        logger.warning("Rejected unverified PayPal webhook")
        return HttpResponseBadRequest()

    try:
        with transaction.atomic():
            PayPalWebhookEvent.objects.create(
                event_id=str(event.get("id", ""))[:60], event_type=str(event.get("event_type", ""))
            )
    except IntegrityError:
        return HttpResponse(status=200)  # already processed: re-deliveries are harmless

    _apply_webhook_event(request, event)
    return HttpResponse(status=200)


def _apply_webhook_event(request, event):
    kind = event.get("event_type", "")
    resource = event.get("resource") or {}
    reference = resource.get("custom_id") or resource.get("invoice_id")
    order = Order.objects.select_related("package").filter(reference=reference).first()
    if not order:
        return

    if kind == "PAYMENT.CAPTURE.COMPLETED":
        amount = resource.get("amount", {})
        if (
            amount.get("currency_code") == order.currency
            and amount.get("value") == paypal.amount_str(order.amount)
            and order.mark_paid(resource.get("id", ""))
        ):
            emails.send_payment_confirmed(request, order)
            emails.notify_team(request, order, "paid")
    elif kind == "BILLING.SUBSCRIPTION.ACTIVATED" and order.package:
        if resource.get("plan_id") == order.package.paypal_plan_id and order.mark_paid(
            resource.get("id", "")
        ):
            emails.send_payment_confirmed(request, order)
            emails.notify_team(request, order, "paid")
    elif kind in {"PAYMENT.CAPTURE.DENIED", "PAYMENT.CAPTURE.DECLINED"}:
        Order.objects.filter(pk=order.pk).exclude(status=Order.Status.PAID).update(
            status=Order.Status.FAILED
        )
    elif kind == "PAYMENT.CAPTURE.REFUNDED":
        Order.objects.filter(pk=order.pk).update(status=Order.Status.REFUNDED)
    elif kind in {"BILLING.SUBSCRIPTION.CANCELLED", "BILLING.SUBSCRIPTION.EXPIRED"}:
        Order.objects.filter(pk=order.pk).update(status=Order.Status.CANCELLED)


@staff_member_required
def payment_proof(request, pk):
    """Staff-only view of an uploaded proof of payment."""
    if not request.user.has_perm("pricing.view_order"):
        raise Http404
    order = get_object_or_404(Order, pk=pk)
    if not order.proof_of_payment:
        raise Http404
    return private_file_response(order.proof_of_payment)
