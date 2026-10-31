"""Demo portfolio content for `manage.py seed_demo`. Replace with real projects in admin.

Client names end in "(demo)" so placeholder work is never mistaken for real clients.
"""

from apps.core.placeholders import placeholder_image

from .models import Project, ProjectCategory, ProjectImage, ProjectMetric

CATEGORIES = [
    ("business", "Business Websites", "Sites vitrines", 1),
    ("ecommerce", "E-commerce", "E-commerce", 2),
    ("landing", "Landing Pages", "Pages d'atterrissage", 3),
    ("ai-marketing", "AI Marketing", "Marketing IA", 4),
]

PROJECTS = [
    {
        "slug": "lagoon-dive-centre",
        "title": ("Lagoon Dive Centre", "Centre de plongée Lagon"),
        "client": "Lagoon Dive Centre (demo)",
        "industry": ("Tourism", "Tourisme"),
        "year": 2026,
        "categories": ["business"],
        "short": (
            "A booking-ready website for a dive school on the west coast.",
            "Un site prêt pour la réservation pour une école de plongée de la côte ouest.",
        ),
        "services": ("Web design, Development, SEO", "Design web, Développement, SEO"),
        "tech": "Django, Tailwind, GSAP",
        "colors": ("#0ea5e9", "#22e3ff"),
        "metrics": [
            ("+140%", "online bookings", "réservations en ligne"),
            ("1.2s", "load time", "temps de chargement"),
        ],
        "featured": True,
    },
    {
        "slug": "island-spice-market",
        "title": ("Island Spice Market", "Marché aux épices de l'île"),
        "client": "Island Spice Market (demo)",
        "industry": ("Retail", "Commerce"),
        "year": 2026,
        "categories": ["ecommerce"],
        "short": (
            "An online store shipping Mauritian spices worldwide.",
            "Une boutique en ligne qui expédie des épices mauriciennes dans le monde entier.",
        ),
        "services": ("E-commerce, Payments, Photography", "E-commerce, Paiements, Photographie"),
        "tech": "Django, HTMX, PayPal",
        "colors": ("#f97316", "#f472b6"),
        "metrics": [
            ("3x", "monthly revenue", "chiffre d'affaires mensuel"),
            ("42", "countries shipped", "pays livrés"),
        ],
        "featured": True,
    },
    {
        "slug": "nordic-villas-launch",
        "title": ("Nordic Villas Launch", "Lancement Nordic Villas"),
        "client": "Nordic Villas (demo)",
        "industry": ("Real estate", "Immobilier"),
        "year": 2025,
        "categories": ["landing"],
        "short": (
            "A high-converting launch page for a luxury villa development.",
            "Une page de lancement performante pour un projet de villas de luxe.",
        ),
        "services": ("Landing page, Copywriting", "Page d'atterrissage, Rédaction"),
        "tech": "Django, GSAP, Three.js",
        "colors": ("#8b5cf6", "#22e3ff"),
        "metrics": [("18%", "visitor-to-lead rate", "taux de conversion en prospects")],
        "featured": True,
    },
    {
        "slug": "cafe-moris-social",
        "title": ("Café Moris Social", "Café Moris sur les réseaux"),
        "client": "Café Moris (demo)",
        "industry": ("Food & drink", "Restauration"),
        "year": 2026,
        "categories": ["ai-marketing"],
        "short": (
            "AI-generated content calendar and visuals for a growing café chain.",
            "Calendrier de contenu et visuels générés par IA pour une chaîne de cafés.",
        ),
        "services": ("AI content, Social media", "Contenu IA, Réseaux sociaux"),
        "tech": "OpenAI, Canva, Meta Business Suite",
        "colors": ("#a855f7", "#f472b6"),
        "metrics": [
            ("+260%", "Instagram reach", "portée Instagram"),
            ("12h", "saved per week", "gagnées par semaine"),
        ],
        "featured": False,
    },
    {
        "slug": "green-isle-solar",
        "title": ("Green Isle Solar", "Green Isle Solaire"),
        "client": "Green Isle Solar (demo)",
        "industry": ("Energy", "Énergie"),
        "year": 2025,
        "categories": ["business", "ai-marketing"],
        "short": (
            "Corporate website plus an AI chatbot that qualifies solar leads.",
            "Site corporate et chatbot IA qui qualifie les prospects solaires.",
        ),
        "services": ("Website, AI chatbot", "Site web, Chatbot IA"),
        "tech": "Django, Alpine.js, OpenAI",
        "colors": ("#22c55e", "#22e3ff"),
        "metrics": [("65%", "leads qualified by AI", "prospects qualifiés par l'IA")],
        "featured": False,
    },
    {
        "slug": "port-louis-fashion",
        "title": ("Port Louis Fashion", "Mode Port-Louis"),
        "client": "PL Fashion House (demo)",
        "industry": ("Fashion", "Mode"),
        "year": 2024,
        "categories": ["ecommerce"],
        "short": (
            "A mobile-first boutique store with lookbooks and drops.",
            "Une boutique mobile-first avec lookbooks et collections capsules.",
        ),
        "services": ("E-commerce, Branding", "E-commerce, Image de marque"),
        "tech": "Django, Tailwind, Stripe",
        "colors": ("#ec4899", "#8b5cf6"),
        "metrics": [("+75%", "mobile conversion", "conversion mobile")],
        "featured": False,
    },
    {
        "slug": "ebene-law-chambers",
        "title": ("Ebene Law Chambers", "Cabinet juridique Ébène"),
        "client": "Ebene Law Chambers (demo)",
        "industry": ("Legal", "Juridique"),
        "year": 2024,
        "categories": ["business"],
        "short": (
            "A trustworthy, bilingual website for a corporate law firm.",
            "Un site bilingue et rassurant pour un cabinet d'avocats d'affaires.",
        ),
        "services": (
            "Web design, Development, Translation",
            "Design web, Développement, Traduction",
        ),
        "tech": "Django, Tailwind",
        "colors": ("#64748b", "#22e3ff"),
        "metrics": [("2x", "consultation requests", "demandes de consultation")],
        "featured": False,
    },
]

