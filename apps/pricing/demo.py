"""Demo packages for `manage.py seed_demo`. No prices: visitors send a brief and get a quote.
Add an optional "From" price per package in admin if you want one shown.

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
            "Basic SEO and Google setup\nOnline in about 2 weeks",
            "Site d'une page\nDesign adapté au mobile\nFormulaire de contact & WhatsApp\n"
            "SEO de base et Google\nEn ligne en 2 semaines environ",
        ),
        "billing": "one_off",
        "popular": False,
    },
    {
        "slug": "business-website",
        "name": ("Business Website", "Site Business"),
        "summary": (
            "A complete multi-page website that builds trust and brings in enquiries.",
            "Un site complet de plusieurs pages qui inspire confiance et génère des demandes.",
        ),
        "features": (
            "Up to 8 pages\nCustom design & animations\nEnglish and French\n"
            "Blog, portfolio or services pages\nSEO setup & Google Analytics\n"
            "Easy admin panel\n30 days of support after launch",
            "Jusqu'à 8 pages\nDesign et animations sur mesure\nAnglais et français\n"
            "Blog, portfolio ou pages services\nSEO & Google Analytics\n"
            "Administration simple\n30 jours de support après la mise en ligne",
        ),
        "billing": "one_off",
        "popular": True,
    },
    {
        "slug": "online-store-booking",
        "name": ("Online Store or Booking Site", "Boutique en ligne ou site de réservation"),
        "summary": (
            "Sell products or take bookings online, with payments built in.",
            "Vendez en ligne ou prenez des réservations, avec paiement intégré.",
        ),
        "features": (
            "Product catalogue or booking calendar\nOnline payments (PayPal, MCB Juice)\n"
            "Customer accounts & order emails\nEnglish and French\n"
            "Easy admin panel\n60 days of support after launch",
            "Catalogue ou calendrier de réservation\nPaiement en ligne (PayPal, MCB Juice)\n"
            "Comptes clients & e-mails de commande\nAnglais et français\n"
            "Administration simple\n60 jours de support après la mise en ligne",
        ),
        "billing": "one_off",
        "popular": False,
    },
    {
        "slug": "care-plan",
        "name": ("Care Plan", "Forfait Entretien"),
        "summary": (
            "Hosting, updates, backups and small changes, so you never have to worry.",
            "Hébergement, mises à jour, sauvegardes et petites modifications, l'esprit tranquille.",
        ),
        "features": (
            "Fast, secure hosting & SSL\nDaily backups\nSecurity & software updates\n"
            "Small content changes each month\nMonthly health report\nPriority WhatsApp support",
            "Hébergement rapide et sécurisé (SSL)\nSauvegardes quotidiennes\n"
            "Mises à jour de sécurité\nPetites modifications chaque mois\n"
            "Rapport mensuel\nSupport WhatsApp prioritaire",
        ),
        "billing": "monthly",
        "popular": False,
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
            is_popular=data["popular"],
            is_purchasable=False,
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
