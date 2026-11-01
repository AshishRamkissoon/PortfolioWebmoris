import json
from decimal import Decimal
from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from apps.core.models import SiteSettings
from apps.pricing import paypal
from apps.pricing.models import Order, Package, PayPalWebhookEvent

pytestmark = pytest.mark.django_db


# --- Fixtures -------------------------------------------------------------------


@pytest.fixture(autouse=True)
def payment_settings():
    obj = SiteSettings.load()
    obj.contact_email = "team@webmoris.test"
    obj.juice_number = "5123 4567"
    obj.bank_details = "Bank: Test\nAccount: 123"
    obj.save()
    return obj


@pytest.fixture
def paypal_on(settings):
    settings.PAYPAL_CLIENT_ID = "client-id"
    settings.PAYPAL_CLIENT_SECRET = "secret"
    settings.PAYPAL_WEBHOOK_ID = "WH-1"


def make_package(**kwargs):
    defaults = {
        "name": "Business Website",
        "slug": "business",
        "summary": "Complete site.",
        "price": Decimal("60000"),
        "paypal_price": Decimal("1300"),
    }
    return Package.objects.create(**{**defaults, **kwargs})


def make_order(package=None, **kwargs):
    package = package or make_package()
    defaults = {
        "package": package,
        "package_name": package.name,
        "billing": package.billing,
        "name": "Jane",
        "email": "jane@example.com",
        "payment_method": Order.Method.PAYPAL,
        "amount": package.paypal_price or package.price,
        "currency": package.paypal_currency if package.paypal_price else package.currency,
    }
    return Order.objects.create(**{**defaults, **kwargs})


def checkout_data(**overrides):
    data = {"name": "Jane", "email": "jane@example.com", "payment_method": "juice", "website": ""}
    return {**data, **overrides}


def capture_response(order, status="COMPLETED", value=None):
    return {
        "status": status,
        "purchase_units": [
            {
                "custom_id": order.reference,
                "payments": {
                    "captures": [
                        {
                            "id": "CAP-1",
                            "status": status,
                            "custom_id": order.reference,
                            "amount": {
                                "currency_code": order.currency,
                                "value": value or paypal.amount_str(order.amount),
                            },
                        }
                    ]
                },
            }
        ],
    }


# --- Packages & listing -----------------------------------------------------------


def test_paypal_availability(settings):
    package = make_package()
    assert package.accepts_paypal and not package.paypal_available  # credentials missing
    settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET = "id", "secret"
    assert package.paypal_available

    monthly = make_package(slug="m", billing="monthly")
    assert not monthly.accepts_paypal  # needs a plan id
    with pytest.raises(ValidationError):
        monthly.full_clean()


def test_pricing_page(client):
    make_package()
    make_package(slug="chatbot", name="Chatbot", is_purchasable=False)
    make_package(slug="social", name="Social", billing="monthly", paypal_price=None)
    make_package(slug="hidden", name="Hidden", is_published=False)
    response = client.get("/en/pricing/")
    content = response.content.decode()
    assert [p.slug for p in response.context["one_off"]] == ["business", "chatbot"]
    assert [p.slug for p in response.context["monthly"]] == ["social"]
    assert "Hidden" not in content
    assert "/en/pricing/business/checkout/" in content
    assert "Request a quote" in content
    assert "MUR 60,000" in content


def test_checkout_requires_purchasable_published_package(client):
    make_package(slug="quote-only", is_purchasable=False)
    make_package(slug="draft", is_published=False)
    assert client.get("/en/pricing/quote-only/checkout/").status_code == 404
    assert client.get("/en/pricing/draft/checkout/").status_code == 404


def test_checkout_offers_only_available_methods(client, paypal_on, payment_settings):
    make_package()
    methods = client.get("/en/pricing/business/checkout/").context["methods"]
    assert methods == ["paypal", "juice", "bank"]

    payment_settings.juice_number = ""
    payment_settings.bank_details = ""
    payment_settings.save()
    make_package(slug="no-paypal", paypal_price=None)
    response = client.get("/en/pricing/no-paypal/checkout/")
    assert response.context["methods"] == []
    assert "Online payment isn't available for this package yet." in response.content.decode()


# --- Creating orders ---------------------------------------------------------------


