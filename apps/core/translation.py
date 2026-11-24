from modeltranslation.translator import TranslationOptions, register

from .models import (
    FAQ,
    AboutPage,
    HeroBusiness,
    LegalPage,
    ProcessStep,
    SiteSettings,
    TeamMember,
    TrustPromise,
)


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = (
        "tagline",
        "footer_about",
        "announcement_text",
        "offer_title",
        "offer_text",
        "whatsapp_message",
        "seo_title",
        "seo_description",
        "hero_eyebrow",
        "hero_title",
        "hero_highlight",
        "hero_picker_label",
        "hero_cta_label",
        "hero_tags",
        "hero_badge_text",
        "promises_eyebrow",
        "promises_title",
        "promises_intro",
        "faq_eyebrow",
        "faq_title",
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


@register(HeroBusiness)
class HeroBusinessTranslationOptions(TranslationOptions):
    fields = ("label", "features")


@register(TrustPromise)
class TrustPromiseTranslationOptions(TranslationOptions):
    fields = ("title", "text")


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ("question", "answer")
