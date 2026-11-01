from modeltranslation.translator import TranslationOptions, register

from .models import Package


@register(Package)
class PackageTranslationOptions(TranslationOptions):
    fields = ("name", "summary", "features")
