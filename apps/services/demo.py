"""Demo services for `manage.py seed_demo`. Replace or edit in admin."""

from apps.portfolio.models import ProjectCategory

from .models import Service, ServiceFAQ, ServiceGroup

GROUPS = [
    {
        "slug": "web-development",
        "name": ("Web Development", "Développement web", "Devlopman web"),
        "intro": (
            "Fast, modern websites designed to turn visitors into customers.",
            "Des sites rapides et modernes conçus pour transformer les visiteurs en clients.",
            "Sit rapid ek modern ki transform vizitor an klian.",
        ),
        "services": [
            (
                "business-websites",
                "code",
                "business",
                ("Business Websites", "Sites vitrines", "Sit biznes"),
                (
                    "A professional site that builds trust and brings in enquiries.",
                    "Un site professionnel qui inspire confiance et génère des demandes.",
                    "Enn sit profesionel ki donn konfians ek amenn demand.",
                ),
            ),
            (
                "e-commerce",
                "cart",
                "ecommerce",
                ("E-commerce Stores", "Boutiques en ligne", "Labutik an liyn"),
                (
                    "Sell online with secure payments, delivery options and stock management.",
                    "Vendez en ligne avec paiements sécurisés, livraison et gestion de stock.",
                    "Vann an liyn avek peman sekirize, livrezon ek zestion stok.",
                ),
            ),
            (
                "landing-pages",
                "rocket",
                "landing",
                ("Landing Pages", "Pages d'atterrissage", "Paz atrisaz"),
                (
                    "High-converting pages for launches, campaigns and ads.",
                    "Des pages performantes pour vos lancements, campagnes et publicités.",
                    "Paz ki konverti bien pou lansman, kanpagn ek piblisite.",
                ),
            ),
            (
                "redesign-maintenance",
                "refresh",
                None,
                ("Redesign & Maintenance", "Refonte & maintenance", "Refer ek mintenans"),
                (
                    "Give an old site a new life, then keep it fast, secure and up to date.",
                    "Donnez une seconde vie à votre site et gardez-le rapide, sûr et à jour.",
                    "Donn ou sit enn nouvo lavi ek gard li rapid, sekirize ek azour.",
                ),
            ),
        ],
    },
    {
        "slug": "ai-marketing",
        "name": ("AI Marketing", "Marketing IA", "Marketing IA"),
        "intro": (
            "Put AI to work on your marketing so you can focus on your business.",
            "Laissez l'IA travailler sur votre marketing pendant que vous gérez votre entreprise.",
            "Les IA travay lor ou marketing pandan ou okip ou biznes.",
        ),
        "services": [
            (
                "ai-content-social-media",
                "sparkles",
                "ai-marketing",
                (
                    "AI Content & Social Media",
                    "Contenu IA & réseaux sociaux",
                    "Kontni IA ek rezo sosyal",
                ),
                (
                    "AI-generated posts, captions, images and videos, planned and published for you.",
                    "Publications, légendes, images et vidéos générées par IA, planifiées et publiées pour vous.",
                    "Post, legend, imaz ek video fer par IA, planifie ek pibliye pou ou.",
                ),
            ),
            (
                "ai-chatbots",
                "chat",
                "ai-marketing",
                ("AI Chatbots", "Chatbots IA", "Chatbot IA"),
                (
                    "Website and WhatsApp chatbots that answer customers and capture leads 24/7.",
                    "Des chatbots site web et WhatsApp qui répondent aux clients et captent des prospects 24h/24.",
                    "Chatbot lor sit web ek WhatsApp ki reponn klian ek ramas prospe 24/7.",
                ),
            ),
        ],
    },
]

BODY = (
    "Every project starts with understanding your goals and your customers. We then design, "
    "build and launch a solution that is fast, easy to manage and built to grow with you.",
    "Chaque projet commence par la compréhension de vos objectifs et de vos clients. Nous "
    "concevons, développons et lançons ensuite une solution rapide, simple à gérer et évolutive.",
)
BENEFITS = (
    "More enquiries from the same traffic\nA brand image customers trust\nLess time spent on admin",
    "Plus de demandes avec le même trafic\nUne image de marque qui inspire confiance\n"
    "Moins de temps passé sur l'administratif",
)
DELIVERABLES = (
    "Strategy call and plan\nDesign and development\nTraining and handover\n30 days of support",
    "Appel stratégique et plan\nDesign et développement\nFormation et remise\n30 jours de support",
)
FAQS = [
    (
        ("How long does it take?", "Combien de temps faut-il ?"),
        (
            "Most projects launch in 2 to 6 weeks, depending on size and how quickly content is ready.",
            "La plupart des projets sont lancés en 2 à 6 semaines selon la taille et la disponibilité "
            "du contenu.",
        ),
    ),
    (
        ("Can I update the content myself?", "Puis-je modifier le contenu moi-même ?"),
        (
            "Yes. Every site comes with an easy admin panel and a short training session.",
            "Oui. Chaque site inclut un espace d'administration simple et une courte formation.",
        ),
    ),
]


def seed_services(stdout=None):
    created = 0
    for group_order, data in enumerate(GROUPS, start=1):
        group, _ = ServiceGroup.objects.get_or_create(
            slug=data["slug"],
            defaults={
                "name_en": data["name"][0],
                "name_fr": data["name"][1],
                "name_mfe": data["name"][2],
                "intro_en": data["intro"][0],
                "intro_fr": data["intro"][1],
                "intro_mfe": data["intro"][2],
                "order": group_order,
            },
        )
        for order, (slug, icon, category, title, summary) in enumerate(data["services"], start=1):
            if Service.objects.filter(slug=slug).exists():
                continue
            service = Service.objects.create(
                group=group,
                slug=slug,
                icon=icon,
                order=order,
                title_en=title[0],
                title_fr=title[1],
                title_mfe=title[2],
                summary_en=summary[0],
                summary_fr=summary[1],
                summary_mfe=summary[2],
                body_en=BODY[0],
                body_fr=BODY[1],
                benefits_en=BENEFITS[0],
                benefits_fr=BENEFITS[1],
                deliverables_en=DELIVERABLES[0],
                deliverables_fr=DELIVERABLES[1],
            )
            if category:
                cat = ProjectCategory.objects.filter(slug=category).first()
                if cat:
                    service.related_projects.set(cat.projects.published()[:3])
            for faq_order, (question, answer) in enumerate(FAQS):
                ServiceFAQ.objects.create(
                    service=service,
                    order=faq_order,
                    question_en=question[0],
                    question_fr=question[1],
                    answer_en=answer[0],
                    answer_fr=answer[1],
                )
            created += 1
    if stdout:
        stdout.write(f"Services: {created} new demo service(s).")
