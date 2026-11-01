import pytest
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.core.models import LegalPage

pytestmark = pytest.mark.django_db

PAGES = [
    "",
    "portfolio/",
    "ready-made-websites/",
    "services/",
    "pricing/",
    "about/",
    "contact/",
    "privacy/",
    "terms/",
]


@pytest.mark.parametrize("prefix", ["en", "fr"])
@pytest.mark.parametrize("page", PAGES)
def test_every_sitemap_page_renders(client, prefix, page):
    for kind in LegalPage.Kind.values:
        LegalPage.objects.create(kind=kind, title=kind, body="Text")
    response = client.get(f"/{prefix}/{page}")
    assert response.status_code == 200


@pytest.mark.parametrize("page", PAGES)
def test_every_sitemap_page_renders_when_empty(client, page):
    """A fresh install with no content must not crash; legal pages 404 until written."""
    expected = 404 if page in ("privacy/", "terms/") else 200
    assert client.get(f"/en/{page}").status_code == expected


def test_base_layout_has_header_footer_and_skip_link(client):
    content = client.get("/en/").content.decode()
    assert 'href="#main"' in content
    assert "<header" in content
    assert "<footer" in content
    assert 'rel="canonical"' in content


def test_current_page_is_marked_in_nav(client):
    content = client.get("/en/pricing/").content.decode()
    assert 'href="/en/pricing/" class="nav-link" aria-current="page"' in content


def test_external_links_are_safe(client):
    from apps.core.models import SiteSettings

    obj = SiteSettings.load()
    obj.whatsapp_number = "23057123456"
    obj.linkedin_url = "https://linkedin.com/company/webmoris"
    obj.save()
    content = client.get("/en/").content.decode()
    assert content.count('rel="noopener noreferrer"') >= 2


def test_custom_404_page(client):
    response = client.get("/en/this-does-not-exist/")
    assert response.status_code == 404
    assert "404" in response.content.decode()


def test_default_admin_url_is_not_exposed(client):
    assert settings.ADMIN_URL != "admin/"
    assert client.get("/admin/").status_code == 404


def test_admin_lives_on_custom_url(client):
    response = client.get(f"/{settings.ADMIN_URL}")
    assert response.status_code == 302  # redirect to admin login


def test_site_settings_admin_opens_edit_form(client):
    user = get_user_model().objects.create_superuser("owner", "owner@example.com", "pw-123456789")
    client.force_login(user)
    response = client.get(f"/{settings.ADMIN_URL}core/sitesettings/")
    assert response.status_code == 302
    assert response["Location"].endswith("/core/sitesettings/1/change/")
    assert client.get(response["Location"]).status_code == 200


def test_no_multiline_template_comments():
    """Django's {# #} comments are single-line only; a multi-line one is printed on the page."""
    from pathlib import Path

    offenders = [
        f"{path}:{number}"
        for path in Path(settings.BASE_DIR, "templates").rglob("*.html")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if "{#" in line and "#}" not in line.split("{#", 1)[1]
    ]
    assert not offenders, f"Use {{% comment %}} for multi-line comments: {offenders}"
