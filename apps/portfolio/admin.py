from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from .models import Project, ProjectCategory, ProjectImage, ProjectMetric


def preview(image_field, height=60):
    if not image_field:
        return "—"
    return format_html(
        '<img src="{}" style="height:{}px;border-radius:6px" alt="">', image_field.url, height
    )


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name_en",)}


class ProjectMetricInline(TranslationTabularInline):
    model = ProjectMetric
    extra = 0


class ProjectImageInline(TranslationTabularInline):
    model = ProjectImage
    extra = 0
    fields = ("thumb", "image", "kind", "caption", "order")
    readonly_fields = ("thumb",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        return preview(obj.image) if obj.pk else "—"


@admin.register(Project)
class ProjectAdmin(TabbedTranslationAdmin):
    list_display = ("cover", "title", "client", "year", "is_published", "is_featured", "order")
    list_display_links = ("cover", "title")
    list_editable = ("is_published", "is_featured", "order")
    list_filter = ("is_published", "is_featured", "categories", "year")
    search_fields = ("title", "client", "short_description")
    prepopulated_fields = {"slug": ("title_en",)}
    filter_horizontal = ("categories",)
    readonly_fields = ("cover_preview",)
    inlines = [ProjectMetricInline, ProjectImageInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "client", "industry", "year", "categories")}),
        ("Card", {"fields": ("short_description", "cover_image", "cover_preview")}),
        ("Case study", {"fields": ("services", "tech_stack", "challenge", "solution", "results")}),
        ("Links & video", {"fields": ("live_url", "video_url", "video_file")}),
        ("Visibility", {"fields": ("is_published", "is_featured", "order")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    @admin.display(description="")
    def cover(self, obj):
        return preview(obj.cover_image, height=40)

    @admin.display(description="Current cover")
    def cover_preview(self, obj):
        return preview(obj.cover_image, height=160)
