from modeltranslation.translator import TranslationOptions, register

from .models import TemplateImage, TemplateIndustry, WebsiteTemplate


@register(TemplateIndustry)
class TemplateIndustryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(WebsiteTemplate)
class WebsiteTemplateTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "short_description",
        "description",
        "features",
        "pages",
        "seo_title",
        "seo_description",
    )


@register(TemplateImage)
class TemplateImageTranslationOptions(TranslationOptions):
    fields = ("caption",)
