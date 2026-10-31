import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.core.placeholders import placeholder_image
from apps.readymade.models import TemplateImage, TemplateIndustry, WebsiteTemplate

pytestmark = pytest.mark.django_db

LIST = "/en/ready-made-websites/"


@pytest.fixture
def industry():
    return TemplateIndustry.objects.create(name="Tourism", slug="tourism")


def make_template(industry, **kwargs):
    count = WebsiteTemplate.objects.count()
    defaults = {
        "name": f"Template {count}",
        "slug": f"template-{count}",
        "short_description": "A template.",
        "cover_image": placeholder_image("t", size=(80, 60)),
        "is_published": True,
    }
    return WebsiteTemplate.objects.create(industry=industry, **{**defaults, **kwargs})


def test_list_shows_published_only(client, industry):
    make_template(industry, name="Visible")
    make_template(industry, name="Draft", is_published=False)
    content = client.get(LIST).content.decode()
    assert "Visible" in content
    assert "Draft" not in content


def test_filter_by_industry_with_htmx(client, industry):
    other = TemplateIndustry.objects.create(name="Restaurant", slug="restaurant")
    make_template(industry, name="Island tours")
    make_template(other, name="Bistro")
    response = client.get(
        f"{LIST}?industry=restaurant", headers={"HX-Request": "true", "HX-Target": "template-grid"}
    )
    content = response.content.decode()
    assert "<html" not in content
    assert "Bistro" in content and "Island tours" not in content
    assert "HX-Request" in response["Vary"]


def test_prices_and_status(client, industry):
    make_template(industry, name="Priced", starting_price=25000)
    make_template(industry, name="Soon", status=WebsiteTemplate.Status.COMING_SOON)
    content = client.get(LIST).content.decode()
    assert "From <strong>MUR 25,000</strong>" in content
    assert "Price on request" in content
    assert "Coming soon" in content


def test_french_price_formatting(client, industry):
    make_template(industry, starting_price=25000, currency="EUR")
    assert "EUR 25" in client.get("/fr/ready-made-websites/").content.decode()


def test_detail_page(client, industry):
    template = make_template(
        industry,
        demo_url="https://demo.example.com",
        features="Booking form\nGallery",
        pages="Home\nContact",
        video_url="https://youtu.be/dQw4w9WgXcQ",
    )
    TemplateImage.objects.create(template=template, image=placeholder_image("s", size=(80, 60)))
    content = client.get(template.get_absolute_url()).content.decode()
    for text in [
        "Booking form",
        "Contact",
        "data-lightbox-item",
        "youtube-nocookie.com/embed/",
        'href="https://demo.example.com" target="_blank" rel="noopener noreferrer"',
        "Customise this website",
    ]:
        assert text in content, text


def test_coming_soon_detail_offers_notification(client, industry):
    template = make_template(industry, status=WebsiteTemplate.Status.COMING_SOON)
    assert "Notify me when it" in client.get(template.get_absolute_url()).content.decode()


def test_unpublished_detail_is_404(client, industry):
    template = make_template(industry, is_published=False)
    assert client.get(template.get_absolute_url()).status_code == 404


def test_other_templates_exclude_current(client, industry):
    template = make_template(industry)
    other = make_template(industry)
    make_template(industry, is_published=False)
    assert list(client.get(template.get_absolute_url()).context["other_templates"]) == [other]


def test_video_link_must_be_youtube_or_vimeo(industry):
    template = make_template(industry, video_url="https://example.com/v.mp4")
    with pytest.raises(ValidationError):
        template.full_clean()


def test_negative_price_rejected(industry):
    template = make_template(industry, starting_price=-1)
    with pytest.raises(ValidationError):
        template.full_clean()


def test_template_admin(client, industry):
    admin = get_user_model().objects.create_superuser("o", "o@example.com", "pw-123456789")
    client.force_login(admin)
    template = make_template(industry)
    base = f"/{settings.ADMIN_URL}readymade/websitetemplate/"
    for url in [base, f"{base}add/", f"{base}{template.pk}/change/"]:
        assert client.get(url).status_code == 200, url
