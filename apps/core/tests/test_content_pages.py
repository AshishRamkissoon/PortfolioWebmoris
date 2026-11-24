from io import StringIO

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.core.models import AboutPage, LegalPage, ProcessStep, TeamMember
from apps.core.templatetags.core_tags import lines
from apps.portfolio.models import Project
from apps.portfolio.tests.factories import ProjectFactory
from apps.readymade.models import WebsiteTemplate
from apps.services.models import Service

pytestmark = pytest.mark.django_db


def test_lines_filter():
    assert lines("One\n\n  Two  \r\nThree") == ["One", "Two", "Three"]
    assert lines(None) == []


def test_about_values_and_tools_parsing():
    about = AboutPage(values="Quality: we care\nSpeed\n: no title\n", tools="Django, , GSAP")
    assert about.values_list == [("Quality", "we care"), ("Speed", "")]
    assert about.tools_list == ["Django", "GSAP"]


def test_team_photo_square_keeps_the_top_of_a_tall_portrait(settings, tmp_path):
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    settings.MEDIA_ROOT = tmp_path
    portrait = Image.new("RGB", (100, 200), "blue")
    portrait.paste(Image.new("RGB", (100, 20), "red"), (0, 0))  # the "head"
    buffer = BytesIO()
    portrait.save(buffer, "PNG")
    member = TeamMember.objects.create(
        name="Tall", role="Director", photo=SimpleUploadedFile("p.png", buffer.getvalue())
    )
    member.photo_square.generate()
    with Image.open(member.photo_square.path) as square:
        red, green, blue = square.convert("RGB").getpixel((300, 5))
    assert square.size == (600, 600) and red > 200 and blue < 60


def test_about_page(client):
    about = AboutPage.load()
    about.story = "Our story."
    about.mission = "Our mission."
    about.values = "Quality: details matter"
    about.tools = "Django, GSAP"
    about.save()
    TeamMember.objects.create(name="Jane Doe", role="Designer")
    TeamMember.objects.create(name="Hidden Person", role="Ex", is_active=False)
    ProcessStep.objects.create(title="Discover", description="We listen.")

    content = client.get("/en/about/").content.decode()
    for text in [
        "Our story.",
        "Our mission.",
        "details matter",
        "GSAP",
        "Jane Doe",
        "JD",
        "Discover",
    ]:
        assert text in content, text
    assert "Hidden Person" not in content


def test_legal_pages(client):
    LegalPage.objects.create(
        kind="privacy",
        title_en="Privacy",
        title_fr="Confidentialité",
        body_en="We protect your data.",
    )
    assert "We protect your data." in client.get("/en/privacy/").content.decode()
    assert "Confidentialité" in client.get("/fr/privacy/").content.decode()
    assert client.get("/en/terms/").status_code == 404


def test_legal_body_is_escaped(client):
    LegalPage.objects.create(kind="terms", title="Terms", body="<script>alert(1)</script>")
    content = client.get("/en/terms/").content.decode()
    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;" in content


def test_home_uses_featured_content(client):
    featured = ProjectFactory(title="Star project", is_featured=True)
    ProjectFactory(title="Regular project")
    response = client.get("/en/")
    assert list(response.context["featured_projects"]) == [featured]
    assert list(response.context["packages"]) == []


def _home_sections(content):
    """Positions of the projects, ready-made and services sections on the home page."""
    markers = ("data-hscroll", "Launch fast with a ready-made site.", "What we do")
    return [content.index(marker) for marker in markers]


def test_home_leads_with_ready_made_sites_while_work_is_in_progress(client):
    call_command("seed_demo", stdout=StringIO())
    Project.objects.update(status=Project.Status.IN_PROGRESS)
    content = client.get("/en/").content.decode()
    work, ready, services = _home_sections(content)
    assert "Work in progress" in content
    assert ready < services < work


def test_home_leads_with_finished_work_once_there_is_a_showcase(client):
    call_command("seed_demo", stdout=StringIO())
    ProjectFactory.create_batch(3, status=Project.Status.COMPLETED, is_featured=True)
    content = client.get("/en/").content.decode()
    work, ready, services = _home_sections(content)
    assert "Selected work" in content
    assert work < ready < services
    assert content.count("data-hscroll-track") == 1


def test_home_with_demo_content(client):
    call_command("seed_demo", stdout=StringIO())
    response = client.get("/en/")
    content = response.content.decode()
    assert response.context["featured_projects"]
    assert response.context["featured_templates"]
    assert len(response.context["service_groups"]) == 3
    for text in ["data-hscroll", "AI Chatbots", "Lagon Bistro", "Discover", "Get a Quote"]:
        assert text in content, text


