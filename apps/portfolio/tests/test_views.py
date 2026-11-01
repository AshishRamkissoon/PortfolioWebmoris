import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.portfolio.models import Project
from apps.portfolio.views import PAGE_SIZE

from .factories import (
    ProjectCategoryFactory,
    ProjectFactory,
    ProjectImageFactory,
    ProjectMetricFactory,
)

pytestmark = pytest.mark.django_db

LIST = "/en/portfolio/"
HTMX_GRID = {"HX-Request": "true", "HX-Target": "project-grid"}
HTMX_MORE = {"HX-Request": "true", "HX-Target": "load-more"}


def titles(response):
    return [p.title for p in response.context["page"].object_list]


# --- List -------------------------------------------------------------------


def test_list_shows_only_published_projects(client):
    ProjectFactory(title="Visible")
    ProjectFactory(title="Hidden", is_published=False)
    response = client.get(LIST)
    assert titles(response) == ["Visible"]
    assert "Hidden" not in response.content.decode()


def test_filter_by_category(client):
    shop = ProjectCategoryFactory(slug="shop")
    ProjectFactory(title="Store", categories=[shop])
    ProjectFactory(title="Brochure")
    response = client.get(f"{LIST}?category=shop")
    assert titles(response) == ["Store"]
    assert response.context["active_category"] == shop


def test_unknown_category_shows_everything(client):
    ProjectFactory.create_batch(2)
    response = client.get(f"{LIST}?category=does-not-exist")
    assert len(titles(response)) == 2
    assert response.context["active_category"] is None


def test_tabs_only_list_categories_with_published_projects(client):
    used = ProjectCategoryFactory(name="Used")
    ProjectCategoryFactory(name="Empty")
    hidden_only = ProjectCategoryFactory(name="HiddenOnly")
    ProjectFactory(categories=[used])
    ProjectFactory(categories=[hidden_only], is_published=False)
    names = [c.name for c in client.get(LIST).context["categories"]]
    assert names == ["Used"]


def test_full_page_works_without_htmx(client):
    ProjectFactory()
    content = client.get(LIST).content.decode()
    assert "<html" in content
    assert 'id="project-grid"' in content


def test_htmx_filter_returns_grid_partial(client):
    ProjectFactory()
    response = client.get(LIST, headers=HTMX_GRID)
    content = response.content.decode()
    assert "<html" not in content
    assert content.lstrip().startswith("<section") or 'id="project-grid"' in content
    assert "HX-Request" in response["Vary"]


def test_pagination_and_load_more(client):
    ProjectFactory.create_batch(PAGE_SIZE + 2)
    first = client.get(LIST)
    assert len(titles(first)) == PAGE_SIZE
    assert 'id="load-more"' in first.content.decode()

    more = client.get(f"{LIST}?page=2", headers=HTMX_MORE)
    content = more.content.decode()
    assert "<html" not in content and 'id="project-grid"' not in content
    assert content.count("<article") == 2
    assert 'id="load-more"' not in content


def test_load_more_keeps_category(client):
    cat = ProjectCategoryFactory(slug="web")
    ProjectFactory.create_batch(PAGE_SIZE + 1, categories=[cat])
    content = client.get(f"{LIST}?category=web").content.decode()
    assert "?page=2&amp;category=web" in content


def test_empty_portfolio(client):
    response = client.get(LIST)
    assert response.status_code == 200
    assert "No projects to show yet" in response.content.decode()


def test_card_buttons(client):
    ProjectFactory(live_url="https://client.example.com", video_url="https://youtu.be/dQw4w9WgXcQ")
    content = client.get(LIST).content.decode()
    assert 'href="https://client.example.com" target="_blank" rel="noopener noreferrer"' in content
    assert 'data-kind="embed"' in content
    assert "youtube-nocookie.com/embed/dQw4w9WgXcQ" in content


# --- Detail -----------------------------------------------------------------


def test_detail_renders_all_sections(client):
    project = ProjectFactory(
        results="Great results.",
        tech_stack="Django, Tailwind",
        video_url="https://vimeo.com/123456",
        live_url="https://client.example.com",
    )
    ProjectMetricFactory(project=project, value="+120%", label="traffic")
    ProjectImageFactory(project=project, kind="desktop", caption="Home")
    ProjectImageFactory(project=project, kind="mobile", caption="Phone")

    response = client.get(project.get_absolute_url())
    content = response.content.decode()
    assert response.status_code == 200
    for text in [
        "The Challenge",
        "The Solution",
        "The Results",
        "+120%",
        "Tailwind",
        "player.vimeo.com/video/123456",
        'id="video"',
        "data-lightbox-item",
        "og:image",
    ]:
        assert text in content, text
    assert [i.caption for i in response.context["desktop_images"]] == ["Home"]
    assert [i.caption for i in response.context["mobile_images"]] == ["Phone"]


