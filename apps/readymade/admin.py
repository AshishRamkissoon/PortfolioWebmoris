from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from apps.core.admin import image_preview as preview

from .models import TemplateImage, TemplateIndustry, WebsiteTemplate


@admin.register(TemplateIndustry)
class TemplateIndustryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name_en",)}


class TemplateImageInline(TranslationTabularInline):
    model = TemplateImage
    extra = 0
    fields = ("thumb", "image", "caption", "order")
    readonly_fields = ("thumb",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        return preview(obj.image) if obj.pk else "—"


@admin.register(WebsiteTemplate)
class WebsiteTemplateAdmin(TabbedTranslationAdmin):
    list_display = (
        "cover",
        "name",
        "industry",
        "starting_price",
        "currency",
        "status",
        "is_published",
        "is_featured",
        "order",
    )
    list_display_links = ("cover", "name")
    list_editable = ("status", "is_published", "is_featured", "order")
    list_filter = ("status", "is_published", "is_featured", "industry")
    search_fields = ("name", "short_description")
    prepopulated_fields = {"slug": ("name_en",)}
    readonly_fields = ("cover_preview",)
    inlines = [TemplateImageInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "industry", "status")}),
        ("Card", {"fields": ("short_description", "cover_image", "cover_preview")}),
        ("Price", {"fields": ("starting_price", "currency")}),
        ("Details", {"fields": ("description", "features", "pages", "demo_url", "video_url")}),
        ("Visibility", {"fields": ("is_published", "is_featured", "order")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    @admin.display(description="")
    def cover(self, obj):
        return preview(obj.cover_image, height=40)

    @admin.display(description="Current cover")
    def cover_preview(self, obj):
        return preview(obj.cover_image, height=160)