def test_seed_demo_counts_and_markers():
    out = StringIO()
    call_command("seed_demo", stdout=out)
    call_command("seed_demo", stdout=out)
    assert Service.objects.count() == 9
    assert WebsiteTemplate.objects.count() == 6
    assert ProcessStep.objects.count() == 5
    assert all("(demo)" in m.name for m in TeamMember.objects.all())
    assert all(p.body.startswith("DEMO TEXT") for p in LegalPage.objects.all())
    # Demo templates never link to a demo site that doesn't exist.
    assert not WebsiteTemplate.objects.exclude(demo_url="").exists()
    assert Service.objects.get(slug="ai-chatbots").related_projects.exists()
    assert Project.objects.count() == 7


def test_singleton_and_content_admin(client):
    admin = get_user_model().objects.create_superuser("o", "o@example.com", "pw-123456789")
    client.force_login(admin)
    base = f"/{settings.ADMIN_URL}core/"
    response = client.get(f"{base}aboutpage/")
    assert response.status_code == 302
    assert client.get(response["Location"]).status_code == 200
    for model in ["teammember", "processstep", "legalpage"]:
        assert client.get(f"{base}{model}/").status_code == 200
        assert client.get(f"{base}{model}/add/").status_code == 200


def test_promises_on_home_pricing_and_contact(client):
    from apps.core.models import TrustPromise

    TrustPromise.objects.create(
        icon="key", title_en="Your domain", title_fr="Votre domaine", text_en="Yours."
    )
    TrustPromise.objects.create(title_en="Hidden promise", text_en="No.", is_active=False)
    for path in ("/en/", "/en/pricing/", "/en/contact/"):
        content = client.get(path).content.decode()
        assert "Our promises" in content and "Your domain" in content, path
        assert "Hidden promise" not in content, path
    assert "Votre domaine" in client.get("/fr/pricing/").content.decode()


def test_no_promises_no_section(client):
    assert "Our promises" not in client.get("/en/").content.decode()


def test_faqs_are_shown_on_the_pages_picked_in_admin(client):
    from apps.core.models import FAQ

    FAQ.objects.create(question_en="Pricing only?", answer_en="Yes.", on_pricing=True)
    FAQ.objects.create(
        question_en="Contact only?", answer_en="Yes.", on_pricing=False, on_contact=True
    )
    FAQ.objects.create(question_en="Hidden?", answer_en="Yes.", on_contact=True, is_active=False)
    pricing = client.get("/en/pricing/").content.decode()
    contact = client.get("/en/contact/").content.decode()
    assert "Pricing only?" in pricing and "Contact only?" not in pricing
    assert "Contact only?" in contact and "Pricing only?" not in contact
    assert "Hidden?" not in pricing + contact
    assert pricing.count('"@type": "FAQPage"') == 1


def test_faq_is_escaped_and_structured_data_is_safe(client):
    from apps.core.models import FAQ

    FAQ.objects.create(question_en="<b>Bold?</b>", answer_en="</script><script>alert(1)</script>")
    response = client.get("/en/pricing/")
    content = response.content.decode()
    assert "<script>alert(1)</script>" not in content
    assert "&lt;b&gt;Bold?&lt;/b&gt;" in content
    nonce = response.context["csp_nonce"]
    assert f'<script type="application/ld+json" nonce="{nonce}">' in content


def test_no_faqs_no_section(client):
    content = client.get("/en/contact/").content.decode()
    assert "Questions we often get" not in content and "FAQPage" not in content


def test_trust_models_are_in_admin():
    from django.contrib import admin

    from apps.core.models import FAQ, TrustPromise

    assert FAQ in admin.site._registry and TrustPromise in admin.site._registry


def test_seed_trust_content_is_idempotent():
    from apps.core.demo import FAQS, PROMISES, seed_trust_content
    from apps.core.models import FAQ, TrustPromise

    seed_trust_content()
    seed_trust_content()
    assert TrustPromise.objects.count() == len(PROMISES)
    assert FAQ.objects.count() == len(FAQS)
    assert (
        FAQ.objects.filter(on_contact=True).exists()
        and FAQ.objects.filter(on_pricing=True).exists()
    )
    assert not TrustPromise.objects.filter(title_fr="").exists()


# --- Phase 17: Site settings control the recent Home, promises and FAQ changes


