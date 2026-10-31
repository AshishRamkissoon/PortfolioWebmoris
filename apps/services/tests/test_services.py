import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.portfolio.tests.factories import ProjectFactory
from apps.services.models import Service, ServiceFAQ, ServiceGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def group():
    return ServiceGroup.objects.create(name="Web Development", slug="web")


def make_service(group, **kwargs):
    defaults = {"title": "Business Websites", "slug": "business", "summary": "Sites that sell."}
    return Service.objects.create(group=group, **{**defaults, **kwargs})


def test_list_groups_only_published_services(client, group):
    make_service(group, title="Shown")
    make_service(group, title="Hidden", slug="hidden", is_published=False)
    ServiceGroup.objects.create(name="Empty group", slug="empty")

    response = client.get("/en/services/")
    content = response.content.decode()
    assert [g.name for g in response.context["groups"]] == ["Web Development"]
    assert "Shown" in content
    assert "Hidden" not in content
    assert "Empty group" not in content


def test_detail_page_sections(client, group):
    service = make_service(
        group,
        body="Long description.",
        benefits="More leads\n\n  Faster site  ",
        deliverables="Design\nDevelopment",
    )
    ServiceFAQ.objects.create(service=service, question="How long?", answer="Two weeks.")
    content = client.get(service.get_absolute_url()).content.decode()
    for text in [
        "Long description.",
        "More leads",
        "Faster site",
        "Development",
        "How long?",
        "<details",
        "Let's talk about your Business Websites project.",
    ]:
        assert text in content, text


def test_admin_text_is_escaped_everywhere(client, group):
    service = make_service(group, title="Bots <script>alert(1)</script>", benefits="<b>x</b>")
    content = client.get(service.get_absolute_url()).content.decode()
    assert "<script>alert(1)</script>" not in content
    assert "<b>x</b>" not in content
    assert "talk about your Bots &lt;script&gt;" in content


def test_detail_related_projects_are_published_only(client, group):
    service = make_service(group)
    shown = ProjectFactory(title="Live project")
    hidden = ProjectFactory(title="Draft project", is_published=False)
    service.related_projects.set([shown, hidden])

    response = client.get(service.get_absolute_url())
    assert list(response.context["related_projects"]) == [shown]


def test_other_services_in_same_group(client, group):
    service = make_service(group)
    sibling = make_service(group, title="E-commerce", slug="shop")
    make_service(group, title="Draft", slug="draft", is_published=False)
    other_group = ServiceGroup.objects.create(name="AI", slug="ai")
    make_service(other_group, title="Chatbots", slug="chat")

    response = client.get(service.get_absolute_url())
    assert list(response.context["other_services"]) == [sibling]


def test_unpublished_service_is_404(client, group):
    service = make_service(group, is_published=False)
    assert client.get(service.get_absolute_url()).status_code == 404


def test_nav_marks_services(client, group):
    content = client.get(make_service(group).get_absolute_url()).content.decode()
    assert 'href="/en/services/" class="nav-link" aria-current="page"' in content


def test_service_admin(client, group):
    admin = get_user_model().objects.create_superuser("o", "o@example.com", "pw-123456789")
    client.force_login(admin)
    service = make_service(group)
    base = f"/{settings.ADMIN_URL}services/service/"
    for url in [base, f"{base}add/", f"{base}{service.pk}/change/"]:
        assert client.get(url).status_code == 200, url
