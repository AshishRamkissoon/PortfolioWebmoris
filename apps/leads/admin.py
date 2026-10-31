import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from . import views
from .models import QuoteRequest, TemplateInquiry

# Spreadsheet apps execute cells starting with these characters as formulas.
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def csv_safe(value):
    text = "" if value is None else str(value)
    return f"'{text}" if text.startswith(FORMULA_PREFIXES) else text


@admin.action(description="Export selected to CSV")
def export_csv(modeladmin, request, queryset):
    fields = modeladmin.csv_fields
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    stamp = timezone.localtime().strftime("%Y%m%d-%H%M")
    response["Content-Disposition"] = (
        f'attachment; filename="{modeladmin.model._meta.model_name}-{stamp}.csv"'
    )
    response.write("﻿")  # BOM so Excel opens UTF-8 (accents) correctly
    writer = csv.writer(response)
    writer.writerow(fields)
    for lead in queryset:
        row = []
        for field in fields:
            display = getattr(lead, f"get_{field}_display", None)
            row.append(csv_safe(display() if display else getattr(lead, field)))
        writer.writerow(row)
    return response


class LeadAdmin(admin.ModelAdmin):
    """Leads come from the website, so they can't be added here and what the visitor
    sent is read-only; staff only update the status and notes."""

    list_editable = ("status",)
    list_filter = ("status", "language", "created_at")
    date_hierarchy = "created_at"
    actions = [export_csv]
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        editable = {"status", "notes"}
        return [f.name for f in self.model._meta.fields if f.name not in editable | {"id"}] + list(
            self.extra_readonly
        )

    extra_readonly = ()


@admin.register(QuoteRequest)
class QuoteRequestAdmin(LeadAdmin):
    list_display = ("name", "email", "project_type", "budget", "timeline", "status", "created_at")
    list_filter = ("status", "project_type", "budget", "language", "created_at")
    search_fields = ("name", "email", "company", "message")
    extra_readonly = ("attachment_link",)
    fieldsets = (
        ("Pipeline", {"fields": ("status", "notes")}),
        ("Contact", {"fields": ("name", "email", "phone", "company", "language")}),
        (
            "Project",
            {"fields": ("project_type", "budget", "timeline", "message", "attachment_link")},
        ),
        ("Source", {"fields": ("source_page", "created_at")}),
    )
    csv_fields = [
        "created_at", "status", "name", "email", "phone", "company", "project_type",
        "budget", "timeline", "message", "language", "source_page", "notes",
    ]  # fmt: skip

    def get_urls(self):
        return [
            path(
                "<int:pk>/attachment/",
                self.admin_site.admin_view(views.quote_attachment),
                name="leads_quoterequest_attachment",
            )
        ] + super().get_urls()

    @admin.display(description="Attachment")
    def attachment_link(self, obj):
        if not obj.attachment:
            return "—"
        url = reverse("admin:leads_quoterequest_attachment", args=[obj.pk])
        return format_html('<a href="{}">Download</a>', url)


@admin.register(TemplateInquiry)
class TemplateInquiryAdmin(LeadAdmin):
    list_display = ("name", "email", "template_name", "business_name", "status", "created_at")
    list_filter = ("status", "template_name", "language", "created_at")
    search_fields = ("name", "email", "business_name", "message", "template_name")
    fieldsets = (
        ("Pipeline", {"fields": ("status", "notes")}),
        ("Contact", {"fields": ("name", "email", "phone", "business_name", "language")}),
        ("Enquiry", {"fields": ("template", "template_name", "message")}),
        ("Source", {"fields": ("source_page", "created_at")}),
    )
    csv_fields = [
        "created_at", "status", "name", "email", "phone", "business_name", "template_name",
        "message", "language", "source_page", "notes",
    ]  # fmt: skip