def test_detail_hides_optional_sections(client):
    content = client.get(ProjectFactory().get_absolute_url()).content.decode()
    assert 'id="video"' not in content
    assert "The Results" not in content
    assert "Screenshots" not in content


def test_unpublished_project_is_404(client):
    project = ProjectFactory(is_published=False)
    assert client.get(project.get_absolute_url()).status_code == 404


def test_previous_next_follow_list_order(client):
    first = ProjectFactory(order=1)
    middle = ProjectFactory(order=2)
    ProjectFactory(order=3, is_published=False)
    last = ProjectFactory(order=4)

    context = client.get(middle.get_absolute_url()).context
    assert context["previous_project"] == first
    assert context["next_project"] == last

    context = client.get(first.get_absolute_url()).context
    assert context["previous_project"] is None
    assert context["next_project"] == middle


def test_related_projects_share_a_category(client):
    web, ai = ProjectCategoryFactory(), ProjectCategoryFactory()
    project = ProjectFactory(categories=[web, ai])
    related = ProjectFactory(categories=[web, ai])  # shares two categories, listed once
    ProjectFactory(categories=[])
    ProjectFactory(categories=[web], is_published=False)
    context = client.get(project.get_absolute_url()).context
    assert list(context["related_projects"]) == [related]


def test_detail_is_translated(client):
    ProjectFactory(title_en="Dive School", title_fr="École de plongée", slug="dive")
    assert "Dive School" in client.get("/en/portfolio/dive/").content.decode()
    assert "École de plongée" in client.get("/fr/portfolio/dive/").content.decode()
    assert client.get("/kr/portfolio/dive/").status_code == 404


def test_nav_marks_portfolio_on_detail_pages(client):
    content = client.get(ProjectFactory().get_absolute_url()).content.decode()
    assert 'href="/en/portfolio/" class="nav-link" aria-current="page"' in content


# --- Admin & seed -----------------------------------------------------------


def test_admin_pages_load(client):
    user = get_user_model().objects.create_superuser("owner", "o@example.com", "pw-123456789")
    client.force_login(user)
    project = ProjectFactory()
    base = f"/{settings.ADMIN_URL}portfolio/project/"
    for url in [base, f"{base}add/", f"{base}{project.pk}/change/"]:
        assert client.get(url).status_code == 200, url


def test_seed_demo_creates_projects_once():
    call_command("seed_demo")
    call_command("seed_demo")
    assert Project.objects.count() == 7
    assert Project.objects.featured().count() == 3
    assert all(p.client.endswith("(demo)") for p in Project.objects.all())
    first = Project.objects.first()
    assert first.images.count() == 4 and first.metrics.exists()


# --- In-progress projects -----------------------------------------------------------

IN_PROGRESS = Project.Status.IN_PROGRESS


def test_status_helpers():
    done = ProjectFactory.build(live_url="https://client.example.com")
    building = ProjectFactory.build(live_url="https://client.example.com", status=IN_PROGRESS)
    assert done.status == Project.Status.COMPLETED  # default
    assert done.show_live_url and not done.is_in_progress
    assert building.is_in_progress and not building.show_live_url


def test_in_progress_card_has_badge_and_no_live_link(client):
    ProjectFactory(status=IN_PROGRESS, live_url="https://client.example.com")
    content = client.get(LIST).content.decode()
    assert ">In progress</span>" in content and "status-badge is-progress" in content
    assert "https://client.example.com" not in content


def test_in_progress_case_study_hides_results_and_live_site(client):
    project = ProjectFactory(
        status=IN_PROGRESS, results="Doubled sales.", live_url="https://client.example.com"
    )
    ProjectMetricFactory(project=project, value="+200%", label="sales")
    content = client.get(project.get_absolute_url()).content.decode()
    assert "This project is still in progress" in content
    for hidden in ["Doubled sales.", "+200%", "https://client.example.com", "Visit live site"]:
        assert hidden not in content, hidden
    assert '"creativeWorkStatus": "Incomplete"' in content


SHOWCASE = "Projects we're proud of."
IN_PROGRESS_HEADING = "What we're building now."


@pytest.mark.parametrize(
    ("completed", "shown", "hidden"),
    [(2, IN_PROGRESS_HEADING, SHOWCASE), (3, SHOWCASE, IN_PROGRESS_HEADING)],
)
def test_home_heading_depends_on_completed_projects(client, completed, shown, hidden):
    ProjectFactory.create_batch(completed, is_featured=True)
    ProjectFactory(is_featured=True, status=IN_PROGRESS)  # never counts
    ProjectFactory(is_published=False)  # never counts
    content = client.get("/en/").content.decode()
    assert shown in content
    assert hidden not in content
