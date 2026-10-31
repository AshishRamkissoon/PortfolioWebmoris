from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.models import SiteSettings
from apps.leads.models import LeadStatus, QuoteRequest
from apps.leads.spam import client_ip
from apps.portfolio.tests.factories import ProjectFactory
from apps.services.models import Service, ServiceGroup

pytestmark = pytest.mark.django_db

URL = "/en/contact/"
HTMX = {"HX-Request": "true"}


def valid_data(**overrides):
    data = {
        "name": "Jane Client",
        "email": "jane@example.com",
        "phone": "+230 5000 0000",
        "company": "Jane Ltd",
        "project_type": "website",
        "budget": "25k_75k",
        "timeline": "1_month",
        "message": "We need a new website for our hotel.",
        "source_page": "/en/services/",
        "website": "",
    }
    return {**data, **overrides}


@pytest.fixture(autouse=True)
def site_settings():
    obj = SiteSettings.load()
    obj.contact_email = "team@webmoris.test"
    obj.save()
    return obj


# --- Page & pre-fill ----------------------------------------------------------


def test_contact_page_renders_form(client):
    content = client.get(URL).content.decode()
    assert 'id="quote-form"' in content
    assert 'enctype="multipart/form-data"' in content
    assert 'class="honeypot"' in content


def test_prefill_from_template_project_service_and_type(client):
    from apps.readymade.models import TemplateIndustry
    from apps.readymade.tests.test_readymade import make_template

    template = make_template(
        TemplateIndustry.objects.create(name="Food", slug="food"), name="Bistro"
    )
    form = client.get(f"{URL}?template={template.slug}").context["form"]
    assert form.initial["project_type"] == "readymade"
    assert "Bistro" in form.initial["message"]

    project = ProjectFactory(title="Dive School")
    assert (
        "Dive School"
        in client.get(f"{URL}?project={project.slug}").context["form"].initial["message"]
    )

    group = ServiceGroup.objects.create(name="AI", slug="ai-marketing")
    Service.objects.create(group=group, title="AI Chatbots", slug="chatbots", summary="s")
    initial = client.get(f"{URL}?service=chatbots").context["form"].initial
    assert initial["project_type"] == "ai_marketing"

    assert client.get(f"{URL}?type=landing").context["form"].initial == {"project_type": "landing"}
    assert client.get(f"{URL}?type=<script>").context["form"].initial == {}
    assert client.get(f"{URL}?project=unpublished-or-missing").context["form"].initial == {}


# --- Submissions ----------------------------------------------------------------


def test_valid_submission_saves_and_redirects(client):
    response = client.post("/fr/contact/", valid_data())
    assert response.status_code == 302
    assert response["Location"] == "/fr/contact/?sent=1"

    lead = QuoteRequest.objects.get()
    assert lead.name == "Jane Client"
    assert lead.language == "fr"
    assert lead.status == LeadStatus.NEW
    assert lead.source_page == "/en/services/"
    assert "Merci" in client.get(response["Location"]).content.decode()


def test_emails_notify_team_and_auto_reply_in_visitor_language(client):
    client.post("/fr/contact/", valid_data(message="Secret spam payload http://spam.example"))
    assert len(mail.outbox) == 2
    notification, auto_reply = mail.outbox

    assert notification.to == ["team@webmoris.test"]
    assert notification.reply_to == ["jane@example.com"]
    assert "Jane Client" in notification.subject
    assert "Secret spam payload" in notification.body
    assert "/core/" not in notification.body and "/leads/quoterequest/" in notification.body

    assert auto_reply.to == ["jane@example.com"]
    assert auto_reply.subject == "Nous avons bien reçu votre message — Webmoris"
    # The auto-reply never echoes visitor input (anti spam-relay).
    for text in ["Secret spam payload", "spam.example", "Jane Client"]:
        assert text not in auto_reply.body
        assert text not in auto_reply.alternatives[0].content


def test_notify_address_setting_overrides_site_settings(client, settings):
    settings.LEADS_NOTIFY_EMAIL = "sales@webmoris.test"
    client.post(URL, valid_data())
    assert mail.outbox[0].to == ["sales@webmoris.test"]


def test_only_auto_reply_when_no_team_address(client, site_settings):
    site_settings.contact_email = ""
    site_settings.save()
    client.post(URL, valid_data())
    assert [m.to for m in mail.outbox] == [["jane@example.com"]]


def test_email_failure_never_loses_the_lead(client):
    with mock.patch("apps.leads.emails._send", side_effect=OSError("SMTP down")):
        response = client.post(URL, valid_data())
    assert response.status_code == 302
    assert QuoteRequest.objects.count() == 1


