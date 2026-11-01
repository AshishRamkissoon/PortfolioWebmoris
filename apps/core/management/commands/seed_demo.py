from django.core.management.base import BaseCommand

from apps.core.demo import seed_core_content
from apps.core.models import SiteSettings
from apps.portfolio.demo import seed_portfolio
from apps.pricing.demo import seed_pricing
from apps.readymade.demo import seed_readymade
from apps.services.demo import seed_services

# Placeholder values only — the owner replaces them in admin.
SITE_SETTINGS_DEMO = {
    "tagline_en": "Websites and AI marketing that grow your business",
    "tagline_fr": "Sites web et marketing IA pour faire grandir votre entreprise",
    "footer_about_en": "Webmoris is a Mauritius-based agency building fast, modern websites "
    "and AI-powered marketing for ambitious businesses.",
    "footer_about_fr": "Webmoris est une agence mauricienne qui crée des sites web modernes "
    "et rapides et du marketing propulsé par l'IA.",
    "whatsapp_number": "23050000000",
    "whatsapp_message_en": "Hello Webmoris, I'd like to discuss a project.",
    "whatsapp_message_fr": "Bonjour Webmoris, j'aimerais discuter d'un projet.",
    "contact_email": "hello@example.com",
    "contact_phone": "+230 5000 0000",
    "address": "Mauritius",
    "seo_title_en": "Webmoris — Web Development & AI Marketing Agency in Mauritius",
    "seo_title_fr": "Webmoris — Agence web et marketing IA à Maurice",
    "seo_description_en": "We design and build modern websites and run AI-powered marketing "
    "for businesses in Mauritius and abroad.",
    "seo_description_fr": "Nous concevons des sites web modernes et gérons du marketing propulsé "
    "par l'IA pour les entreprises à Maurice et à l'étranger.",
}


class Command(BaseCommand):
    help = "Fill empty fields with demo content. Safe to run repeatedly; never overwrites."

    def handle(self, *args, **options):
        settings_obj = SiteSettings.load()
        filled = []
        for field, value in SITE_SETTINGS_DEMO.items():
            if not getattr(settings_obj, field):
                setattr(settings_obj, field, value)
                filled.append(field)
        settings_obj.save()
        self.stdout.write(
            self.style.SUCCESS(f"Site settings: filled {len(filled)} empty field(s).")
        )

        # Portfolio first: services link to demo projects.
        for seed in (
            seed_core_content,
            seed_portfolio,
            seed_services,
            seed_readymade,
            seed_pricing,
        ):
            seed(stdout=self.stdout)
