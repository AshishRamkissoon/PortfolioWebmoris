from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.uploads import RandomFilename, document_validators, private_storage
from apps.readymade.models import WebsiteTemplate


class LeadStatus(models.TextChoices):
    NEW = "new", _("New")
    CONTACTED = "contacted", _("Contacted")
    QUOTED = "quoted", _("Quoted")
    WON = "won", _("Won")
    LOST = "lost", _("Lost")


class Lead(models.Model):
    """Fields shared by every kind of enquiry."""

    name = models.CharField(_("name"), max_length=100)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone / WhatsApp"), max_length=30, blank=True)
    message = models.TextField(_("message"), max_length=5000)
    language = models.CharField(
        _("language"), max_length=8, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE
    )
    source_page = models.CharField(_("sent from page"), max_length=200, blank=True)

    status = models.CharField(
        _("status"), max_length=20, choices=LeadStatus.choices, default=LeadStatus.NEW
    )
    notes = models.TextField(_("internal notes"), blank=True)
    created_at = models.DateTimeField(_("received"), auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class QuoteRequest(Lead):
    class ProjectType(models.TextChoices):
        WEBSITE = "website", _("Website")
        ECOMMERCE = "ecommerce", _("Online store")
        BOOKING = "booking", _("Booking website")
        CARE = "care", _("Care plan (hosting & maintenance)")
        LANDING = "landing", _("Landing page")
        AI_MARKETING = "ai_marketing", _("AI marketing")
        READYMADE = "readymade", _("Ready-made website")
        BRANDING = "branding", _("Branding & print")
        PHOTO_VIDEO = "photo_video", _("Photo & video")
        OTHER = "other", _("Other")

    class Budget(models.TextChoices):
        UNDER_25K = "under_25k", _("Under MUR 25,000")
        FROM_25K = "25k_75k", _("MUR 25,000 – 75,000")
        FROM_75K = "75k_150k", _("MUR 75,000 – 150,000")
        OVER_150K = "over_150k", _("Over MUR 150,000")
        UNSURE = "unsure", _("Not sure yet")

    class Pages(models.TextChoices):
        ONE = "1", _("1 page")
        FEW = "2_5", _("2–5 pages")
        SEVERAL = "6_10", _("6–10 pages")
        MANY = "10_plus", _("More than 10 pages")
        UNSURE = "unsure", _("Not sure yet")

    # Brief checkboxes; stored as a comma-separated list of these keys.
    FEATURES = {
        "booking": _("Online booking"),
        "payments": _("Online payments"),
        "shop": _("Product catalogue / shop"),
        "blog": _("Blog or news"),
        "bilingual": _("English and French"),
        "whatsapp": _("WhatsApp button"),
        "forms": _("Contact / enquiry forms"),
        "gallery": _("Photo or video gallery"),
        "seo": _("SEO and Google setup"),
        "copywriting": _("Help writing the content"),
    }

    class Timeline(models.TextChoices):
        ASAP = "asap", _("As soon as possible")
        ONE_MONTH = "1_month", _("Within a month")
        ONE_TO_THREE = "1_3_months", _("In 1–3 months")
        FLEXIBLE = "flexible", _("Flexible")

    company = models.CharField(_("company"), max_length=120, blank=True)
    project_type = models.CharField(_("project type"), max_length=20, choices=ProjectType.choices)
    budget = models.CharField(_("budget"), max_length=20, choices=Budget.choices)
    timeline = models.CharField(_("timeline"), max_length=20, choices=Timeline.choices)

    # Project brief (all optional, so older enquiries and short forms still fit).
    package = models.ForeignKey(
        "pricing.Package",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_requests",
        verbose_name=_("package"),
    )
    industry = models.CharField(_("industry"), max_length=100, blank=True)
    current_website = models.URLField(_("current website"), blank=True)
    pages = models.CharField(_("number of pages"), max_length=10, choices=Pages.choices, blank=True)
    features = models.CharField(_("features"), max_length=300, blank=True)
    inspiration = models.TextField(_("websites you like"), max_length=1000, blank=True)
    starting_template = models.ForeignKey(
        WebsiteTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_requests",
        verbose_name=_("start from demo"),
    )
    attachment = models.FileField(
        _("attachment"),
        upload_to=RandomFilename("quotes"),
        storage=private_storage,
        validators=document_validators,
        blank=True,
        help_text=_("Optional brief or brand files: PDF, Word, images or ZIP, max 10 MB."),
    )

    class Meta(Lead.Meta):
        verbose_name = _("quote request")
        verbose_name_plural = _("quote requests")

    @property
    def feature_labels(self):
        return [str(self.FEATURES[key]) for key in self.features.split(",") if key in self.FEATURES]


class TemplateInquiry(Lead):
    template = models.ForeignKey(
        WebsiteTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inquiries",
        verbose_name=_("template"),
    )
    # Kept so the enquiry still makes sense if the template is later deleted.
    template_name = models.CharField(_("template name"), max_length=100)
    business_name = models.CharField(_("business name"), max_length=120, blank=True)

    class Meta(Lead.Meta):
        verbose_name = _("template enquiry")
        verbose_name_plural = _("template enquiries")
