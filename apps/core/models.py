from urllib.parse import quote

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

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
    calendly_url = models.URLField(_("Calendly URL"), blank=True)

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

    @property
    def whatsapp_link(self):
        if not self.whatsapp_number:
            return ""
        link = f"https://wa.me/{self.whatsapp_number}"
        if self.whatsapp_message:
            link += f"?text={quote(self.whatsapp_message)}"
        return link

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
