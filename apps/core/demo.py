"""Demo content for the About page, team, process and legal pages. Replace in admin.

Team members are clearly marked "(demo)", and the legal pages say they must be replaced:
neither should ever go live as if it were real.
"""

from .models import (
    FAQ,
    AboutPage,
    HeroBusiness,
    LegalPage,
    ProcessStep,
    TeamMember,
    TrustPromise,
)

PROCESS = [
    (
        "Discover",
        "Découverte",
        "We learn about your business, goals and customers.",
        "Nous découvrons votre entreprise, vos objectifs et vos clients.",
    ),
    (
        "Design",
        "Design",
        "We plan the structure and design how your site will look and feel.",
        "Nous planifions la structure et concevons l'apparence de votre site.",
    ),
    (
        "Develop",
        "Développement",
        "We build a fast, secure site that you can easily manage.",
        "Nous développons un site rapide, sûr et facile à gérer.",
    ),
    (
        "Launch",
        "Lancement",
        "We test everything, connect your domain and go live.",
        "Nous testons tout, connectons votre domaine et mettons le site en ligne.",
    ),
    (
        "Grow",
        "Croissance",
        "We help you get more visitors and leads with SEO and AI marketing.",
        "Nous vous aidons à attirer plus de visiteurs et de prospects grâce au SEO et à l'IA.",
    ),
]

ABOUT = {
    "story_title_en": "A Mauritian agency building for the web — and for AI.",
    "story_title_fr": "Une agence mauricienne qui construit pour le web — et pour l'IA.",
    "story_en": "Webmoris helps businesses in Mauritius and abroad stand out online.\n\n"
    "We combine modern web development with AI-powered marketing, so our clients get a website "
    "that looks great and a marketing engine that keeps working for them.\n\n"
    "(Demo text: replace it with your own story in admin.)",
    "story_fr": "Webmoris aide les entreprises à Maurice et à l'étranger à se démarquer en ligne.\n\n"
    "Nous associons développement web moderne et marketing propulsé par l'IA.\n\n"
    "(Texte de démonstration : remplacez-le par votre histoire dans l'administration.)",
    "mission_en": "Give every business a website and marketing that work as hard as they do.",
    "mission_fr": "Offrir à chaque entreprise un site et un marketing aussi efficaces qu'elle.",
    "values_en": "Quality: we sweat the details, from code to copy.\n"
    "Transparency: clear prices, clear timelines, no surprises.\n"
    "Results: we measure success by your growth.",
    "values_fr": "Qualité : nous soignons chaque détail, du code aux textes.\n"
    "Transparence : prix clairs, délais clairs, aucune surprise.\n"
    "Résultats : nous mesurons notre succès à votre croissance.",
    "tools": "Django, Python, Tailwind CSS, GSAP, Three.js, OpenAI, Figma, Google Analytics",
}

TEAM = [
    ("Team member 1 (demo)", "Founder & Lead Developer", "Fondateur & développeur principal"),
    ("Team member 2 (demo)", "UI/UX Designer", "Designer UI/UX"),
    ("Team member 3 (demo)", "AI Marketing Specialist", "Spécialiste marketing IA"),
]

LEGAL_PLACEHOLDER = (
    "DEMO TEXT — replace this page with your real {title} before the site goes live. "
    "Have it reviewed by a legal professional.\n\n"
    "This page should explain, in plain language, how Webmoris handles the topics a visitor "
    "would expect to find here."
)


def seed_core_content(stdout=None):
    about = AboutPage.load()
    filled = [field for field, value in ABOUT.items() if not getattr(about, field)]
    for field in filled:
        setattr(about, field, ABOUT[field])
    about.save()

    if not ProcessStep.objects.exists():
        for order, (en, fr, desc_en, desc_fr) in enumerate(PROCESS):
            ProcessStep.objects.create(
                order=order,
                title_en=en,
                title_fr=fr,
                description_en=desc_en,
                description_fr=desc_fr,
            )

    if not TeamMember.objects.exists():
        for order, (name, role_en, role_fr) in enumerate(TEAM):
            TeamMember.objects.create(name=name, role_en=role_en, role_fr=role_fr, order=order)

    for kind, label in LegalPage.Kind.choices:
        title = str(label)
        LegalPage.objects.get_or_create(
            kind=kind,
            defaults={"title_en": title, "body_en": LEGAL_PLACEHOLDER.format(title=title.lower())},
        )

    if stdout:
        stdout.write(
            f"About/team/process/legal: filled {len(filled)} about field(s); "
            f"{ProcessStep.objects.count()} steps, {TeamMember.objects.count()} team members."
        )


