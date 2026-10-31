import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError

from apps.core.booking import booking_embed_url
from apps.core.models import SiteSettings
from apps.leads.admin import csv_safe
from apps.leads.models import QuoteRequest, TemplateInquiry
from apps.portfolio.tests.factories import ProjectFactory
from apps.readymade.models import TemplateIndustry
from apps.readymade.tests.test_readymade import make_template

pytestmark = pytest.mark.django_db


@pytest.fixture
def template():
    return make_template(TemplateIndustry.objects.create(name="Food", slug="food"), name="Bistro")


@pytest.fixture
def admin_client(client):
    user = get_user_model().objects.create_superuser("o", "o@example.com", "pw-123456789")
    client.force_login(user)
    return client


def inquiry_data(**overrides):
    data = {"name": "Sam", "email": "sam@example.com", "message": "Hello", "website": ""}
    return {**data, **overrides}


# --- Template enquiries -----------------------------------------------------------


def test_inquiry_page_and_htmx_partial(client, template):
    url = f"/en/contact/ready-made/{template.slug}/"
    page = client.get(url).content.decode()
    assert "<html" in page and "Bistro" in page

    partial = client.get(url, headers={"HX-Request": "true"}).content.decode()
    assert "<html" not in partial and 'id="inquiry-form"' in partial


def test_inquiry_saves_template_snapshot(client, template):
    SiteSettings.objects.update_or_create(pk=1, defaults={"contact_email": "team@webmoris.test"})
    response = client.post(f"/kr/contact/ready-made/{template.slug}/", inquiry_data())
    assert response.status_code == 302
    inquiry = TemplateInquiry.objects.get()
    assert inquiry.template == template
    assert inquiry.template_name == "Bistro"
    assert inquiry.language == "mfe"
    assert inquiry.source_page == template.get_absolute_url()
    assert len(mail.outbox) == 2

    template.delete()
    inquiry.refresh_from_db()
    assert inquiry.template is None and inquiry.template_name == "Bistro"


def test_inquiry_for_unpublished_template_is_404(client, template):
    template.is_published = False
    template.save()
    assert client.get(f"/en/contact/ready-made/{template.slug}/").status_code == 404


def test_template_page_opens_inquiry_dialog(client, template):
    content = client.get(template.get_absolute_url()).content.decode()
    assert f'hx-get="/en/contact/ready-made/{template.slug}/"' in content
    assert f"?template={template.slug}" in content  # CTA band pre-fills the quote form


# --- CTAs and WhatsApp ------------------------------------------------------------


def test_project_cta_prefills_quote(client):
    project = ProjectFactory(slug="dive")
    content = client.get(project.get_absolute_url()).content.decode()
    assert "/en/contact/?project=dive" in content


def test_contextual_whatsapp_message(client, template):
    SiteSettings.objects.update_or_create(pk=1, defaults={"whatsapp_number": "23057123456"})
    content = client.get(template.get_absolute_url()).content.decode()
    assert "wa.me/23057123456?text=Hello%2C%20I%27m%20interested%20in%20the%20ready-made" in content


# --- Booking embed ----------------------------------------------------------------


def test_booking_embed_url():
    assert booking_embed_url("https://calendly.com/webmoris/30min").startswith(
        "https://calendly.com/webmoris/30min?hide_gdpr_banner=1"
    )
    assert booking_embed_url("https://cal.com/webmoris").endswith("?embed=true&theme=dark")
    for bad in ["http://calendly.com/x", "https://calendly.com.evil.io/x", "https://evil.io", ""]:
        assert booking_embed_url(bad) == ""


def test_booking_url_validation_and_embed(client):
    obj = SiteSettings.load()
    obj.calendly_url = "https://evil.example.com/book"
    with pytest.raises(ValidationError):
        obj.full_clean()
    obj.calendly_url = "https://calendly.com/webmoris/30min"
    obj.save()
    assert (
        'src="https://calendly.com/webmoris/30min?hide_gdpr_banner=1'
        in client.get("/en/contact/").content.decode()
    )


# --- Admin ------------------------------------------------------------------------


def test_csv_safe_neutralises_formulas():
    assert csv_safe("=HYPERLINK(1)") == "'=HYPERLINK(1)"
    assert csv_safe("+1") == "'+1"
    assert csv_safe("@SUM") == "'@SUM"
    assert csv_safe("Hello") == "Hello"
    assert csv_safe(None) == ""


def test_admin_lists_and_exports(admin_client):
    lead = QuoteRequest.objects.create(
        name="=cmd|'/c calc'!A1",
        email="a@example.com",
        message="Hi",
        project_type="website",
        budget="unsure",
        timeline="flexible",
    )
    base = f"/{settings.ADMIN_URL}leads/quoterequest/"
    assert admin_client.get(base).status_code == 200
    assert admin_client.get(f"{base}{lead.pk}/change/").status_code == 200
    assert admin_client.get(f"{base}add/").status_code == 403  # leads only come from the site

    response = admin_client.post(base, {"action": "export_csv", "_selected_action": [lead.pk]})
    body = response.content.decode("utf-8-sig")
    assert response["Content-Type"].startswith("text/csv")
    assert "'=cmd" in body
    assert "Website" in body and "Not sure yet" in body


def test_admin_can_only_edit_status_and_notes(admin_client):
    lead = QuoteRequest.objects.create(
        name="Real", email="r@example.com", message="Hi", project_type="website",
        budget="unsure", timeline="flexible",
    )  # fmt: skip
    url = f"/{settings.ADMIN_URL}leads/quoterequest/{lead.pk}/change/"
    admin_client.post(url, {"status": "won", "notes": "Signed!", "name": "Changed"})
    lead.refresh_from_db()
    assert (lead.status, lead.notes, lead.name) == ("won", "Signed!", "Real")


def test_inquiry_admin(admin_client, template):
    inquiry = TemplateInquiry.objects.create(
        name="Sam", email="s@example.com", message="Hi", template=template, template_name="Bistro"
    )
    base = f"/{settings.ADMIN_URL}leads/templateinquiry/"
    assert admin_client.get(base).status_code == 200
    assert admin_client.get(f"{base}{inquiry.pk}/change/").status_code == 200
