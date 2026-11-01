"""Phase 6: security headers, SEO (sitemap, robots, JSON-LD, canonical) and analytics."""

import json
import re
from decimal import Decimal

import pytest
from django.conf import settings

from apps.core.models import SiteSettings
from apps.portfolio.tests.factories import ProjectFactory
from apps.pricing.models import Package

pytestmark = pytest.mark.django_db

JSON_LD = re.compile(r'<script type="application/ld\+json" nonce="([^"]+)">(.*?)</script>', re.S)


# --- Content Security Policy ----------------------------------------------------------


def test_csp_header_is_strict(client):
    response = client.get("/en/")
    policy = response["Content-Security-Policy"]
    directives = dict(d.strip().split(" ", 1) for d in policy.split(";"))
    assert directives["default-src"] == "'self'"
    assert directives["object-src"] == "'none'"
    assert directives["frame-ancestors"] == "'none'"
    assert "'unsafe-inline'" not in directives["script-src"]
    assert "'unsafe-eval'" not in directives["script-src"]
    assert re.search(r"'nonce-[\w-]+'", directives["script-src"])


def test_every_inline_script_carries_the_request_nonce(client):
    response = client.get("/en/")
    nonce = re.search(r"'nonce-([\w-]+)'", response["Content-Security-Policy"]).group(1)
    content = response.content.decode()
    inline_scripts = re.findall(r"<script(?![^>]*\bsrc=)([^>]*)>", content)
    assert inline_scripts
    for attrs in inline_scripts:
        assert f'nonce="{nonce}"' in attrs, attrs


def test_nonce_changes_per_request(client):
    first = client.get("/en/")["Content-Security-Policy"]
    second = client.get("/en/")["Content-Security-Policy"]
    assert first != second


def test_no_third_party_fonts(client):
    content = client.get("/en/").content.decode()
    assert "fonts.googleapis.com" not in content
    assert "dist/fonts.css" in content


# --- robots.txt & sitemap ---------------------------------------------------------------


def test_robots_txt_never_reveals_admin(client):
    response = client.get("/robots.txt")
    body = response.content.decode()
    assert response["Content-Type"].startswith("text/plain")
    assert settings.ADMIN_URL.strip("/") not in body
    assert "Sitemap: http://testserver/sitemap.xml" in body
    assert "Disallow: /*/pricing/order/" in body


def test_sitemap_lists_published_pages_in_every_language(client):
    ProjectFactory(slug="shown")
    ProjectFactory(slug="draft", is_published=False)
    body = client.get("/sitemap.xml").content.decode()
    for prefix in ("en", "fr"):
        assert f"http://testserver/{prefix}/portfolio/shown/" in body
    assert "/portfolio/draft/" not in body
    assert 'hreflang="fr" href="http://testserver/fr/' in body
    assert "/kr/" not in body and 'hreflang="mfe"' not in body
    assert 'hreflang="x-default"' in body


# --- Canonical, Open Graph, JSON-LD -------------------------------------------------------


def test_canonical_and_alternates_ignore_query_strings(client):
    content = client.get("/en/portfolio/?category=x&page=2").content.decode()
    assert '<link rel="canonical" href="http://testserver/en/portfolio/">' in content
    assert 'hreflang="fr" href="http://testserver/fr/portfolio/"' in content
    assert 'hreflang="x-default" href="http://testserver/en/portfolio/"' in content


def test_default_share_image(client):
    from apps.core.placeholders import placeholder_image

    obj = SiteSettings.load()
    obj.og_image = placeholder_image("share", size=(120, 63))
    obj.save()
    assert re.search(r'<meta property="og:image" content="http://testserver/media/seo/[^"]+">',
                     client.get("/en/about/").content.decode())  # fmt: skip


def json_ld(response):
    return [json.loads(raw) for _nonce, raw in JSON_LD.findall(response.content.decode())]


def test_organization_schema_on_every_page(client):
    obj = SiteSettings.load()
    obj.contact_email = "hello@webmoris.test"
    obj.instagram_url = "https://instagram.com/webmoris"
    obj.save()
    org = json_ld(client.get("/en/about/"))[0]
    assert org["@type"] == "ProfessionalService"
    assert org["email"] == "hello@webmoris.test"
    assert org["sameAs"] == ["https://instagram.com/webmoris"]


def test_project_and_pricing_schemas(client):
    project = ProjectFactory(title="Dive School", tech_stack="Django, GSAP")
    data = json_ld(client.get(project.get_absolute_url()))
    assert data[1]["@type"] == "CreativeWork" and data[1]["name"] == "Dive School"

    Package.objects.create(name="Starter", slug="starter", summary="s", price=Decimal("25000"))
    graph = json_ld(client.get("/en/pricing/"))[1]["@graph"]
    assert graph[0]["offers"] == {
        "@type": "Offer",
        "price": "25000.00",
        "priceCurrency": "MUR",
        "availability": "https://schema.org/InStock",
        "url": "http://testserver/en/pricing/starter/checkout/",
    }


def test_json_ld_cannot_break_out_of_its_script_tag(client):
    project = ProjectFactory(title="</script><script>alert(1)</script>")
    content = client.get(project.get_absolute_url()).content.decode()
    assert "</script><script>alert(1)" not in content
    assert json_ld(client.get(project.get_absolute_url()))[1]["name"].startswith("</script>")


# --- Analytics & consent -------------------------------------------------------------------


def test_no_analytics_by_default(client):
    content = client.get("/en/").content.decode()
    assert "plausible" not in content and "ga4-id" not in content
    assert 'x-data="consent"' not in content


def test_plausible_loads_without_consent_banner(client, settings):
    settings.ANALYTICS_PROVIDER = "plausible"
    settings.PLAUSIBLE_DOMAIN = "webmoris.mu"
    content = client.get("/en/").content.decode()
    assert 'data-domain="webmoris.mu"' in content
    assert 'x-data="consent"' not in content


def test_ga4_waits_for_consent(client, settings):
    settings.ANALYTICS_PROVIDER = "ga4"
    settings.GA4_MEASUREMENT_ID = "G-TEST123"
    content = client.get("/en/").content.decode()
    assert '<meta name="ga4-id" content="G-TEST123">' in content
    assert "googletagmanager.com/gtag/js" not in content  # only loaded by JS after consent
    assert 'x-data="consent"' in content


def test_conversion_markers(client):
    content = client.get("/en/contact/?sent=1").content.decode()
    assert 'data-track-event="lead_submitted"' in content


# --- Hero ----------------------------------------------------------------------------------


def test_home_hero_has_3d_mount_and_css_fallback(client):
    content = client.get("/en/").content.decode()
    assert 'data-hero-3d aria-hidden="true"' in content
    assert 'class="hero-glow"' in content


# --- Regressions found in visual QA ---------------------------------------------------------


def test_section_intros_do_not_leak_into_later_sections(client):
    from io import StringIO

    from django.core.management import call_command

    call_command("seed_demo", stdout=StringIO())
    content = client.get("/en/").content.decode()
    # The ready-made section's intro used to reappear under "How we work" and "Pricing".
    assert content.count("Pick a design for your industry") == 1
    assert len(client.get("/en/").context["featured_templates"]) == 3  # one full row
