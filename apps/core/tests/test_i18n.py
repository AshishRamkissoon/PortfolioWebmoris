import pytest
from django.urls import reverse, translate_url
from django.utils import translation

from apps.core.i18n import language_from_path, url_prefix_for

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("path", "expected"),
    [("/en/about/", "en"), ("/fr/", "fr"), ("/kr/contact/", "mfe"), ("/mfe/", None), ("/", None)],
)
def test_language_from_path(path, expected):
    assert language_from_path(path) == expected


def test_kreol_uses_kr_prefix():
    assert url_prefix_for("mfe") == "kr"
    assert url_prefix_for("fr") == "fr"


@pytest.mark.parametrize(("lang", "prefix"), [("en", "en"), ("fr", "fr"), ("mfe", "kr")])
def test_reverse_uses_language_prefix(lang, prefix):
    with translation.override(lang):
        assert reverse("core:about") == f"/{prefix}/about/"


@pytest.mark.parametrize(("lang", "prefix"), [("en", "en"), ("fr", "fr"), ("mfe", "kr")])
def test_prefixed_home_renders_in_language(client, lang, prefix):
    response = client.get(f"/{prefix}/")
    assert response.status_code == 200
    assert response["Content-Language"] == lang
    assert f'<html lang="{lang}">' in response.content.decode()


def test_root_redirects_to_default_language(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response["Location"] == "/en/"


def test_root_redirect_respects_accept_language(client):
    response = client.get("/", headers={"accept-language": "fr"})
    assert response["Location"] == "/fr/"


def test_unprefixed_page_redirects_with_prefix(client):
    response = client.get("/about/")
    assert response.status_code == 302
    assert response["Location"] == "/en/about/"


def test_language_code_is_not_a_url_prefix(client):
    assert client.get("/mfe/").status_code == 404


def test_kreol_translations_are_active(client):
    content = client.get("/kr/").content.decode()
    assert "Demann enn devi" in content  # "Get a Quote"


def test_french_translations_are_active(client):
    content = client.get("/fr/").content.decode()
    assert "Demander un devis" in content


def test_translate_url_between_languages():
    with translation.override("en"):
        assert translate_url("/en/about/", "mfe") == "/kr/about/"
    with translation.override("mfe"):
        assert translate_url("/kr/about/", "fr") == "/fr/about/"


def test_language_switcher_and_hreflang_point_to_same_page(client):
    content = client.get("/fr/services/").content.decode()
    assert 'href="/kr/services/"' in content
    assert 'href="/en/services/"' in content
    assert 'hreflang="mfe" href="http://testserver/kr/services/"' in content
