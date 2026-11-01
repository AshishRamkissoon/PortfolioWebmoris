"""Demo packages for `manage.py seed_demo`. Prices are placeholders: set real ones in admin.

The demo Juice/bank details are obviously fake ("DEMO"), so nobody can pay into them.
"""

from apps.core.models import SiteSettings

from .models import Package

PACKAGES = [
    {
        "slug": "starter-website",
        "name": ("Starter Website", "Site Starter"),
        "summary": (
            "A clean one-page site to get your business online fast.",
            "Un site d'une page pour être en ligne rapidement.",
        ),
        "features": (
            "One-page website\nMobile-friendly design\nContact form & WhatsApp button\n"
            "Basic SEO\n1 round of revisions",
            "Site d'une page\nDesign adapté au mobile\nFormulaire de contact & WhatsApp\n"
            "SEO de base\n1 série de modifications",
        ),
        "billing": "one_off",
        "price": 25000,
        "paypal_price": 550,
        "popular": False,
        "purchasable": True,
    },
    {
        "slug": "business-website",
        "name": ("Business Website", "Site Business"),
        "summary": (
            "A complete multi-page website that builds trust and wins clients.",
            "Un site complet de plusieurs pages qui inspire confiance.",
        ),
        "features": (
            "Up to 6 pages\nCustom design & animations\nBlog or portfolio section\n"
            "SEO setup & Google Analytics\nEasy admin panel\n30 days of support",
            "Jusqu'à 6 pages\nDesign et animations sur mesure\nBlog ou portfolio\n"
            "SEO & Google Analytics\nAdministration simple\n30 jours de support",
        ),
        "billing": "one_off",
        "price": 60000,
        "paypal_price": 1300,
        "popular": True,
        "purchasable": True,
    },
    {
        "slug": "ai-chatbot-setup",
        "name": ("AI Chatbot Setup", "Chatbot IA"),
        "summary": (
            "A website or WhatsApp chatbot trained on your business.",
            "Un chatbot site web ou WhatsApp formé sur votre entreprise.",
        ),
        "features": (
            "Website or WhatsApp chatbot\nTrained on your content\nLead capture\nMonthly report",
            "Chatbot site web ou WhatsApp\nFormé sur vos contenus\nCapture de prospects\n"
            "Rapport mensuel",
        ),
        "billing": "one_off",
        "price": 35000,
        "paypal_price": None,
        "popular": False,
        "purchasable": False,  # needs a discussion first → "Request a quote"
    },
    {
        "slug": "ai-social-media-monthly",
        "name": ("AI Social Media", "Réseaux sociaux IA"),
        "summary": (
            "AI-powered posts, visuals and captions every month.",
            "Publications, visuels et légendes générés par IA chaque mois.",
        ),
        "features": (
            "12 posts per month\nAI-generated visuals\nCaptions in EN/FR\nScheduling & publishing\n"
            "Monthly performance report",
            "12 publications par mois\nVisuels générés par IA\nLégendes EN/FR\n"
            "Planification & publication\nRapport mensuel",
        ),
        "billing": "monthly",
        "price": 8000,
        # PayPal needs a billing plan ID from your PayPal account before it can be enabled.
        "paypal_price": None,
        "popular": False,
        "purchasable": True,
    },
]

DEMO_PAYMENT_DETAILS = {
    "juice_number": "5000 0000 (DEMO)",
    "juice_account_name": "Webmoris (DEMO — replace in admin)",
    "bank_details": "DEMO — replace in admin\nBank: Example Bank\nAccount name: Webmoris\n"
    "Account number: 000000000000",
}


def seed_pricing(stdout=None):
    created = 0
    for order, data in enumerate(PACKAGES, start=1):
        if Package.objects.filter(slug=data["slug"]).exists():
            continue
        Package.objects.create(
            slug=data["slug"],
            name_en=data["name"][0],
            name_fr=data["name"][1],
            summary_en=data["summary"][0],
            summary_fr=data["summary"][1],
            features_en=data["features"][0],
            features_fr=data["features"][1],
            billing=data["billing"],
            price=data["price"],
            paypal_price=data["paypal_price"],
            is_popular=data["popular"],
            is_purchasable=data["purchasable"],
            order=order,
        )
        created += 1

    site_settings = SiteSettings.load()
    for field, value in DEMO_PAYMENT_DETAILS.items():
        if not getattr(site_settings, field):
            setattr(site_settings, field, value)
    site_settings.save()

    if stdout:
        stdout.write(f"Pricing: {created} new demo package(s).")
