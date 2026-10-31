from urllib.parse import quote

from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from .booking import validate_booking_url
from .uploads import RandomFilename, image_validators

whatsapp_validator = RegexValidator(
    r"^[1-9]\d{6,14}$",
    _("International format, digits only, no + or spaces (e.g. 23057123456)."),
)


class SingletonModel(models.Model):
    """A model with exactly one row (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # the single row is never deleted

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    site_name = models.CharField(_("site name"), max_length=100, default="Webmoris")
    tagline = models.CharField(_("tagline"), max_length=200, blank=True)
    footer_about = models.TextField(_("footer about text"), blank=True)

    announcement_enabled = models.BooleanField(_("show announcement bar"), default=False)
    announcement_text = models.CharField(_("announcement text"), max_length=200, blank=True)
    announcement_link = models.URLField(_("announcement link"), blank=True)

    stat_projects = models.PositiveIntegerField(_("projects delivered"), default=0)
    stat_years = models.PositiveIntegerField(_("years of experience"), default=0)
    stat_clients = models.PositiveIntegerField(_("happy clients"), default=0)
    stat_countries = models.PositiveIntegerField(_("countries served"), default=0)

    whatsapp_number = models.CharField(
        _("WhatsApp number"), max_length=15, blank=True, validators=[whatsapp_validator]
    )
    whatsapp_message = models.CharField(
        _("WhatsApp pre-filled message"), max_length=300, blank=True
    )
    calendly_url = models.URLField(
        _("booking link (Calendly or Cal.com)"), blank=True, validators=[validate_booking_url]
    )

    contact_email = models.EmailField(_("contact email"), blank=True)
    contact_phone = models.CharField(_("contact phone"), max_length=30, blank=True)
    address = models.CharField(_("address"), max_length=255, blank=True)

    facebook_url = models.URLField("Facebook", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    tiktok_url = models.URLField("TikTok", blank=True)
    youtube_url = models.URLField("YouTube", blank=True)

    seo_title = models.CharField(_("default SEO title"), max_length=70, blank=True)
    seo_description = models.CharField(_("default meta description"), max_length=160, blank=True)

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self):
        return str(self._meta.verbose_name)

    def whatsapp_link_for(self, message=None):
        """Click-to-chat link with ``message`` (or the default message) pre-filled."""
        if not self.whatsapp_number:
            return ""
        link = f"https://wa.me/{self.whatsapp_number}"
        text = message or self.whatsapp_message
        return f"{link}?text={quote(text)}" if text else link

    @property
    def whatsapp_link(self):
        return self.whatsapp_link_for()

    @property
    def social_links(self):
        links = [
            ("Facebook", self.facebook_url),
            ("Instagram", self.instagram_url),
            ("LinkedIn", self.linkedin_url),
            ("TikTok", self.tiktok_url),
            ("YouTube", self.youtube_url),
        ]
        return [(name, url) for name, url in links if url]

    @property
    def stats(self):
        return [
            (self.stat_projects, _("Projects delivered")),
            (self.stat_years, _("Years of experience")),
            (self.stat_clients, _("Happy clients")),
            (self.stat_countries, _("Countries served")),
        ]


class AboutPage(SingletonModel):
    """Editable copy for the About page (one row)."""

    story_title = models.CharField(_("story heading"), max_length=120, blank=True)
    story = models.TextField(_("our story"), blank=True)
    mission = models.TextField(_("mission"), blank=True)
    values = models.TextField(
        _("values"), blank=True, help_text=_("One per line, as “Title: description”.")
    )
    tools = models.CharField(
        _("tools & technologies"), max_length=300, blank=True, help_text=_("Comma-separated.")
    )

    class Meta:
        verbose_name = _("about page")
        verbose_name_plural = _("about page")

    def __str__(self):
        return str(self._meta.verbose_name)

    @property
    def values_list(self):
        """[(title, description), ...] parsed from "Title: description" lines."""
        pairs = []
        for line in self.values.splitlines():
            title, _sep, description = line.partition(":")
            if title.strip():
                pairs.append((title.strip(), description.strip()))
        return pairs

    @property
    def tools_list(self):
        return [tool.strip() for tool in self.tools.split(",") if tool.strip()]


class TeamMember(models.Model):
    name = models.CharField(_("name"), max_length=100)
    role = models.CharField(_("role"), max_length=100)
    bio = models.TextField(_("short bio"), blank=True)
    photo = models.ImageField(
        _("photo"), upload_to=RandomFilename("team"), validators=image_validators, blank=True
    )
    photo_square = ImageSpecField(
        source="photo", processors=[ResizeToFill(600, 600)], format="WEBP", options={"quality": 82}
    )
    linkedin_url = models.URLField("LinkedIn", blank=True)
    is_active = models.BooleanField(_("show on site"), default=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("team member")
        verbose_name_plural = _("team members")

    def __str__(self):
        return self.name

    @property
    def initials(self):
        return "".join(part[0] for part in self.name.split()[:2]).upper()


class ProcessStep(models.Model):
    """A step of the agency process, shown on Home and About."""

    title = models.CharField(_("title"), max_length=60)
    description = models.CharField(_("description"), max_length=240)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = _("process step")
        verbose_name_plural = _("process steps")

    def __str__(self):
        return self.title


class LegalPage(models.Model):
    class Kind(models.TextChoices):
        PRIVACY = "privacy", _("Privacy Policy")
        TERMS = "terms", _("Terms & Conditions")

    kind = models.CharField(_("page"), max_length=20, choices=Kind.choices, unique=True)
    title = models.CharField(_("title"), max_length=120)
    body = models.TextField(_("content"), help_text=_("Plain text. Blank lines start paragraphs."))
    updated_at = models.DateTimeField(_("last updated"), auto_now=True)

    class Meta:
        ordering = ["kind"]
        verbose_name = _("legal page")
        verbose_name_plural = _("legal pages")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(f"core:{self.kind}")
