"""Demo ready-made website templates for `manage.py seed_demo`. Replace in admin.

Demo templates have no demo URL, so no "Live demo" button points at a site that doesn't exist.
Templates with a built demo (see `demos/`) use real screenshots from `demo_screens/<slug>/`.
"""

from pathlib import Path

from django.core.files.base import ContentFile

from apps.core.placeholders import placeholder_image

from .models import TemplateImage, TemplateIndustry, WebsiteTemplate

INDUSTRIES = [
    ("restaurant", "Restaurant", "Restaurant"),
    ("tourism", "Tourism", "Tourisme"),
    ("car-rental", "Car rental", "Location de voitures"),
    ("real-estate", "Real estate", "Immobilier"),
]

TEMPLATES = [
    (
        "lagon-bistro",
        "restaurant",
        "Lagon Bistro",
        25000,
        "available",
        True,
        ("#f97316", "#f472b6"),
        (
            "A warm restaurant site with menu, gallery and table bookings.",
            "Un site chaleureux avec menu, galerie et réservation de table.",
        ),
    ),
    (
        "island-explorer",
        "tourism",
        "Island Explorer",
        35000,
        "available",
        True,
        ("#0ea5e9", "#22e3ff"),
        (
            "Tours and excursions with online booking and reviews.",
            "Excursions et visites avec réservation en ligne et avis.",
        ),
    ),
    (
        "drive-moris",
        "car-rental",
        "Drive Moris",
        40000,
        "available",
        True,
        ("#8b5cf6", "#22e3ff"),
        (
            "A car rental site with fleet listing and booking requests.",
            "Un site de location avec flotte de véhicules et demandes de réservation.",
        ),
    ),
    (
        "villa-select",
        "real-estate",
        "Villa Select",
        45000,
        "available",
        True,
        ("#22c55e", "#0ea5e9"),
        (
            "Property listings with search, filters and enquiry forms.",
            "Annonces immobilières avec recherche, filtres et formulaires de contact.",
        ),
    ),
    (
        "street-food-co",
        "restaurant",
        "Street Food Co.",
        None,
        "coming_soon",
        False,
        ("#ec4899", "#f97316"),
        (
            "A bold, mobile-first site for food trucks and takeaways.",
            "Un site audacieux, pensé mobile, pour food trucks et vente à emporter.",
        ),
    ),
    (
        "eco-lodge",
        "tourism",
        "Eco Lodge",
        None,
        "coming_soon",
        False,
        ("#64748b", "#22c55e"),
        (
            "A calm, nature-inspired site for guesthouses and lodges.",
            "Un site apaisant, inspiré de la nature, pour maisons d'hôtes et lodges.",
        ),
    ),
]

FEATURES = (
    "Mobile-friendly design\nContact and enquiry forms\nWhatsApp button\nGoogle Maps\nSEO basics\n"
    "Easy admin panel",
    "Design adapté au mobile\nFormulaires de contact\nBouton WhatsApp\nGoogle Maps\nBases SEO\n"
    "Administration simple",
)
PAGES = ("Home\nAbout\nServices\nGallery\nContact", "Accueil\nÀ propos\nServices\nGalerie\nContact")
DESCRIPTION = (
    "A ready-made design built for your industry. We add your logo, colours, photos and text, "
    "connect your domain and launch it, usually within a week.",
    "Un design clé en main pensé pour votre secteur. Nous ajoutons votre logo, vos couleurs, "
    "vos photos et vos textes, connectons votre domaine et lançons le site, souvent en une semaine.",
)


SCREENS_DIR = Path(__file__).resolve().parent / "demo_screens"
# Gallery screenshots per template, in display order: (file, English caption, French caption).
SCREENS = {
    "drive-moris": [
        ("devices.jpg", "Home page on desktop and phone", "Accueil sur ordinateur et mobile"),
        (
            "coast.jpg",
            "The coast route draws itself as you scroll",
            "L'itinéraire côtier se dessine au défilement",
        ),
        ("fleet.jpg", "Fleet with filters and clear prices", "Flotte avec filtres et prix clairs"),
        (
            "book.jpg",
            "Booking with a live trip ticket",
            "Réservation avec ticket de voyage en direct",
        ),
    ],
    "lagon-bistro": [
        ("devices.jpg", "Home page on desktop and phone", "Accueil sur ordinateur et mobile"),
        (
            "day.jpg",
            "From lunch to late: the sky changes as you scroll",
            "Du déjeuner au soir : le ciel change au défilement",
        ),
        ("cocktails.jpg", "Cocktail reel", "Carrousel de cocktails"),
        ("menu.jpg", "Menu with photo previews", "Menu avec aperçus photo"),
    ],
    "island-explorer": [
        ("devices.jpg", "Home page on desktop and phone", "Accueil sur ordinateur et mobile"),
        ("moods.jpg", "Tours by mood", "Excursions par thème"),
        ("tours.jpg", "Tour listing with filters", "Liste des excursions avec filtres"),
        ("tour.jpg", "Tour page", "Page d'une excursion"),
    ],
}


def screenshot(slug, filename):
    path = SCREENS_DIR / slug / filename
    return ContentFile(path.read_bytes(), name=filename)


def seed_readymade(stdout=None):
    industries = {}
    for order, (slug, en, fr) in enumerate(INDUSTRIES, start=1):
        industries[slug], _ = TemplateIndustry.objects.get_or_create(
            slug=slug, defaults={"name_en": en, "name_fr": fr, "order": order}
        )

    created = 0
    for order, (slug, industry, name, price, status, featured, colors, short) in enumerate(
        TEMPLATES, start=1
    ):
        if WebsiteTemplate.objects.filter(slug=slug).exists():
            continue
        template = WebsiteTemplate.objects.create(
            slug=slug,
            name_en=name,
            industry=industries[industry],
            short_description_en=short[0],
            short_description_fr=short[1],
            description_en=DESCRIPTION[0],
            description_fr=DESCRIPTION[1],
            features_en=FEATURES[0],
            features_fr=FEATURES[1],
            pages_en=PAGES[0],
            pages_fr=PAGES[1],
            starting_price=price,
            status=status,
            is_published=True,
            is_featured=featured,
            order=order,
            cover_image=screenshot(slug, "cover.jpg")
            if slug in SCREENS
            else placeholder_image(f"{name} template", colors=colors, name="cover.png"),
        )
        if slug in SCREENS:
            for index, (filename, caption_en, caption_fr) in enumerate(SCREENS[slug]):
                TemplateImage.objects.create(
                    template=template,
                    order=index,
                    caption_en=caption_en,
                    caption_fr=caption_fr,
                    image=screenshot(slug, filename),
                )
        else:
            for index, page in enumerate(["Home", "Services"]):
                TemplateImage.objects.create(
                    template=template,
                    order=index,
                    caption_en=page,
                    image=placeholder_image(f"{name} · {page}", colors=colors),
                )
        created += 1
    if stdout:
        stdout.write(f"Ready-made websites: {created} new demo template(s).")
