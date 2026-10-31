from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from modeltranslation.admin import TabbedTranslationAdmin

from .models import SiteSettings

admin.site.site_header = "Webmoris admin"
admin.site.site_title = "Webmoris admin"


@admin.register(SiteSettings)
class SiteSettingsAdmin(TabbedTranslationAdmin):
    fieldsets = (
        (None, {"fields": ("site_name", "tagline", "footer_about")}),
        (
            "Announcement bar",
            {"fields": ("announcement_enabled", "announcement_text", "announcement_link")},
        ),
        (
            "Stats counters",
            {"fields": ("stat_projects", "stat_years", "stat_clients", "stat_countries")},
        ),
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
        ("SEO defaults", {"fields": ("seo_title", "seo_description")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Skip the one-row list and go straight to the edit form.
        obj = SiteSettings.load()
        return redirect(reverse("admin:core_sitesettings_change", args=[obj.pk]))
