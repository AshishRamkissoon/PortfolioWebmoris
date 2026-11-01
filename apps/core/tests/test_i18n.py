import pytest
from django.conf import settings
from django.urls import reverse, translate_url
from django.utils import translation

pytestmark = pytest.mark.django_db


def test_site_languages():
    assert [code for code, _name in settings.LANGUAGES] == ["en", "fr"]


@pytest.mark.parametrize("lang", ["en", "fr"])
def test_reverse_uses_language_prefix(lang):
    with translation.override(lang):
        assert reverse("core:about") == f"/{lang}/about/"


@pytest.mark.parametrize("lang", ["en", "fr"])
def test_prefixed_home_renders_in_language(client, lang):
    response = client.get(f"/{lang}/")
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


@pytest.mark.parametrize("path", ["/kr/", "/mfe/", "/kr/about/"])
def test_removed_kreol_urls_are_gone(client, path):
    assert client.get(path).status_code == 404


def test_french_translations_are_active(client):
    content = client.get("/fr/").content.decode()
    assert "Demander un devis" in content


def test_translate_url_between_languages():
    with translation.override("en"):
        assert translate_url("/en/about/", "fr") == "/fr/about/"


def test_language_switcher_and_hreflang_point_to_same_page(client):
    content = client.get("/fr/services/").content.decode()
    assert 'href="/en/services/"' in content
    assert 'hreflang="en" href="http://testserver/en/services/"' in content
    assert 'hreflang="mfe"' not in content
    assert ">KR<" not in content
