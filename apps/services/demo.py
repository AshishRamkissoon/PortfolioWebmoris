"""Demo services for `manage.py seed_demo`. Replace or edit in admin."""

from apps.portfolio.models import ProjectCategory

from .models import Service, ServiceFAQ, ServiceGroup

GROUPS = [
    {
        "slug": "web-development",
        "name": ("Web Development", "Développement web"),
        "intro": (
            "Fast, modern websites designed to turn visitors into customers.",
            "Des sites rapides et modernes conçus pour transformer les visiteurs en clients.",
        ),
        "services": [
            {
                "slug": "business-websites",
                "icon": "code",
                "category": "business",
                "title": ("Business Websites", "Sites vitrines"),
                "summary": (
                    "A professional site that builds trust and brings in enquiries.",
                    "Un site professionnel qui inspire confiance et génère des demandes.",
                ),
                "body": (
                    "We design and build websites that load fast, look great on every screen and "
                    "are structured so Google understands them. You get a site that explains what "
                    "you do and makes it easy for customers to get in touch.",
                    "Nous concevons et développons des sites rapides, beaux sur tous les écrans et "
                    "structurés pour que Google les comprenne. Vous obtenez un site qui explique "
                    "clairement ce que vous faites et qui facilite la prise de contact.",
                ),
                "deliverables": (
                    "Custom design: built around your brand, not a generic theme\n"
                    "Mobile first: looks and works great on phones, tablets and desktops\n"
                    "Fast loading: optimised images and clean code\n"
                    "SEO foundations: clean structure, meta tags and structured data\n"
                    "Easy to update: change texts and photos yourself in a simple admin\n"
                    "WhatsApp and contact forms: customers reach you in one tap",
                    "Design sur mesure : pensé pour votre marque, pas un thème générique\n"
                    "Adapté au mobile : parfait sur téléphone, tablette et ordinateur\n"
                    "Chargement rapide : images optimisées et code propre\n"
                    "Bases SEO : structure claire, balises meta et données structurées\n"
                    "Facile à modifier : changez textes et photos vous-même\n"
                    "WhatsApp et formulaires : vos clients vous contactent en un geste",
                ),
                "benefits": (
                    "A brand image customers trust\nMore enquiries from the same visitors\n"
                    "Found on Google when people search for what you do",
                    "Une image de marque qui inspire confiance\n"
                    "Plus de demandes avec les mêmes visiteurs\n"
                    "Trouvé sur Google quand on cherche ce que vous faites",
                ),
            },
            {
                "slug": "e-commerce",
                "icon": "cart",
                "category": "ecommerce",
                "title": ("E-commerce Stores", "Boutiques en ligne"),
                "summary": (
                    "Sell online with secure payments, delivery options and stock management.",
                    "Vendez en ligne avec paiements sécurisés, livraison et gestion de stock.",
                ),
                "body": (
                    "We build online stores that are easy to shop on a phone and easy for you to "
                    "manage. Customers pay securely with MCB Juice, PayPal or bank transfer, and "
                    "you follow every order from one dashboard.",
                    "Nous créons des boutiques en ligne faciles à utiliser sur mobile et simples à "
                    "gérer. Vos clients paient en toute sécurité par MCB Juice, PayPal ou virement, "
                    "et vous suivez chaque commande depuis un seul tableau de bord.",
                ),
                "deliverables": (
                    "Local payments: MCB Juice, bank transfer and PayPal\n"
                    "Orders and stock: manage products, orders and inventory in one place\n"
                    "Product pages that sell: clear photos, prices and options\n"
                    "Delivery and pickup: options set up for Mauritius\n"
                    "Order emails: automatic confirmations for you and your customers",
                    "Paiements locaux : MCB Juice, virement et PayPal\n"
                    "Commandes et stock : produits, commandes et inventaire au même endroit\n"
                    "Fiches produits qui vendent : photos claires, prix et options\n"
                    "Livraison et retrait : options adaptées à Maurice\n"
                    "E-mails de commande : confirmations automatiques pour vous et vos clients",
                ),
                "benefits": (
                    "Sell 24/7, even when the shop is closed\nLess time spent on WhatsApp orders\n"
                    "Reach customers all over the island",
                    "Vendez 24h/24, même boutique fermée\n"
                    "Moins de temps passé sur les commandes WhatsApp\n"
                    "Touchez des clients dans toute l'île",
                ),
            },
            {
                "slug": "landing-pages",
                "icon": "rocket",
                "category": "landing",
                "title": ("Landing Pages", "Pages d'atterrissage"),
                "summary": (
                    "High-converting pages for launches, campaigns and ads.",
                    "Des pages performantes pour vos lancements, campagnes et publicités.",
                ),
                "body": (
                    "A landing page has one job: turn visitors from an ad, a post or a QR code into "
                    "enquiries. We write, design and build it around a single clear offer.",
                    "Une page d'atterrissage a un seul objectif : transformer les visiteurs venus "
                    "d'une publicité, d'un post ou d'un QR code en demandes. Nous la rédigeons, la "
                    "concevons et la développons autour d'une offre claire.",
                ),
                "deliverables": (
                    "One clear message: built around a single offer or event\n"
                    "Fast to launch: ready in days, not weeks\n"
                    "Lead capture: form, WhatsApp button or booking link\n"
                    "Tracking: see how many visitors become enquiries",
                    "Un message clair : pensée autour d'une seule offre ou d'un événement\n"
                    "Lancement rapide : prête en quelques jours\n"
                    "Capture de prospects : formulaire, bouton WhatsApp ou lien de réservation\n"
                    "Suivi : voyez combien de visiteurs deviennent des demandes",
                ),
                "benefits": (
                    "More results from your ad budget\nA page ready for every campaign\n"
                    "Clear numbers on what works",
                    "Plus de résultats pour votre budget publicitaire\n"
                    "Une page prête pour chaque campagne\nDes chiffres clairs sur ce qui fonctionne",
                ),
            },
            {
                "slug": "redesign-maintenance",
                "icon": "refresh",
                "category": None,
                "title": ("Redesign & Maintenance", "Refonte & maintenance"),
                "summary": (
                    "Give an old site a new life, then keep it fast, secure and up to date.",
                    "Donnez une seconde vie à votre site et gardez-le rapide, sûr et à jour.",
                ),
                "body": (
                    "A website is never really finished. We refresh old sites so they look modern "
                    "and load fast, then keep them updated, backed up and secure so you can focus "
                    "on your business.",
                    "Un site n'est jamais vraiment terminé. Nous modernisons les anciens sites pour "
                    "qu'ils soient beaux et rapides, puis nous les gardons à jour, sauvegardés et "
                    "sécurisés pour que vous puissiez vous concentrer sur votre activité.",
                ),
                "deliverables": (
                    "Redesign: a modern look without losing your Google ranking\n"
                    "Updates: software and security updates every month\n"
                    "Daily backups: stored off-site and restored quickly if needed\n"
                    "Monitoring: we check that the site is online and fast\n"
                    "Small changes: texts, photos and prices updated for you",
                    "Refonte : un look moderne sans perdre votre référencement\n"
                    "Mises à jour : logiciels et sécurité, chaque mois\n"
                    "Sauvegardes quotidiennes : stockées hors site, restaurées rapidement\n"
                    "Surveillance : nous vérifions que le site est en ligne et rapide\n"
                    "Petites modifications : textes, photos et prix mis à jour pour vous",
                ),
                "benefits": (
                    "A site that keeps up with your business\nNo technical worries\n"
                    "One local team to call",
                    "Un site qui suit l'évolution de votre activité\nAucun souci technique\n"
                    "Une équipe locale à appeler",
                ),
            },
            {
                "slug": "hosting-email",
                "icon": "server",
                "category": None,
                "title": ("Hosting & Email", "Hébergement & e-mail"),
                "summary": (
                    "Fast, secure hosting and professional email at your own domain.",
                    "Un hébergement rapide et sécurisé, et des e-mails professionnels à votre nom.",
                ),
                "body": (
                    "We host your website on fast, secure servers and look after the technical "
                    "side for you. Your email becomes you@yourbusiness.mu instead of a free Gmail "
                    "address, so every message looks professional.",
                    "Nous hébergeons votre site sur des serveurs rapides et sécurisés et gérons la "
                    "partie technique pour vous. Votre e-mail devient vous@votreentreprise.mu au "
                    "lieu d'une adresse Gmail gratuite : chaque message fait plus professionnel.",
                ),
                "deliverables": (
                    "Fast, secure hosting: SSL certificate and CDN included\n"
                    "Professional email: mailboxes at your own domain\n"
                    "Domain names: .mu and .com registered and renewed for you\n"
                    "Backups and monitoring: your site is checked and backed up daily\n"
                    "Local support: help by WhatsApp and phone",
                    "Hébergement rapide et sécurisé : certificat SSL et CDN inclus\n"
                    "E-mail professionnel : boîtes mail à votre nom de domaine\n"
                    "Noms de domaine : .mu et .com enregistrés et renouvelés pour vous\n"
                    "Sauvegardes et surveillance : site vérifié et sauvegardé chaque jour\n"
                    "Support local : aide par WhatsApp et téléphone",
                ),
                "benefits": (
                    "A business email customers trust\nNo renewal dates to remember\n"
                    "One contact for your site, domain and email",
                    "Une adresse e-mail qui inspire confiance\n"
                    "Aucune date de renouvellement à retenir\n"
                    "Un seul contact pour le site, le domaine et les e-mails",
                ),
            },
        ],
    },
    {
        "slug": "ai-marketing",
        "name": ("AI Marketing", "Marketing IA"),
        "intro": (
            "Put AI to work on your marketing so you can focus on your business.",
            "Laissez l'IA travailler sur votre marketing pendant que vous gérez votre entreprise.",
        ),
        "services": [
            {
                "slug": "ai-content-social-media",
                "icon": "sparkles",
                "category": "ai-marketing",
                "title": ("AI Content & Social Media", "Contenu IA & réseaux sociaux"),
                "summary": (
                    "AI-generated posts, captions, images and videos, planned and published for "
                    "you.",
                    "Publications, légendes, images et vidéos générées par IA, planifiées et "
                    "publiées pour vous.",
                ),
                "body": (
                    "We plan, create and publish your social media content, using AI to work "
                    "faster and keep you posting consistently. A person checks every post before "
                    "it goes out.",
                    "Nous planifions, créons et publions vos contenus sur les réseaux sociaux, avec "
                    "l'IA pour aller plus vite et publier régulièrement. Chaque publication est "
                    "relue par une personne avant d'être mise en ligne.",
                ),
                "deliverables": (
                    "Monthly content plan: posts planned around your offers and events\n"
                    "Captions in English and French: written for your audience\n"
                    "Images and short videos: created and edited with AI tools\n"
                    "Scheduling: posts published at the best times\n"
                    "Monthly report: what worked and what to try next",
                    "Planning mensuel : publications prévues selon vos offres et événements\n"
                    "Légendes en anglais et en français : écrites pour votre audience\n"
                    "Images et vidéos courtes : créées et montées avec des outils IA\n"
                    "Programmation : publications aux meilleurs moments\n"
                    "Rapport mensuel : ce qui a marché et ce qu'il faut essayer ensuite",
                ),
                "benefits": (
                    "Post regularly without spending your evenings on it\n"
                    "A consistent look on every platform\nMore people who know your business",
                    "Publiez régulièrement sans y passer vos soirées\n"
                    "Une image cohérente sur chaque réseau\n"
                    "Plus de personnes qui connaissent votre entreprise",
                ),
            },
            {
                "slug": "ai-chatbots",
                "icon": "chat",
                "category": "ai-marketing",
                "title": ("AI Chatbots", "Chatbots IA"),
                "summary": (
                    "Website and WhatsApp chatbots that answer customers and capture leads 24/7.",
                    "Des chatbots site web et WhatsApp qui répondent aux clients et captent des "
                    "prospects 24h/24.",
                ),
                "body": (
                    "Our chatbots answer common questions on your website and WhatsApp, day and "
                    "night, and pass real enquiries to you with the customer's details.",
                    "Nos chatbots répondent aux questions fréquentes sur votre site et sur "
                    "WhatsApp, jour et nuit, et vous transmettent les vraies demandes avec les "
                    "coordonnées du client.",
                ),
                "deliverables": (
                    "Trained on your business: prices, opening hours, services and FAQs\n"
                    "Website and WhatsApp: one assistant on both channels\n"
                    "Lead capture: names and numbers sent straight to you\n"
                    "English and French: answers in the customer's language",
                    "Formé sur votre activité : prix, horaires, services et FAQ\n"
                    "Site web et WhatsApp : un seul assistant sur les deux canaux\n"
                    "Capture de prospects : noms et numéros envoyés directement\n"
                    "Anglais et français : réponses dans la langue du client",
                ),
                "benefits": (
                    "Never miss an enquiry at night\nLess time answering the same questions\n"
                    "Faster replies for your customers",
                    "Ne manquez plus une demande la nuit\n"
                    "Moins de temps à répondre aux mêmes questions\n"
                    "Des réponses plus rapides pour vos clients",
                ),
            },
        ],
    },
    {
        "slug": "brand-content",
        "name": ("Brand & Content", "Image & contenu"),
        "intro": (
            "Logos, print, photos and videos that make your business look its best.",
            "Logos, impressions, photos et vidéos pour valoriser votre entreprise.",
        ),
        "services": [
            {
                "slug": "branding-print",
                "icon": "brush",
                "category": None,
                "title": ("Branding & Print", "Identité visuelle & impression"),
                "summary": (
                    "Logos, flyers, menus and banners that make your brand look consistent.",
                    "Logos, flyers, menus et banderoles pour une image de marque cohérente.",
                ),
                "body": (
                    "Your brand should look the same on your website, your shop front and your "
                    "flyers. We design your logo and print materials and deliver files ready for "
                    "local printers.",
                    "Votre marque doit avoir la même allure sur votre site, votre devanture et vos "
                    "flyers. Nous concevons votre logo et vos supports imprimés et livrons des "
                    "fichiers prêts pour les imprimeurs locaux.",
                ),
                "deliverables": (
                    "Logo and brand colours: a simple identity you can use everywhere\n"
                    "Flyers, brochures and menus: designed to be read at a glance\n"
                    "Roll-ups, banners and signage: large formats that stand out\n"
                    "Print-ready files: PDFs with the right colours and margins for local printers",
                    "Logo et couleurs : une identité simple, utilisable partout\n"
                    "Flyers, brochures et menus : conçus pour être lus d'un coup d'œil\n"
                    "Roll-ups, banderoles et enseignes : des grands formats qui se remarquent\n"
                    "Fichiers prêts à imprimer : PDF aux bonnes couleurs et marges",
                ),
                "benefits": (
                    "A brand people recognise\nThe same look online and offline\n"
                    "No back-and-forth with the printer",
                    "Une marque que l'on reconnaît\nLa même image en ligne et hors ligne\n"
                    "Pas d'allers-retours avec l'imprimeur",
                ),
            },
            {
                "slug": "photo-video",
                "icon": "camera",
                "category": None,
                "title": ("Photo & Video", "Photo & vidéo"),
                "summary": (
                    "Product photos, portraits and short videos for your website and social media.",
                    "Photos produits, portraits et vidéos courtes pour votre site et vos réseaux.",
                ),
                "body": (
                    "Real photos and videos of your products, team and place make a website far "
                    "more convincing than stock images. We shoot, edit and deliver them ready for "
                    "your website and social media.",
                    "De vraies photos et vidéos de vos produits, de votre équipe et de votre lieu "
                    "rendent un site bien plus convaincant que des images de banque. Nous les "
                    "réalisons, les retouchons et les livrons prêtes pour votre site et vos "
                    "réseaux.",
                ),
                "deliverables": (
                    "Product photos: clean shots for your website and online store\n"
                    "Portraits: team and founder photos for your About page\n"
                    "Short videos and reels: promo clips for Instagram, TikTok and Facebook\n"
                    "Editing included: colour, captions and music\n"
                    "Web-ready files: optimised so your site stays fast",
                    "Photos produits : des images nettes pour votre site et votre boutique\n"
                    "Portraits : photos d'équipe et du fondateur pour votre page À propos\n"
                    "Vidéos courtes et reels : clips promo pour Instagram, TikTok et Facebook\n"
                    "Montage inclus : couleurs, sous-titres et musique\n"
                    "Fichiers prêts pour le web : optimisés pour garder votre site rapide",
                ),
                "benefits": (
                    "Show customers the real thing\nContent for months of social media posts\n"
                    "A site that stands out from stock photos",
                    "Montrez à vos clients la réalité\nDu contenu pour des mois de publications\n"
                    "Un site qui se démarque des photos de banque",
                ),
            },
        ],
    },
]

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


def translated(data, *fields):
    """{"title": ("EN", "FR")} -> {"title_en": "EN", "title_fr": "FR"}."""
    return {f"{f}_{lang}": data[f][i] for f in fields for i, lang in enumerate(("en", "fr"))}


def seed_services(stdout=None):
    created = 0
    for group_order, data in enumerate(GROUPS, start=1):
        group, _ = ServiceGroup.objects.get_or_create(
            slug=data["slug"],
            defaults={**translated(data, "name", "intro"), "order": group_order},
        )
        for order, item in enumerate(data["services"], start=1):
            if Service.objects.filter(slug=item["slug"]).exists():
                continue
            service = Service.objects.create(
                group=group,
                slug=item["slug"],
                icon=item["icon"],
                order=order,
                **translated(item, "title", "summary", "body", "benefits", "deliverables"),
            )
            if item["category"]:
                cat = ProjectCategory.objects.filter(slug=item["category"]).first()
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
