"""Minimal PayPal REST client (Orders v2, Subscriptions v1, webhook verification).

Amounts always come from our database, never from the browser.
"""

import base64
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

API_BASE = {"sandbox": "https://api-m.sandbox.paypal.com", "live": "https://api-m.paypal.com"}
TOKEN_CACHE_KEY = "pricing:paypal:token"  # noqa: S105 (a cache key, not a secret)


class PayPalError(Exception):
    pass


def is_configured():
    return bool(settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET)


def _base_url():
    return API_BASE["live" if settings.PAYPAL_MODE == "live" else "sandbox"]


def _http(method, path, body=None, headers=None, form=False):
    url = f"{_base_url()}{path}"
    data = None
    if body is not None:
        data = body.encode() if form else json.dumps(body).encode()
    request = urllib.request.Request(url, data=data, method=method, headers=headers or {})  # noqa: S310
    try:
        with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310
            raw = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read()[:500].decode(errors="replace")
        logger.warning("PayPal %s %s failed: %s %s", method, path, error.code, detail)
        raise PayPalError(f"PayPal returned {error.code}") from error
    except OSError as error:
        raise PayPalError("PayPal is unreachable") from error
    return json.loads(raw) if raw else {}


def _access_token():
    token = cache.get(TOKEN_CACHE_KEY)
    if token:
        return token
    credentials = f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}"
    response = _http(
        "POST",
        "/v1/oauth2/token",
        "grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {base64.b64encode(credentials.encode()).decode()}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        form=True,
    )
    token = response["access_token"]
    cache.set(TOKEN_CACHE_KEY, token, max(60, int(response.get("expires_in", 3000)) - 120))
    return token


def _api(method, path, body=None, request_id=None):
    headers = {"Authorization": f"Bearer {_access_token()}", "Content-Type": "application/json"}
    if request_id:
        headers["PayPal-Request-Id"] = request_id  # makes retries idempotent on PayPal's side
    return _http(method, path, body, headers)


def amount_str(amount):
    return f"{amount:.2f}"


def create_order(order):
    """Create a PayPal order for ``order`` and return PayPal's order id."""
    response = _api(
        "POST",
        "/v2/checkout/orders",
        {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": order.reference,
                    "custom_id": order.reference,
                    "invoice_id": order.reference,
                    "description": order.package_name[:127],
                    "amount": {"currency_code": order.currency, "value": amount_str(order.amount)},
                }
            ],
            "payment_source": {
                "paypal": {"experience_context": {"shipping_preference": "NO_SHIPPING"}}
            },
        },
        request_id=f"create-{order.reference}-{order.access_token[:8]}",
    )
    return response["id"]


def capture_order(paypal_order_id):
    return _api(
        "POST",
        f"/v2/checkout/orders/{paypal_order_id}/capture",
        request_id=f"capture-{paypal_order_id}",
    )


def completed_capture(response, order):
    """The capture id if PayPal confirms the full amount for this order was paid, else None."""
    if response.get("status") != "COMPLETED":
        return None
    for unit in response.get("purchase_units", []):
        for capture in unit.get("payments", {}).get("captures", []):
            amount = capture.get("amount", {})
            if (
                capture.get("status") == "COMPLETED"
                and capture.get("custom_id", unit.get("custom_id")) == order.reference
                and amount.get("currency_code") == order.currency
                and amount.get("value") == amount_str(order.amount)
            ):
                return capture.get("id")
    return None


def get_subscription(subscription_id):
    return _api("GET", f"/v1/billing/subscriptions/{subscription_id}")


def subscription_is_active_for(subscription, order, plan_id):
    return (
        subscription.get("status") in {"ACTIVE", "APPROVED"}
        and subscription.get("plan_id") == plan_id
        and subscription.get("custom_id") == order.reference
    )


def verify_webhook(headers, event):
    """Ask PayPal whether this webhook delivery is genuine (signed for our webhook id)."""
    if not settings.PAYPAL_WEBHOOK_ID:
        return False
    try:
        response = _api(
            "POST",
            "/v1/notifications/verify-webhook-signature",
            {
                "auth_algo": headers.get("PAYPAL-AUTH-ALGO", ""),
                "cert_url": headers.get("PAYPAL-CERT-URL", ""),
                "transmission_id": headers.get("PAYPAL-TRANSMISSION-ID", ""),
                "transmission_sig": headers.get("PAYPAL-TRANSMISSION-SIG", ""),
                "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME", ""),
                "webhook_id": settings.PAYPAL_WEBHOOK_ID,
                "webhook_event": event,
            },
        )
    except PayPalError:
        return False
    return response.get("verification_status") == "SUCCESS"
