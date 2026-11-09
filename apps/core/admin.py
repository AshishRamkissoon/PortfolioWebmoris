from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import AboutPage, HeroBusiness, LegalPage, ProcessStep, SiteSettings, TeamMember

admin.site.site_header = "Webmoris admin"
admin.site.site_title = "Webmoris admin"


def image_preview(image_field, height=60):
    """Small thumbnail for admin lists and forms."""
    if not image_field:
        return "—"
    return format_html(
        '<img src="{}" style="height:{}px;border-radius:6px" alt="">', image_field.url, height
    )


class SingletonAdminMixin:
    """Admin for one-row models: no add/delete, and the list goes straight to the edit form."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        opts = self.model._meta
        return redirect(reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk]))


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdminMixin, TabbedTranslationAdmin):
    fieldsets = (
        (None, {"fields": ("site_name", "tagline", "footer_about")}),
        (
            "Announcement bar",
            {"fields": ("announcement_enabled", "announcement_text", "announcement_link")},
        ),
        ("Launch offer", {"fields": ("offer_enabled", "offer_title", "offer_text")}),
        ("WhatsApp & booking", {"fields": ("whatsapp_number", "whatsapp_message", "calendly_url")}),
        ("Contact", {"fields": ("contact_email", "contact_phone", "address")}),
        (
            "Social links",
            {
                "fields": (
                    "facebook_url",
                    "instagram_url",
                    "linkedin_url",
                    "tiktok_url",
                    "youtube_url",
                )
            },
        ),
        ("SEO defaults", {"fields": ("seo_title", "seo_description", "og_image")}),
        (
            "Payments (MCB Juice & bank transfer)",
            {"fields": ("juice_number", "juice_account_name", "juice_qr", "bank_details")},
        ),
    )


@admin.register(AboutPage)
class AboutPageAdmin(SingletonAdminMixin, TabbedTranslationAdmin):
    fields = ("story_title", "story", "mission", "values", "tools")


@admin.register(TeamMember)
class TeamMemberAdmin(TabbedTranslationAdmin):
    list_display = ("photo_thumb", "name", "role", "is_active", "order")
    list_display_links = ("photo_thumb", "name")
    list_editable = ("is_active", "order")
    readonly_fields = ("photo_thumb",)
    fields = ("name", "role", "bio", "photo", "photo_thumb", "linkedin_url", "is_active", "order")

    @admin.display(description="Photo")
    def photo_thumb(self, obj):
        if not obj.photo:
            return "—"
        style = "height:48px;width:48px;object-fit:cover;border-radius:50%"
        return format_html('<img src="{}" style="{}" alt="">', obj.photo.url, style)


@admin.register(ProcessStep)
class ProcessStepAdmin(TabbedTranslationAdmin):
    list_display = ("title", "description", "order")
    list_editable = ("order",)


@admin.register(LegalPage)
class LegalPageAdmin(TabbedTranslationAdmin):
    list_display = ("title", "kind", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(HeroBusiness)
class HeroBusinessAdmin(TabbedTranslationAdmin):
    list_display = ("label", "package", "template", "is_active", "order")
    list_editable = ("is_active", "order")
    prepopulated_fields = {"slug": ("label_en",)}
    fields = (
        "label",
        "slug",
        "features",
        "package",
        "template",
        "project_type",
        "is_active",
        "order",
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "project_type":
            # Same choices as the brief; imported here to keep core free of a leads import cycle.
            from django import forms

            from apps.leads.models import QuoteRequest

            return forms.ChoiceField(
                choices=QuoteRequest.ProjectType.choices,
                label=db_field.verbose_name,
                help_text=db_field.help_text,
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)