def test_manual_order_uses_server_price_and_sends_instructions(client):
    make_package()
    response = client.post(
        "/fr/pricing/business/checkout/",
        checkout_data(amount="1", currency="USD", status="paid"),  # tampering is ignored
    )
    order = Order.objects.get()
    assert response.status_code == 302 and response["Location"] == order.get_absolute_url()
    assert (order.amount, order.currency) == (Decimal("60000.00"), "MUR")
    assert order.status == Order.Status.PENDING
    assert order.language == "fr"
    assert order.reference.startswith("WM-") and len(order.access_token) >= 30

    customer, team = mail.outbox
    assert customer.to == ["jane@example.com"]
    assert "5123 4567" in customer.body and order.reference in customer.body
    assert order.get_absolute_url() in customer.body
    assert team.to == ["team@webmoris.test"] and "awaiting payment" in team.subject


def test_paypal_order_uses_paypal_price_and_sends_nothing_yet(client, paypal_on):
    make_package()
    client.post("/en/pricing/business/checkout/", checkout_data(payment_method="paypal"))
    order = Order.objects.get()
    assert (order.amount, order.currency) == (Decimal("1300.00"), "USD")
    assert not mail.outbox


def test_paypal_not_selectable_when_not_configured(client):
    make_package()
    response = client.post("/en/pricing/business/checkout/", checkout_data(payment_method="paypal"))
    assert "payment_method" in response.context["form"].errors
    assert not Order.objects.exists()


def test_checkout_honeypot_and_rate_limit(client, settings):
    make_package()
    client.post("/en/pricing/business/checkout/", checkout_data(website="spam"))
    assert not Order.objects.exists()

    settings.LEADS_RATE_LIMIT = 1
    client.post("/en/pricing/business/checkout/", checkout_data())
    response = client.post("/en/pricing/business/checkout/", checkout_data())
    assert "Too many orders" in response.content.decode()
    assert Order.objects.count() == 1


# --- Order page & manual payment ---------------------------------------------------


def test_order_page_needs_the_secret_token(client):
    order = make_order(payment_method="juice", amount=60000, currency="MUR")
    assert client.get(f"/en/pricing/order/{order.reference}/").status_code == 404
    response = client.get(order.get_absolute_url())
    assert response.status_code == 200
    assert "no-store" in response["Cache-Control"] or "max-age=0" in response["Cache-Control"]
    assert "5123 4567" in response.content.decode()


def test_proof_upload_moves_order_to_verification(client, settings):
    order = make_order(payment_method="juice", amount=60000, currency="MUR")
    proof = SimpleUploadedFile("receipt.png", b"\x89PNG fake", content_type="image/png")
    response = client.post(order.get_absolute_url(), {"proof_of_payment": proof})
    assert response.status_code == 302
    order.refresh_from_db()
    assert order.status == Order.Status.PENDING_VERIFICATION
    assert str(settings.PRIVATE_MEDIA_ROOT) in order.proof_of_payment.path
    assert "receipt" not in order.proof_of_payment.name
    assert mail.outbox[-1].to == ["team@webmoris.test"] and "verify" in mail.outbox[-1].subject


def test_proof_needs_reference_or_file_and_rejects_bad_files(client):
    order = make_order(payment_method="bank", amount=60000, currency="MUR")
    response = client.post(order.get_absolute_url(), {})
    assert "transaction reference" in response.content.decode()

    bad = SimpleUploadedFile("x.html", b"<script>", content_type="text/html")
    response = client.post(order.get_absolute_url(), {"proof_of_payment": bad})
    assert "proof_of_payment" in response.context["proof_form"].errors
    order.refresh_from_db()
    assert order.status == Order.Status.PENDING


# --- PayPal one-off ----------------------------------------------------------------


def test_paypal_create_stores_paypal_order_id(client, paypal_on):
    order = make_order()
    with mock.patch.object(paypal, "create_order", return_value="PP-123") as create:
        response = client.post(f"{order.get_absolute_url()}paypal/create/")
    assert response.json() == {"id": "PP-123"}
    create.assert_called_once()
    order.refresh_from_db()
    assert order.paypal_order_id == "PP-123"
    assert client.get(f"{order.get_absolute_url()}paypal/create/").status_code == 405


def test_paypal_endpoints_reject_other_orders(client, paypal_on):
    order = make_order(payment_method="juice", amount=60000, currency="MUR")
    assert client.post(f"{order.get_absolute_url()}paypal/create/").status_code == 404


