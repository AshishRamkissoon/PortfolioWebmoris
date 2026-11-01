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


def test_home_with_demo_content(client):
    call_command("seed_demo", stdout=StringIO())
    response = client.get("/en/")
    content = response.content.decode()
    assert response.context["featured_projects"]
    assert response.context["featured_templates"]
    assert len(response.context["service_groups"]) == 2
    for text in ["data-hscroll", "AI Chatbots", "Lagon Bistro", "Discover", "Get a Quote"]:
        assert text in content, text


def test_seed_demo_counts_and_markers():
    out = StringIO()
    call_command("seed_demo", stdout=out)
    call_command("seed_demo", stdout=out)
    assert Service.objects.count() == 6
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