STORY = {
    "challenge": (
        "The client's old website was slow, hard to update and didn't work well on phones, "
        "so most visitors left before getting in touch.",
        "L'ancien site du client était lent, difficile à mettre à jour et mal adapté aux mobiles : "
        "la plupart des visiteurs partaient avant de prendre contact.",
    ),
    "solution": (
        "We designed a fast, mobile-first site with clear calls to action, content they can edit "
        "themselves, and analytics to track every enquiry.",
        "Nous avons conçu un site rapide, pensé pour le mobile, avec des appels à l'action clairs, "
        "un contenu modifiable par le client et un suivi de chaque demande.",
    ),
    "results": (
        "Within three months the new site was bringing in more qualified enquiries than ever, "
        "with far less time spent on manual updates.",
        "En trois mois, le nouveau site générait plus de demandes qualifiées que jamais, "
        "avec beaucoup moins de temps passé sur les mises à jour.",
    ),
}


def seed_portfolio(stdout=None):
    categories = {}
    for slug, name_en, name_fr, order in CATEGORIES:
        categories[slug], _ = ProjectCategory.objects.get_or_create(
            slug=slug, defaults={"name_en": name_en, "name_fr": name_fr, "order": order}
        )

    created = 0
    for order, data in enumerate(PROJECTS, start=1):
        if Project.objects.filter(slug=data["slug"]).exists():
            continue  # never touch projects the owner may have edited
        title_en, title_fr = data["title"]
        project = Project.objects.create(
            slug=data["slug"],
            title_en=title_en,
            title_fr=title_fr,
            client=data["client"],
            industry_en=data["industry"][0],
            industry_fr=data["industry"][1],
            year=data["year"],
            short_description_en=data["short"][0],
            short_description_fr=data["short"][1],
            services_en=data["services"][0],
            services_fr=data["services"][1],
            tech_stack=data["tech"],
            challenge_en=STORY["challenge"][0],
            challenge_fr=STORY["challenge"][1],
            solution_en=STORY["solution"][0],
            solution_fr=STORY["solution"][1],
            results_en=STORY["results"][0],
            results_fr=STORY["results"][1],
            cover_image=placeholder_image(title_en, colors=data["colors"], name="cover.png"),
            is_published=True,
            is_featured=data["featured"],
            order=order,
        )
        project.categories.set(categories[slug] for slug in data["categories"])

        for index, (value, label_en, label_fr) in enumerate(data["metrics"]):
            ProjectMetric.objects.create(
                project=project, value=value, label_en=label_en, label_fr=label_fr, order=index
            )

        shots = [
            ("desktop", (1600, 1000), "Home page"),
            ("desktop", (1600, 1000), "Services"),
            ("mobile", (600, 1200), "Mobile home"),
            ("mobile", (600, 1200), "Mobile menu"),
        ]
        for index, (kind, size, caption) in enumerate(shots):
            ProjectImage.objects.create(
                project=project,
                kind=kind,
                caption_en=caption,
                order=index,
                image=placeholder_image(
                    f"{title_en} · {caption}", size=size, colors=data["colors"]
                ),
            )
        created += 1

    if stdout:
        stdout.write(f"Portfolio: {len(categories)} categories, {created} new demo project(s).")
