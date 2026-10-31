from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

from apps.core.uploads import RandomFilename, image_validators
from apps.core.video import embed_url, validate_video_url

ONE_PER_LINE = _("One per line.")


class Currency(models.TextChoices):
    MUR = "MUR", "MUR (Rs)"
    EUR = "EUR", "EUR (€)"
    USD = "USD", "USD ($)"


class TemplateIndustry(models.Model):
    name = models.CharField(_("name"), max_length=60)
    slug = models.SlugField(_("slug"), unique=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("industry")
        verbose_name_plural = _("industries")

    def __str__(self):
        return self.name


class WebsiteTemplateQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def featured(self):
        return self.published().filter(is_featured=True)


class WebsiteTemplate(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", _("Available")
        COMING_SOON = "coming_soon", _("Coming soon")

    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(_("slug"), unique=True)
    industry = models.ForeignKey(
        TemplateIndustry,
        on_delete=models.PROTECT,
        related_name="templates",
        verbose_name=_("industry"),
    )
    short_description = models.CharField(_("short description"), max_length=180)
    description = models.TextField(_("description"), blank=True)
    features = models.TextField(_("included features"), blank=True, help_text=ONE_PER_LINE)
    pages = models.TextField(_("pages included"), blank=True, help_text=ONE_PER_LINE)

    starting_price = models.DecimalField(
        _("starting price"),
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Leave empty to show “Price on request”."),
    )
    currency = models.CharField(
        _("currency"), max_length=3, choices=Currency.choices, default=Currency.MUR
    )

    cover_image = models.ImageField(
        _("cover image"), upload_to=RandomFilename("templates/covers"), validators=image_validators
    )
    cover_card = ImageSpecField(
        source="cover_image",
        processors=[ResizeToFill(800, 600)],
        format="WEBP",
        options={"quality": 80},
    )
    cover_hero = ImageSpecField(
        source="cover_image",
        processors=[ResizeToFit(1800, 1100)],
        format="WEBP",
        options={"quality": 82},
    )
    demo_url = models.URLField(_("live demo URL"), blank=True)
    video_url = models.URLField(
        _("video link"),
        blank=True,
        validators=[validate_video_url],
        help_text=_("YouTube or Vimeo link."),
    )

    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    is_published = models.BooleanField(_("published"), default=False)
    is_featured = models.BooleanField(_("featured on home page"), default=False)
    order = models.PositiveSmallIntegerField(_("order"), default=0)
    seo_title = models.CharField(_("SEO title"), max_length=70, blank=True)
    seo_description = models.CharField(_("meta description"), max_length=160, blank=True)

    objects = WebsiteTemplateQuerySet.as_manager()

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("website template")
        verbose_name_plural = _("website templates")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("readymade:detail", kwargs={"slug": self.slug})

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE

    @property
    def video_embed_url(self):
        return embed_url(self.video_url)


class TemplateImage(models.Model):
    template = models.ForeignKey(WebsiteTemplate, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        _("image"), upload_to=RandomFilename("templates/gallery"), validators=image_validators
    )
    thumbnail = ImageSpecField(
        source="image", processors=[ResizeToFit(900, 900)], format="WEBP", options={"quality": 80}
    )
    large = ImageSpecField(
        source="image", processors=[ResizeToFit(2000, 2000)], format="WEBP", options={"quality": 85}
    )
    caption = models.CharField(_("caption"), max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = _("screenshot")
        verbose_name_plural = _("screenshots")

    def __str__(self):
        return self.caption or f"{self.template} #{self.pk}"
