from django.contrib import admin, messages
from django.urls import path, reverse
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from apps.core.uploads import INLINE_IMAGE_EXTENSIONS

from . import emails, views
from .models import Order, Package, PaymentRequest, PayPalWebhookEvent


@admin.register(Package)
class PackageAdmin(TabbedTranslationAdmin):
    list_display = (
        "name",
        "billing",
        "price",
        "currency",
        "paypal_price",
        "paypal_currency",
        "is_purchasable",
        "is_popular",
        "is_published",
        "order",
    )
    list_editable = ("is_purchasable", "is_popular", "is_published", "order")
    list_filter = ("billing", "is_published")
    prepopulated_fields = {"slug": ("name_en",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "summary", "features", "billing")}),
        ("“From” price (optional)", {"fields": ("price", "currency")}),
        ("PayPal", {"fields": ("paypal_price", "paypal_currency", "paypal_plan_id")}),
        ("Visibility", {"fields": ("is_purchasable", "is_popular", "is_published", "order")}),
    )


@admin.action(description="Email the payment link to the client")
def email_payment_link(modeladmin, request, queryset):
    sent = sum(emails.send_payment_request(request, pr) for pr in queryset.filter(is_active=True))
    modeladmin.message_user(request, f"Payment link emailed to {sent} client(s).")


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    """Deposits and balances after a quote is agreed. Staff set the amount here; the client
    pays through a private link (PayPal / Juice / bank), and the result shows as an order."""

    list_display = (
        "reference",
        "description",
        "name",
        "amount",
        "currency",
        "status",
        "created_at",
    )
    list_filter = ("is_active", "currency", "created_at")
    search_fields = ("reference", "description", "name", "email", "company")
    actions = [email_payment_link]
    readonly_fields = ("reference", "pay_link", "status", "orders_list", "created_at")
    fieldsets = (
        (None, {"fields": ("description", "amount", "currency", "note")}),
        ("Client", {"fields": ("quote", "name", "email", "phone", "company", "language")}),
        ("PayPal (optional)", {"fields": ("paypal_amount", "paypal_currency")}),
        (
            "Link and status",
            {
                "fields": (
                    "is_active",
                    "reference",
                    "pay_link",
                    "status",
                    "orders_list",
                    "created_at",
                )
            },
        ),
    )

    def get_changeform_initial_data(self, request):
        """Opened from a quote request ("Create a payment request"): copy the client in."""
        initial = super().get_changeform_initial_data(request)
        from apps.leads.models import QuoteRequest

        quote = QuoteRequest.objects.filter(pk=request.GET.get("quote") or 0).first()
        if quote:
            what = quote.package.name if quote.package else quote.get_project_type_display()
            initial.update(
                quote=quote.pk,
                name=quote.name,
                email=quote.email,
                phone=quote.phone,
                company=quote.company,
                language=quote.language,
                description=f"50% deposit — {what}"[:80],
            )
        return initial

    @admin.display(description="Payment link")
    def pay_link(self, obj):
        if not obj.pk:
            return "Created when you save."
        url = obj.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank">Open the payment page</a><br>'
            '<span style="color:#888">Send it with the “Email the payment link” action, '
            "or open it and copy the address to share on WhatsApp.</span>",
            url,
        )

    @admin.display(description="Status")
    def status(self, obj):
        if not obj.pk:
            return "—"
        if obj.paid_order:
            return "Paid"
        if obj.orders.filter(status=Order.Status.PENDING_VERIFICATION).exists():
            return "Payment being verified"
        return "Awaiting payment" if obj.is_active else "Closed"

    @admin.display(description="Orders")
    def orders_list(self, obj):
        if not obj.pk or not obj.orders.exists():
            return "—"
        links = [
            format_html(
                '<a href="{}">{}</a> ({}, {})',
                reverse("admin:pricing_order_change", args=[order.pk]),
                order.reference,
                order.get_payment_method_display(),
                order.get_status_display(),
            )
            for order in obj.orders.all()
        ]
        return format_html("<br>".join(["{}"] * len(links)), *links)


@admin.action(description="Mark Juice / bank payment as verified and email the customer")
def mark_paid_verified(modeladmin, request, queryset):
    """Only manual payments are verified by staff; PayPal orders are confirmed by PayPal."""
    manual = queryset.filter(payment_method__in=[Order.Method.JUICE, Order.Method.BANK])
    done = 0
    for order in manual.exclude(status=Order.Status.PAID):
        if order.mark_paid():
            emails.send_payment_confirmed(request, order)
            done += 1
    skipped = queryset.count() - manual.count()
    note = f" {skipped} PayPal order(s) skipped." if skipped else ""
    modeladmin.message_user(request, f"{done} order(s) marked as paid.{note}", messages.SUCCESS)


@admin.action(description="Mark as cancelled")
def mark_cancelled(modeladmin, request, queryset):
    count = queryset.exclude(status=Order.Status.PAID).update(status=Order.Status.CANCELLED)
    modeladmin.message_user(request, f"{count} order(s) cancelled (paid orders are skipped).")


@admin.action(description="Mark as refunded")
def mark_refunded(modeladmin, request, queryset):
    count = queryset.filter(status=Order.Status.PAID).update(status=Order.Status.REFUNDED)
    modeladmin.message_user(request, f"{count} paid order(s) marked as refunded.")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Orders come from checkout; staff change their state only through the actions above,
    so "paid" always goes with a confirmation email and is never set by accident."""

    list_display = (
        "reference",
        "package_name",
        "name",
        "email",
        "payment_method",
        "amount",
        "currency",
        "status",
        "created_at",
    )
    list_filter = ("status", "payment_method", "billing", "created_at")
    search_fields = ("reference", "name", "email", "company", "transaction_ref")
    date_hierarchy = "created_at"
    actions = [mark_paid_verified, mark_cancelled, mark_refunded]
    fieldsets = (
        (
            "Order",
            {
                "fields": (
                    "reference",
                    "status",
                    "package_name",
                    "payment_request",
                    "billing",
                    "amount",
                    "currency",
                )
            },  # fmt: skip
        ),
        (
            "Customer",
            {"fields": ("name", "email", "phone", "company", "notes_from_customer", "language")},
        ),
        (
            "Payment",
            {
                "fields": (
                    "payment_method",
                    "transaction_ref",
                    "proof_preview",
                    "paypal_order_id",
                    "paypal_subscription_id",
                    "paid_at",
                )
            },
        ),
        ("Internal", {"fields": ("admin_notes", "created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in Order._meta.fields if f.name not in {"id", "admin_notes"}] + [
            "proof_preview"
        ]

    def get_urls(self):
        return [
            path(
                "<int:pk>/proof/",
                self.admin_site.admin_view(views.payment_proof),
                name="pricing_order_proof",
            )
        ] + super().get_urls()

    @admin.display(description="Proof of payment")
    def proof_preview(self, obj):
        if not obj.proof_of_payment:
            return "—"
        url = reverse("admin:pricing_order_proof", args=[obj.pk])
        if any(obj.proof_of_payment.name.lower().endswith(ext) for ext in INLINE_IMAGE_EXTENSIONS):
            style = "max-height:320px;border-radius:8px"
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="{}" alt=""></a>', url, url, style
            )
        return format_html('<a href="{}">Download</a>', url)


@admin.register(PayPalWebhookEvent)
class PayPalWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "event_id", "received_at")
    list_filter = ("event_type",)
    search_fields = ("event_id",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
