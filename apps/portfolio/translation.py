from modeltranslation.translator import TranslationOptions, register

from .models import Project, ProjectCategory, ProjectImage, ProjectMetric


@register(ProjectCategory)
class ProjectCategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "industry",
        "short_description",
        "services",
        "challenge",
        "solution",
        "results",
        "seo_title",
        "seo_description",
    )


@register(ProjectMetric)
class ProjectMetricTranslationOptions(TranslationOptions):
    fields = ("label",)


@register(ProjectImage)
class ProjectImageTranslationOptions(TranslationOptions):
    fields = ("caption",)
