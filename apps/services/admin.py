from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationStackedInline

from .models import Service, ServiceFAQ, ServiceGroup


@admin.register(ServiceGroup)
class ServiceGroupAdmin(TabbedTranslationAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name_en",)}


class ServiceFAQInline(TranslationStackedInline):
    model = ServiceFAQ
    extra = 0


@admin.register(Service)
class ServiceAdmin(TabbedTranslationAdmin):
    list_display = ("title", "group", "is_published", "order")
    list_editable = ("is_published", "order")
    list_filter = ("group", "is_published")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title_en",)}
    filter_horizontal = ("related_projects",)
    inlines = [ServiceFAQInline]
    fieldsets = (
        (None, {"fields": ("group", "title", "slug", "icon", "summary")}),
        ("Page content", {"fields": ("body", "benefits", "deliverables", "related_projects")}),
        ("Visibility", {"fields": ("is_published", "order")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )
