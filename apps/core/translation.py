from modeltranslation.translator import TranslationOptions, register

from .models import SiteSettings


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = (
        "tagline",
        "footer_about",
        "announcement_text",
        "whatsapp_message",
        "seo_title",
        "seo_description",
    )