# Home hero "See what we could build for you": (slug, label, features, package, demo, brief type).
HERO_BUSINESSES = [
    (
        "restaurant",
        ("Restaurant", "Restaurant"),
        (
            "Menu online\nTable booking\nWhatsApp orders",
            "Menu en ligne\nRéservation de table\nCommandes WhatsApp",
        ),
        "business-website",
        "lagon-bistro",
        "website",
    ),
    (
        "tours",
        ("Tours & activities", "Excursions & activités"),
        (
            "Online booking\nActivity pages\nReviews & photos",
            "Réservation en ligne\nPages d'activités\nAvis & photos",
        ),
        "online-store-booking",
        "island-explorer",
        "booking",
    ),
    (
        "car-rental",
        ("Car rental", "Location de voitures"),
        (
            "Fleet & prices\nBooking requests\nAirport pick-up info",
            "Flotte & tarifs\nDemandes de réservation\nInfos aéroport",
        ),
        "online-store-booking",
        "drive-moris",
        "booking",
    ),
    (
        "villas",
        ("Villas & real estate", "Villas & immobilier"),
        (
            "Property listings\nPhoto galleries\nEnquiry forms",
            "Annonces de biens\nGaleries photos\nFormulaires de contact",
        ),
        "business-website",
        "villa-select",
        "website",
    ),
    (
        "hotels",
        ("Hotels & lodges", "Hôtels & lodges"),
        (
            "Room booking\nEnglish & French\nGoogle Maps & reviews",
            "Réservation de chambres\nAnglais & français\nGoogle Maps & avis",
        ),
        "online-store-booking",
        "eco-lodge",
        "booking",
    ),
]


def seed_hero_businesses(stdout=None):
    """Runs after pricing and ready-made seeds, since each type links a package and a demo."""
    from apps.pricing.models import Package
    from apps.readymade.models import WebsiteTemplate

    if HeroBusiness.objects.exists():
        return
    for order, (slug, label, features, package, template, project_type) in enumerate(
        HERO_BUSINESSES
    ):
        HeroBusiness.objects.create(
            slug=slug,
            label_en=label[0],
            label_fr=label[1],
            features_en=features[0],
            features_fr=features[1],
            package=Package.objects.filter(slug=package).first(),
            template=WebsiteTemplate.objects.filter(slug=template).first(),
            project_type=project_type,
            order=order,
        )
    if stdout:
        stdout.write(f"Hero: {len(HERO_BUSINESSES)} business types.")


# Promises: (icon, title EN/FR, text EN/FR). Only promises the agency already keeps.
PROMISES = [
    (
        "check",
        ("Fixed quote before we start", "Un devis fixe avant de commencer"),
        (
            "Price, scope and timeline in writing. No surprise bills.",
            "Prix, contenu et délais par écrit. Aucune facture surprise.",
        ),
    ),
    (
        "wallet",
        ("Pay in stages", "Paiement en plusieurs fois"),
        (
            "A deposit to start, the balance at launch. Never everything upfront.",
            "Un acompte pour commencer, le solde à la mise en ligne. Jamais tout d'avance.",
        ),
    ),
    (
        "clock",
        ("A reply within one business day", "Une réponse sous un jour ouvré"),
        (
            "By email or WhatsApp, from a real person on the team.",
            "Par e-mail ou WhatsApp, par une vraie personne de l'équipe.",
        ),
    ),
    (
        "refresh",
        ("Changes included", "Modifications incluses"),
        (
            "Every package includes rounds of changes after you see the preview.",
            "Chaque formule inclut des séries de modifications après l'aperçu.",
        ),
    ),
    (
        "shield",
        ("Support after launch", "Un suivi après la mise en ligne"),
        (
            "We stay available after launch, and a Care Plan can look after your site for you.",
            "Nous restons disponibles après la mise en ligne, et le Care Plan peut gérer votre "
            "site pour vous.",
        ),
    ),
]

