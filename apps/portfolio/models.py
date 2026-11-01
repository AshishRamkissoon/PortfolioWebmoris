from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

from apps.core.uploads import RandomFilename, image_validators, video_validators
from apps.core.video import embed_url, validate_video_url


class ProjectCategory(models.Model):
    name = models.CharField(_("name"), max_length=60)
    slug = models.SlugField(_("slug"), unique=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.name


class ProjectQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def featured(self):
        return self.published().filter(is_featured=True)

    def completed(self):
        return self.published().filter(status=Project.Status.COMPLETED)


class Project(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", _("Completed")
        IN_PROGRESS = "in_progress", _("In progress")

    title = models.CharField(_("title"), max_length=120)
    slug = models.SlugField(_("slug"), unique=True)
    client = models.CharField(_("client"), max_length=120)
    industry = models.CharField(_("industry"), max_length=80, blank=True)
    year = models.PositiveSmallIntegerField(_("year"))
    categories = models.ManyToManyField(
        ProjectCategory, related_name="projects", verbose_name=_("categories")
    )
    short_description = models.CharField(_("short description"), max_length=180)
    services = models.CharField(
        _("services provided"), max_length=200, blank=True, help_text=_("Comma-separated.")
    )
    tech_stack = models.CharField(
        _("tech stack"),
        max_length=200,
        blank=True,
        help_text=_("Comma-separated, e.g. Django, Tailwind."),
    )

    challenge = models.TextField(_("the challenge"))
    solution = models.TextField(_("the solution"))
    results = models.TextField(_("the results"), blank=True)

    cover_image = models.ImageField(
        _("cover image"), upload_to=RandomFilename("projects/covers"), validators=image_validators
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

    live_url = models.URLField(_("live site URL"), blank=True)
    video_url = models.URLField(
        _("video link"),
        blank=True,
        validators=[validate_video_url],
        help_text=_("YouTube or Vimeo link."),
    )
    video_file = models.FileField(
        _("video file"),
        upload_to=RandomFilename("projects/videos"),
        blank=True,
        validators=video_validators,
        help_text=_("MP4 or WebM, max 50 MB. Used when no video link is set."),
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
        help_text=_("In-progress projects show a badge and hide results and the live-site link."),
    )
    is_published = models.BooleanField(_("published"), default=False)
    is_featured = models.BooleanField(_("featured on home page"), default=False)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    seo_title = models.CharField(_("SEO title"), max_length=70, blank=True)
    seo_description = models.CharField(_("meta description"), max_length=160, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["order", "-year", "title"]
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("portfolio:detail", kwargs={"slug": self.slug})

    @property
    def services_list(self):
        return _split(self.services)

    @property
    def tech_list(self):
        return _split(self.tech_stack)

    @property
    def video_embed_url(self):
        return embed_url(self.video_url)

    @property
    def has_video(self):
        return bool(self.video_embed_url or self.video_file)

    @property
    def is_in_progress(self):
        return self.status == self.Status.IN_PROGRESS

    @property
    def show_live_url(self):
        """No live-site link until the project is finished."""
        return bool(self.live_url) and not self.is_in_progress


class ProjectMetric(models.Model):
    """A headline result such as "+120%" / "organic traffic"."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="metrics")
    value = models.CharField(_("value"), max_length=20, help_text=_('e.g. "+120%" or "3x".'))
    label = models.CharField(_("label"), max_length=80)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = _("result metric")
        verbose_name_plural = _("result metrics")

    def __str__(self):
        return f"{self.value} {self.label}"


class ProjectImage(models.Model):
    class Kind(models.TextChoices):
        DESKTOP = "desktop", _("Desktop")
        MOBILE = "mobile", _("Mobile")

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        _("image"), upload_to=RandomFilename("projects/gallery"), validators=image_validators
    )
    thumbnail = ImageSpecField(
        source="image", processors=[ResizeToFit(900, 900)], format="WEBP", options={"quality": 80}
    )
    large = ImageSpecField(
        source="image", processors=[ResizeToFit(2000, 2000)], format="WEBP", options={"quality": 85}
    )
    kind = models.CharField(_("type"), max_length=10, choices=Kind.choices, default=Kind.DESKTOP)
    caption = models.CharField(_("caption"), max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = _("screenshot")
        verbose_name_plural = _("screenshots")

    def __str__(self):
        return self.caption or f"{self.project} #{self.pk}"


def _split(value):
    return [item.strip() for item in value.split(",") if item.strip()]
