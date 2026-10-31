from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.portfolio.models import Project

ONE_PER_LINE = _("One per line.")


class ServiceGroup(models.Model):
    name = models.CharField(_("name"), max_length=80)
    slug = models.SlugField(_("slug"), unique=True)
    intro = models.CharField(_("intro"), max_length=240, blank=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("service group")
        verbose_name_plural = _("service groups")

    def __str__(self):
        return self.name


class ServiceQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Service(models.Model):
    class Icon(models.TextChoices):
        CODE = "code", _("Code")
        CART = "cart", _("Shopping cart")
        ROCKET = "rocket", _("Rocket")
        REFRESH = "refresh", _("Refresh")
        SPARKLES = "sparkles", _("Sparkles")
        CHAT = "chat", _("Chat")
        MEGAPHONE = "megaphone", _("Megaphone")
        CHART = "chart", _("Chart")

    group = models.ForeignKey(
        ServiceGroup, on_delete=models.PROTECT, related_name="services", verbose_name=_("group")
    )
    title = models.CharField(_("title"), max_length=100)
    slug = models.SlugField(_("slug"), unique=True)
    icon = models.CharField(_("icon"), max_length=20, choices=Icon.choices, default=Icon.CODE)
    summary = models.CharField(_("summary"), max_length=200)
    body = models.TextField(_("description"), blank=True)
    benefits = models.TextField(_("benefits"), blank=True, help_text=ONE_PER_LINE)
    deliverables = models.TextField(_("what you get"), blank=True, help_text=ONE_PER_LINE)
    related_projects = models.ManyToManyField(
        Project, blank=True, related_name="services_used", verbose_name=_("related projects")
    )
    is_published = models.BooleanField(_("published"), default=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)
    seo_title = models.CharField(_("SEO title"), max_length=70, blank=True)
    seo_description = models.CharField(_("meta description"), max_length=160, blank=True)

    objects = ServiceQuerySet.as_manager()

    class Meta:
        ordering = ["group__order", "order", "title"]
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("services:detail", kwargs={"slug": self.slug})


class ServiceFAQ(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(_("question"), max_length=200)
    answer = models.TextField(_("answer"))
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")

    def __str__(self):
        return self.question
