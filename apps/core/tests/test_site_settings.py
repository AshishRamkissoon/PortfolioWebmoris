import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import RequestFactory

from apps.core.context_processors import site
from apps.core.models import SiteSettings

pytestmark = pytest.mark.django_db


def test_load_creates_a_single_row():
    first = SiteSettings.load()
    second = SiteSettings.load()
    assert first.pk == second.pk == 1
    assert SiteSettings.objects.count() == 1


def test_save_always_targets_the_singleton_row():
    SiteSettings.load()
    SiteSettings(site_name="Other").save()
    assert SiteSettings.objects.count() == 1
    assert SiteSettings.load().site_name == "Other"


def test_delete_is_a_no_op():
    obj = SiteSettings.load()
    obj.delete()
    assert SiteSettings.objects.count() == 1


def test_whatsapp_link_encodes_message():
    obj = SiteSettings(whatsapp_number="23057123456", whatsapp_message="Hi & hello?")
    assert obj.whatsapp_link == "https://wa.me/23057123456?text=Hi%20%26%20hello%3F"


def test_whatsapp_link_empty_without_number():
    assert SiteSettings(whatsapp_message="Hi").whatsapp_link == ""


@pytest.mark.parametrize("number", ["+23057123456", "230 5712 3456", "abc", "0123456"])
def test_whatsapp_number_rejects_bad_formats(number):
    obj = SiteSettings(whatsapp_number=number)
    with pytest.raises(ValidationError):
        obj.full_clean()


def test_social_links_skip_empty():
    obj = SiteSettings(instagram_url="https://instagram.com/webmoris")
    assert obj.social_links == [("Instagram", "https://instagram.com/webmoris")]


def test_context_processor_exposes_settings():
    context = site(RequestFactory().get("/"))
    assert context["site_settings"].pk == 1


def test_settings_changes_appear_on_pages(client):
    obj = SiteSettings.load()
    obj.contact_email = "team@webmoris.test"
    obj.whatsapp_number = "23057123456"
    obj.save()
    content = client.get("/en/").content.decode()
    assert "team@webmoris.test" in content
    assert "https://wa.me/23057123456" in content


def test_announcement_bar_toggle(client):
    obj = SiteSettings.load()
    obj.announcement_text = "Launch offer: 20% off"
    obj.save()
    assert "Launch offer" not in client.get("/en/").content.decode()
    obj.announcement_enabled = True
    obj.save()
    assert "Launch offer" in client.get("/en/").content.decode()


def test_translated_fields_follow_language(client):
    obj = SiteSettings.load()
    obj.tagline_en = "English tagline"
    obj.tagline_fr = "Slogan français"
    obj.save()
    assert "English tagline" in client.get("/en/").content.decode()
    assert "Slogan français" in client.get("/fr/").content.decode()
    # Kreol falls back to French, then English, when empty.
    assert "Slogan français" in client.get("/kr/").content.decode()


def test_seed_demo_is_idempotent_and_never_overwrites():
    obj = SiteSettings.load()
    obj.contact_email = "real@webmoris.test"
    obj.save()
    call_command("seed_demo")
    call_command("seed_demo")
    obj.refresh_from_db()
    assert obj.contact_email == "real@webmoris.test"
    assert obj.tagline_en
    assert SiteSettings.objects.count() == 1
