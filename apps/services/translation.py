from modeltranslation.translator import TranslationOptions, register

from .models import Service, ServiceFAQ, ServiceGroup


@register(ServiceGroup)
class ServiceGroupTranslationOptions(TranslationOptions):
    fields = ("name", "intro")


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "summary",
        "body",
        "benefits",
        "deliverables",
        "seo_title",
        "seo_description",
    )


@register(ServiceFAQ)
class ServiceFAQTranslationOptions(TranslationOptions):
    fields = ("question", "answer")
