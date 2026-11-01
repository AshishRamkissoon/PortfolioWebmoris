"""Demo content for the About page, team, process and legal pages. Replace in admin.

Team members are clearly marked "(demo)", and the legal pages say they must be replaced:
neither should ever go live as if it were real.
"""

from .models import AboutPage, LegalPage, ProcessStep, TeamMember

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