def test_capture_marks_paid_once_and_emails(client, paypal_on):
    order = make_order(paypal_order_id="PP-123")
    with mock.patch.object(paypal, "capture_order", return_value=capture_response(order)) as cap:
        response = client.post(
            f"{order.get_absolute_url()}paypal/capture/",
            data=json.dumps({"orderID": "ATTACKER-ORDER"}),
            content_type="application/json",
        )
        cap.assert_called_once_with("PP-123")  # the id from our DB, not the browser
        assert response.json()["status"] == "paid"
        client.post(f"{order.get_absolute_url()}paypal/capture/")  # double click
    order.refresh_from_db()
    assert order.is_paid and order.transaction_ref == "CAP-1" and order.paid_at
    assert len(mail.outbox) == 2  # customer + team, once


@pytest.mark.parametrize(
    "response_kwargs",
    [{"status": "PENDING"}, {"value": "1.00"}],
    ids=["not-completed", "wrong-amount"],
)
def test_capture_refuses_incomplete_or_wrong_amount(client, paypal_on, response_kwargs):
    order = make_order(paypal_order_id="PP-123")
    with mock.patch.object(
        paypal, "capture_order", return_value=capture_response(order, **response_kwargs)
    ):
        response = client.post(f"{order.get_absolute_url()}paypal/capture/")
    assert response.status_code == 402
    order.refresh_from_db()
    assert not order.is_paid


def test_capture_when_paypal_down(client, paypal_on):
    order = make_order(paypal_order_id="PP-123")
    with mock.patch.object(paypal, "capture_order", side_effect=paypal.PayPalError("down")):
        assert client.post(f"{order.get_absolute_url()}paypal/capture/").status_code == 502


# --- PayPal subscriptions ----------------------------------------------------------


@pytest.fixture
def monthly_order(paypal_on):
    package = make_package(slug="social", billing="monthly", paypal_price=175, paypal_plan_id="P-1")
    return make_order(package)


def test_subscription_verified_with_paypal(client, monthly_order):
    subscription = {"status": "ACTIVE", "plan_id": "P-1", "custom_id": monthly_order.reference}
    with mock.patch.object(paypal, "get_subscription", return_value=subscription):
        response = client.post(
            f"{monthly_order.get_absolute_url()}paypal/subscription/",
            data=json.dumps({"subscriptionID": "I-ABC123"}),
            content_type="application/json",
        )
    assert response.json()["status"] == "paid"
    monthly_order.refresh_from_db()
    assert monthly_order.is_paid and monthly_order.paypal_subscription_id == "I-ABC123"


@pytest.mark.parametrize(
    "subscription",
    [{"status": "ACTIVE", "plan_id": "P-OTHER"}, {"status": "CANCELLED", "plan_id": "P-1"}],
    ids=["other-plan", "inactive"],
)
def test_subscription_rejected_when_not_ours(client, monthly_order, subscription):
    subscription["custom_id"] = monthly_order.reference
    with mock.patch.object(paypal, "get_subscription", return_value=subscription):
        response = client.post(
            f"{monthly_order.get_absolute_url()}paypal/subscription/",
            data=json.dumps({"subscriptionID": "I-ABC123"}),
            content_type="application/json",
        )
    assert response.status_code == 402
    monthly_order.refresh_from_db()
    assert not monthly_order.is_paid


def test_subscription_id_format_checked(client, monthly_order):
    response = client.post(
        f"{monthly_order.get_absolute_url()}paypal/subscription/",
        data=json.dumps({"subscriptionID": "../../v1/x"}),
        content_type="application/json",
    )
    assert response.status_code == 400


# --- Webhooks ----------------------------------------------------------------------

WEBHOOK = "/payments/paypal/webhook/"


def post_event(event, verified=True):
    client = Client(enforce_csrf_checks=True)  # PayPal can't send a CSRF token
    with mock.patch.object(paypal, "verify_webhook", return_value=verified):
        return client.post(WEBHOOK, data=json.dumps(event), content_type="application/json")


def capture_event(order, event_id="WH-EVT-1", value=None, kind="PAYMENT.CAPTURE.COMPLETED"):
    return {
        "id": event_id,
        "event_type": kind,
        "resource": {
            "id": "CAP-9",
            "custom_id": order.reference,
            "amount": {
                "currency_code": order.currency,
                "value": value or paypal.amount_str(order.amount),
            },
        },
    }


def test_unverified_webhook_rejected(paypal_on):
    order = make_order()
    assert post_event(capture_event(order), verified=False).status_code == 400
    order.refresh_from_db()
    assert not order.is_paid
    assert not PayPalWebhookEvent.objects.exists()