def test_htmx_submission_returns_success_partial(client):
    response = client.post(URL, valid_data(), headers=HTMX)
    content = response.content.decode()
    assert response.status_code == 200
    assert "<html" not in content
    assert "Thank you" in content
    assert QuoteRequest.objects.count() == 1


def test_invalid_submission_shows_errors(client):
    response = client.post(URL, valid_data(email="not-an-email", budget=""), headers=HTMX)
    content = response.content.decode()
    assert 'aria-invalid="true"' in content
    assert "<html" not in content
    assert not QuoteRequest.objects.exists()
    assert not mail.outbox


def test_newlines_in_name_cannot_inject_headers(client):
    client.post(URL, valid_data(name="Eve\r\nBcc: victim@example.com"))
    for message in mail.outbox:
        assert "\n" not in message.subject and "\r" not in message.subject
        assert "victim@example.com" not in message.bcc


def test_unsafe_source_page_is_reduced_to_a_path(client):
    client.post(URL, valid_data(source_page="//evil.example/phish"))
    client.post(URL, valid_data(source_page="javascript:alert(1)"))
    assert set(QuoteRequest.objects.values_list("source_page", flat=True)) == {""}


# --- Spam protection --------------------------------------------------------------


def test_honeypot_pretends_success_but_drops_submission(client):
    response = client.post(URL, valid_data(website="http://spam.example"), headers=HTMX)
    assert "Thank you" in response.content.decode()
    assert not QuoteRequest.objects.exists()
    assert not mail.outbox


def test_rate_limit(client, settings):
    settings.LEADS_RATE_LIMIT = 2
    for _ in range(2):
        client.post(URL, valid_data())
    response = client.post(URL, valid_data(), headers=HTMX)
    assert "several messages" in response.content.decode()
    assert QuoteRequest.objects.count() == 2


def test_rate_limit_is_per_visitor(client, settings):
    settings.LEADS_RATE_LIMIT = 1
    client.post(URL, valid_data(), REMOTE_ADDR="10.0.0.1")
    client.post(URL, valid_data(), REMOTE_ADDR="10.0.0.2")
    assert QuoteRequest.objects.count() == 2


def test_client_ip_trusts_only_configured_proxies(rf, settings):
    request = rf.get("/", REMOTE_ADDR="10.0.0.9", HTTP_X_FORWARDED_FOR="6.6.6.6, 1.2.3.4")
    assert client_ip(request) == "10.0.0.9"  # no proxy configured: ignore spoofable header
    settings.TRUSTED_PROXY_COUNT = 1
    assert client_ip(request) == "1.2.3.4"


def test_turnstile_required_when_configured(client, settings):
    settings.TURNSTILE_SITE_KEY = "site"
    settings.TURNSTILE_SECRET_KEY = "secret"
    assert 'class="cf-turnstile"' in client.get(URL).content.decode()

    response = client.post(URL, valid_data(), headers=HTMX)
    assert "spam check" in response.content.decode()
    assert not QuoteRequest.objects.exists()

    fake = mock.MagicMock()
    fake.__enter__.return_value.read.return_value = b'{"success": true}'
    with mock.patch("urllib.request.urlopen", return_value=fake):
        client.post(URL, valid_data(**{"cf-turnstile-response": "token"}))
    assert QuoteRequest.objects.count() == 1


# --- Attachments ------------------------------------------------------------------


def pdf(name="brief.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 test", content_type="application/pdf")


def test_attachment_is_stored_privately(client, settings):
    client.post(URL, valid_data(attachment=pdf()))
    lead = QuoteRequest.objects.get()
    path = lead.attachment.path
    assert str(settings.PRIVATE_MEDIA_ROOT) in path
    assert str(settings.MEDIA_ROOT) not in path
    assert "brief" not in lead.attachment.name  # random name


@pytest.mark.parametrize("name", ["evil.exe", "page.html", "shell.php", "image.svg"])
def test_dangerous_attachments_rejected(client, name):
    response = client.post(URL, valid_data(attachment=SimpleUploadedFile(name, b"x")), headers=HTMX)
    assert "attachment" in response.context["form"].errors
    assert not QuoteRequest.objects.exists()


def test_attachment_download_is_staff_only(client):
    client.post(URL, valid_data(attachment=pdf()))
    lead = QuoteRequest.objects.get()
    from django.conf import settings

    url = f"/{settings.ADMIN_URL}leads/quoterequest/{lead.pk}/attachment/"

    assert client.get(url).status_code == 302  # anonymous → login

    user_model = get_user_model()
    client.force_login(user_model.objects.create_user("visitor", "v@example.com", "pw-123456789"))
    assert client.get(url).status_code == 302  # not staff → login

    client.force_login(user_model.objects.create_superuser("o", "o@example.com", "pw-123456789"))
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Disposition"].startswith("attachment;")
    assert b"".join(response.streaming_content) == b"%PDF-1.4 test"
