import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.uploads import RandomFilename, document_validators, private_storage
from apps.readymade.models import Currency


class PayPalCurrency(models.TextChoices):
    """PayPal does not support MUR, so PayPal prices use one of these."""

    USD = "USD", "USD ($)"
    EUR = "EUR", "EUR (€)"


class PackageQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Package(models.Model):
    class Billing(models.TextChoices):
        ONE_OFF = "one_off", _("One-off")
        MONTHLY = "monthly", _("Monthly")

    name = models.CharField(_("name"), max_length=80)
    slug = models.SlugField(_("slug"), unique=True)
    summary = models.CharField(_("summary"), max_length=200)
    features = models.TextField(_("features"), blank=True, help_text=_("One per line."))
    billing = models.CharField(
        _("billing"), max_length=10, choices=Billing.choices, default=Billing.ONE_OFF
    )

    price = models.DecimalField(
        _("price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(1)]
    )
    currency = models.CharField(
        _("currency"), max_length=3, choices=Currency.choices, default=Currency.MUR
    )
    paypal_price = models.DecimalField(
        _("PayPal price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text=_("PayPal can't charge in MUR. Leave empty to hide PayPal for this package."),
    )
    paypal_currency = models.CharField(
        _("PayPal currency"),
        max_length=3,
        choices=PayPalCurrency.choices,
        default=PayPalCurrency.USD,
    )
    paypal_plan_id = models.CharField(
        _("PayPal plan ID"),
        max_length=50,
        blank=True,
        help_text=_("Monthly packages only: the billing plan ID (P-…) created in PayPal."),
    )

    is_purchasable = models.BooleanField(
        _("can be bought online"),
        default=True,
        help_text=_("Untick to show “Request a quote” instead of “Buy”."),
    )
    is_popular = models.BooleanField(_("highlight as popular"), default=False)
    is_published = models.BooleanField(_("published"), default=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    objects = PackageQuerySet.as_manager()

    class Meta:
        ordering = ["order", "price"]
        verbose_name = _("package")
        verbose_name_plural = _("packages")

    def __str__(self):
        return self.name

    def clean(self):
        if self.billing == self.Billing.MONTHLY and self.paypal_price and not self.paypal_plan_id:
            raise ValidationError(
                {"paypal_plan_id": _("Monthly packages need a PayPal plan ID to use PayPal.")}
            )

    def get_checkout_url(self):
        return reverse("pricing:checkout", kwargs={"slug": self.slug})

    @property
    def is_monthly(self):
        return self.billing == self.Billing.MONTHLY

    @property
    def accepts_paypal(self):
        """The package has what PayPal needs (a price, and a plan for monthly billing)."""
        return bool(self.paypal_price and (not self.is_monthly or self.paypal_plan_id))

    @property
    def paypal_available(self):
        """PayPal can be offered right now: package ready and PayPal credentials configured."""
        from . import paypal

        return self.accepts_paypal and paypal.is_configured()


def _new_reference():
    alphabet = string.ascii_uppercase + string.digits
    return "WM-" + "".join(secrets.choice(alphabet) for _ in range(7))


def _new_token():
    return secrets.token_urlsafe(24)


class Order(models.Model):
    class Method(models.TextChoices):
        PAYPAL = "paypal", "PayPal"
        JUICE = "juice", "MCB Juice"
        BANK = "bank", _("Bank transfer")

    class Status(models.TextChoices):
        PENDING = "pending", _("Awaiting payment")
        PENDING_VERIFICATION = "pending_verification", _("Payment being verified")
        PAID = "paid", _("Paid")
        FAILED = "failed", _("Failed")
        CANCELLED = "cancelled", _("Cancelled")
        REFUNDED = "refunded", _("Refunded")

    # Shown to the customer (emails, bank transfer reference)…
    reference = models.CharField(_("reference"), max_length=12, unique=True, default=_new_reference)
    # …while the order page URL uses an unguessable token, so orders can't be enumerated.
    access_token = models.CharField(max_length=40, unique=True, default=_new_token, editable=False)

    package = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="orders", verbose_name=_("package")
    )
    package_name = models.CharField(_("package name"), max_length=80)
    billing = models.CharField(_("billing"), max_length=10, choices=Package.Billing.choices)

    name = models.CharField(_("name"), max_length=100)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone / WhatsApp"), max_length=30, blank=True)
    company = models.CharField(_("company"), max_length=120, blank=True)
    notes_from_customer = models.TextField(_("notes"), max_length=2000, blank=True)
    language = models.CharField(
        _("language"), max_length=8, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE
    )

    payment_method = models.CharField(_("payment method"), max_length=10, choices=Method.choices)
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("currency"), max_length=3)
    status = models.CharField(
        _("status"), max_length=25, choices=Status.choices, default=Status.PENDING
    )

    paypal_order_id = models.CharField(max_length=50, blank=True, db_index=True)
    paypal_subscription_id = models.CharField(max_length=50, blank=True, db_index=True)
    transaction_ref = models.CharField(_("transaction reference"), max_length=100, blank=True)
    proof_of_payment = models.FileField(
        _("proof of payment"),
        upload_to=RandomFilename("payments"),
        storage=private_storage,
        validators=document_validators,
        blank=True,
    )
    admin_notes = models.TextField(_("internal notes"), blank=True)

    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)
    paid_at = models.DateTimeField(_("paid at"), null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return f"{self.reference} — {self.package_name}"

    def get_absolute_url(self):
        return reverse("pricing:order", kwargs={"token": self.access_token})

    @property
    def is_paid(self):
        return self.status == self.Status.PAID

    @property
    def is_manual(self):
        return self.payment_method in (self.Method.JUICE, self.Method.BANK)

    @property
    def awaiting_payment(self):
        return self.status in (self.Status.PENDING, self.Status.FAILED)

    def mark_paid(self, transaction_ref=""):
        """Mark as paid exactly once, even if the browser and a PayPal webhook race.

        A single conditional UPDATE decides the winner; returns True only for it, so
        confirmation emails are sent once.
        """
        now = timezone.now()
        changes = {"status": self.Status.PAID, "paid_at": now, "updated_at": now}
        if transaction_ref:
            changes["transaction_ref"] = transaction_ref
        won = (
            Order.objects.filter(pk=self.pk).exclude(status=self.Status.PAID).update(**changes) == 1
        )
        self.refresh_from_db()
        return won


class PayPalWebhookEvent(models.Model):
    """Every processed PayPal webhook, so a re-delivered event is never applied twice."""

    event_id = models.CharField(max_length=60, unique=True)
    event_type = models.CharField(max_length=60)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at"]
        verbose_name = _("PayPal webhook event")
        verbose_name_plural = _("PayPal webhook events")

    def __str__(self):
        return f"{self.event_type} ({self.event_id})"