def test_webhook_marks_paid_once(paypal_on):
    order = make_order()
    assert post_event(capture_event(order)).status_code == 200
    assert post_event(capture_event(order)).status_code == 200  # re-delivery
    order.refresh_from_db()
    assert order.is_paid and order.transaction_ref == "CAP-9"
    assert len(mail.outbox) == 2
    assert PayPalWebhookEvent.objects.count() == 1


def test_webhook_wrong_amount_ignored(paypal_on):
    order = make_order()
    post_event(capture_event(order, value="1.00"))
    order.refresh_from_db()
    assert not order.is_paid


@pytest.mark.parametrize(
    ("kind", "status"),
    [
        ("PAYMENT.CAPTURE.DENIED", Order.Status.FAILED),
        ("PAYMENT.CAPTURE.REFUNDED", Order.Status.REFUNDED),
        ("BILLING.SUBSCRIPTION.CANCELLED", Order.Status.CANCELLED),
    ],
)
def test_webhook_status_changes(paypal_on, kind, status):
    order = make_order()
    post_event(capture_event(order, kind=kind))
    order.refresh_from_db()
    assert order.status == status


def test_webhook_rejects_garbage(paypal_on):
    client = Client()
    assert client.post(WEBHOOK, data="not json", content_type="application/json").status_code == 400
    assert client.get(WEBHOOK).status_code == 405


# --- PayPal client helpers -----------------------------------------------------------


def test_completed_capture_checks_everything():
    order = make_order()
    assert paypal.completed_capture(capture_response(order), order) == "CAP-1"
    other = capture_response(order)
    other["purchase_units"][0]["payments"]["captures"][0]["custom_id"] = "WM-OTHER"
    assert paypal.completed_capture(other, order) is None


def test_verify_webhook_without_webhook_id_fails_closed(settings):
    settings.PAYPAL_WEBHOOK_ID = ""
    assert paypal.verify_webhook({}, {}) is False


# --- Admin ---------------------------------------------------------------------------


@pytest.fixture
def admin_client(client):
    client.force_login(get_user_model().objects.create_superuser("o", "o@x.com", "pw-123456789"))
    return client


def test_admin_marks_manual_payments_only(admin_client):
    package = make_package()
    juice = make_order(package, payment_method="juice", amount=60000, currency="MUR")
    paypal_order = make_order(package, payment_method="paypal")
    url = f"/{settings.ADMIN_URL}pricing/order/"
    admin_client.post(
        url, {"action": "mark_paid_verified", "_selected_action": [juice.pk, paypal_order.pk]}
    )
    juice.refresh_from_db()
    paypal_order.refresh_from_db()
    assert juice.is_paid and not paypal_order.is_paid
    assert [m.to for m in mail.outbox] == [["jane@example.com"]]
    assert admin_client.get(f"{url}add/").status_code == 403
    assert admin_client.get(f"{url}{juice.pk}/change/").status_code == 200


def test_proof_view_is_staff_only(client, admin_client):
    order = make_order(payment_method="juice", amount=60000, currency="MUR")
    order.proof_of_payment = SimpleUploadedFile("r.png", b"\x89PNG")
    order.save()
    url = f"/{settings.ADMIN_URL}pricing/order/{order.pk}/proof/"
    assert Client().get(url).status_code == 302
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "attachment" not in response.get("Content-Disposition", "")  # images preview inline


def test_private_files_have_no_public_url():
    order = make_order(payment_method="juice", amount=60000, currency="MUR")
    order.proof_of_payment = SimpleUploadedFile("r.png", b"\x89PNG")
    order.save()
    with pytest.raises(ValueError):
        order.proof_of_payment.url  # noqa: B018


# --- Home & seed -----------------------------------------------------------------------


def test_home_shows_pricing_teaser(client):
    make_package(is_popular=True)
    content = client.get("/en/").content.decode()
    assert "Business Website" in content and "Most popular" in content


def test_seed_demo_pricing():
    from io import StringIO

    from django.core.management import call_command

    call_command("seed_demo", stdout=StringIO())
    call_command("seed_demo", stdout=StringIO())
    assert Package.objects.count() == 4
    assert not Package.objects.get(slug="ai-chatbot-setup").is_purchasable
    # Demo payment details never overwrite real ones (the fixture set a real number).
    assert SiteSettings.load().juice_number == "5123 4567"