def _settings(**fields):
    from apps.core.models import SiteSettings

    s = SiteSettings.load()
    for name, value in fields.items():
        setattr(s, name, value)
    s.save()
    return s


def test_hero_texts_from_site_settings_with_defaults(client):
    content = client.get("/en/").content.decode()
    assert "We build websites that" in content and "Start my website" in content
    _settings(
        hero_title_en="Websites for",
        hero_highlight_en="island businesses.",
        hero_cta_label_en="Get my quote",
        hero_tags_en="Fast\nBilingual",
    )
    s = _settings()
    assert s.hero_texts["tags"] == ["Fast", "Bilingual", "WhatsApp button"]
    content = client.get("/en/").content.decode()
    assert "Websites for" in content and "island businesses." in content
    assert "Get my quote" in content and "We build websites that" not in content
    # French left blank: falls back to the English text (modeltranslation), never empty.
    assert "Websites for" in client.get("/fr/").content.decode()


def test_hero_badge_auto_chosen_and_off(client):
    from apps.core.models import TeamMember
    from apps.core.placeholders import placeholder_image

    first = TeamMember.objects.create(
        name="First Face",
        role_en="Director",
        order=0,
        photo=placeholder_image("a", size=(80, 80), name="a.png"),
    )
    second = TeamMember.objects.create(
        name="Second Face",
        role_en="Designer",
        order=1,
        photo=placeholder_image("b", size=(80, 80), name="b.png"),
    )
    no_photo = TeamMember.objects.create(name="No Photo", role_en="Writer", order=2)
    assert "First Face" in client.get("/en/").content.decode()

    _settings(hero_badge="chosen", hero_badge_member=second, hero_badge_text_en="Say hi")
    content = client.get("/en/").content.decode()
    assert "Second Face" in content and "Say hi" in content and "First Face" not in content

    _settings(hero_badge_member=no_photo)
    assert "Say hi" not in client.get("/en/").content.decode()

    _settings(hero_badge="off", hero_badge_member=first)
    assert "First Face" not in client.get("/en/").content.decode()


def test_projects_position_and_showcase_threshold(client):
    call_command("seed_demo", stdout=StringIO())
    Project.objects.update(status=Project.Status.IN_PROGRESS)

    def order():
        work, ready, services = _home_sections(client.get("/en/").content.decode())
        return work < ready

    assert order() is False  # automatic, nothing finished: ready-made first
    _settings(home_projects_position="top")
    assert order() is True
    _settings(home_projects_position="auto", showcase_min_completed=1)
    Project.objects.filter(pk=Project.objects.first().pk).update(status=Project.Status.COMPLETED)
    content = client.get("/en/").content.decode()
    assert "Selected work" in content and order() is True
    _settings(home_projects_position="after_services")
    assert order() is False


def test_promises_pages_and_heading_from_site_settings(client):
    from apps.core.models import TrustPromise

    TrustPromise.objects.create(title_en="Fixed quote", text_en="Always.")
    _settings(promises_on_pricing=False, promises_title_en="What you can count on")
    home = client.get("/en/").content.decode()
    assert "What you can count on" in home and "No surprises" not in home
    assert "Fixed quote" not in client.get("/en/pricing/").content.decode()
    assert "Fixed quote" in client.get("/en/contact/").content.decode()
    _settings(promises_on_contact=False)
    assert "Fixed quote" not in client.get("/en/contact/").content.decode()


def test_faq_heading_from_site_settings(client):
    from apps.core.models import FAQ

    FAQ.objects.create(question_en="Is it free?", answer_en="Yes.")
    assert "Questions we often get" in client.get("/en/pricing/").content.decode()
    _settings(faq_title_en="Good to know")
    content = client.get("/en/pricing/").content.decode()
    assert "Good to know" in content and "Questions we often get" not in content
    assert "Questions fréquentes" not in client.get("/fr/pricing/").content.decode()


def test_site_settings_admin_shows_the_new_controls(admin_client):
    from django.urls import reverse

    from apps.core.models import SiteSettings

    url = reverse("admin:core_sitesettings_change", args=[SiteSettings.load().pk])
    content = admin_client.get(url).content.decode()
    for text in [
        "Home hero",
        "Home hero: team badge",
        "Home sections",
        "Promises and FAQ",
        'name="hero_title_fr"',
        'name="hero_badge_member"',
        'name="home_projects_position"',
        'name="showcase_min_completed"',
        'name="promises_on_contact"',
        'name="faq_title_en"',
    ]:
        assert text in content, text