# FAQs: (question EN/FR, answer EN/FR, on Pricing, on Contact).
FAQS = [
    (
        ("How much does a website cost?", "Combien coûte un site web ?"),
        (
            "It depends on the number of pages and the features you need. Our packages show "
            "a starting price. After you send your brief, we reply with a fixed quote, so you "
            "know the full price before anything starts.",
            "Cela dépend du nombre de pages et des fonctionnalités. Nos formules indiquent un "
            "prix de départ. Après votre demande, nous envoyons un devis fixe : vous connaissez "
            "le prix total avant que quoi que ce soit ne commence.",
        ),
        True,
        False,
    ),
    (
        ("How long does it take?", "Combien de temps faut-il ?"),
        (
            "A Starter website is usually online in about 2 weeks. Larger sites and online "
            "stores take longer; your quote gives you a clear timeline.",
            "Un site Starter est généralement en ligne en 2 semaines environ. Les sites plus "
            "grands et les boutiques en ligne prennent plus de temps ; votre devis donne un "
            "délai clair.",
        ),
        True,
        False,
    ),
    (
        ("How do I pay?", "Comment payer ?"),
        (
            "You pay a deposit to start and the balance at launch. You can pay by MCB Juice, "
            "bank transfer or PayPal.",
            "Vous payez un acompte pour commencer et le solde à la mise en ligne, par MCB Juice, "
            "virement bancaire ou PayPal.",
        ),
        True,
        False,
    ),
    (
        ("Who owns the website and the domain?", "À qui appartiennent le site et le domaine ?"),
        (
            "You do. The domain is registered in your name, and once the website is paid for, "
            "it belongs to you.",
            "À vous. Le nom de domaine est enregistré à votre nom et, une fois payé, le site "
            "vous appartient.",
        ),
        True,
        False,
    ),
    (
        ("What is a round of changes?", "Qu'est-ce qu'une série de modifications ?"),
        (
            "After you see the preview, you send us one list of everything you want changed, "
            "and we make those changes. Your package says how many rounds are included; extra "
            "rounds are available if you need them.",
            "Après l'aperçu, vous nous envoyez une seule liste de tout ce que vous voulez "
            "modifier, et nous l'appliquons. Votre formule indique le nombre de séries incluses ; "
            "des séries supplémentaires sont possibles.",
        ),
        True,
        False,
    ),
    (
        ("What happens after launch?", "Que se passe-t-il après la mise en ligne ?"),
        (
            "Support after launch is included in our packages. After that, the monthly Care "
            "Plan covers hosting, backups, small updates and priority help, if you want it.",
            "Un suivi après la mise en ligne est inclus dans nos formules. Ensuite, le Care Plan "
            "mensuel couvre l'hébergement, les sauvegardes, les petites mises à jour et une "
            "aide prioritaire, si vous le souhaitez.",
        ),
        True,
        False,
    ),
    (
        ("Is the quote free?", "Le devis est-il gratuit ?"),
        (
            "Yes. The quote is free and you're under no obligation to go ahead.",
            "Oui. Le devis est gratuit et sans engagement.",
        ),
        True,
        True,
    ),
    (
        ("What happens after I send my brief?", "Que se passe-t-il après l'envoi de ma demande ?"),
        (
            "We reply within one business day, usually with a few questions or a short call. "
            "Then we send a fixed quote. If you're happy with it, a deposit starts the project.",
            "Nous répondons sous un jour ouvré, souvent avec quelques questions ou un court "
            "appel. Puis nous envoyons un devis fixe. S'il vous convient, un acompte lance le "
            "projet.",
        ),
        False,
        True,
    ),
    (
        ("What do I need to prepare?", "Que dois-je préparer ?"),
        (
            "Your logo, your texts and some photos, if you have them. If not, don't worry: "
            "we can help with branding, writing and photos.",
            "Votre logo, vos textes et quelques photos, si vous les avez. Sinon, pas "
            "d'inquiétude : nous pouvons vous aider pour l'identité visuelle, les textes et les "
            "photos.",
        ),
        False,
        True,
    ),
    (
        ("Can you redesign my existing website?", "Pouvez-vous refaire mon site actuel ?"),
        (
            "Yes. Add your current website's address to the brief and tell us what isn't "
            "working. We'll suggest what to keep and what to improve.",
            "Oui. Indiquez l'adresse de votre site actuel dans la demande et dites-nous ce qui "
            "ne va pas. Nous vous dirons quoi garder et quoi améliorer.",
        ),
        False,
        True,
    ),
]


def seed_trust_content(stdout=None):
    if not TrustPromise.objects.exists():
        for order, (icon, title, text) in enumerate(PROMISES):
            TrustPromise.objects.create(
                icon=icon,
                title_en=title[0],
                title_fr=title[1],
                text_en=text[0],
                text_fr=text[1],
                order=order,
            )
    if not FAQ.objects.exists():
        for order, (question, answer, on_pricing, on_contact) in enumerate(FAQS):
            FAQ.objects.create(
                question_en=question[0],
                question_fr=question[1],
                answer_en=answer[0],
                answer_fr=answer[1],
                on_pricing=on_pricing,
                on_contact=on_contact,
                order=order,
            )
    if stdout:
        stdout.write(f"Trust: {TrustPromise.objects.count()} promises, {FAQ.objects.count()} FAQs.")
