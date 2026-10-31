from modeltranslation.translator import TranslationOptions, register

from .models import AboutPage, LegalPage, ProcessStep, SiteSettings, TeamMember


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


@register(AboutPage)
class AboutPageTranslationOptions(TranslationOptions):
    fields = ("story_title", "story", "mission", "values")


@register(TeamMember)
class TeamMemberTranslationOptions(TranslationOptions):
    fields = ("role", "bio")


@register(ProcessStep)
class ProcessStepTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(LegalPage)
class LegalPageTranslationOptions(TranslationOptions):
    fields = ("title", "body")
