"""schema.org JSON-LD for search engines (Organization, CreativeWork, Service, Product/Offer)."""

import json

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# Same escaping as Django's json_script: the JSON can never close the <script> element.
_JSON_ESCAPES = {ord(">"): "\\u003E", ord("<"): "\\u003C", ord("&"): "\\u0026"}


def _script(context, data):
    payload = json.dumps(data, ensure_ascii=False, default=str).translate(_JSON_ESCAPES)
    return format_html(
        '<script type="application/ld+json" nonce="{}">{}</script>',
        context.get("csp_nonce", ""),
        mark_safe(payload),  # noqa: S308 — escaped above, like json_script
    )


def _origin(context):
    request = context["request"]
    return f"{request.scheme}://{request.get_host()}"


def _organization(context):
    s = context["site_settings"]
    origin = _origin(context)
    data = {
        "@type": "ProfessionalService",
        "@id": f"{origin}/#organization",
        "name": s.site_name,
        "url": f"{origin}/",
        "description": s.seo_description or s.tagline,
        "areaServed": "MU",
        "address": {"@type": "PostalAddress", "addressCountry": "MU"},
    }
    if s.address:
        data["address"]["streetAddress"] = s.address
    if s.contact_email:
        data["email"] = s.contact_email
    if s.contact_phone:
        data["telephone"] = s.contact_phone
    if s.og_image:
        data["image"] = origin + s.og_image.url
    if same_as := [url for _name, url in s.social_links]:
        data["sameAs"] = same_as
    return data


def _with_context(data):
    return {"@context": "https://schema.org", **data}


@register.simple_tag(takes_context=True)
def schema_organization(context):
    return _script(context, _with_context(_organization(context)))


@register.simple_tag(takes_context=True)
def schema_project(context, project):
    origin = _origin(context)
    data = {
        "@type": "CreativeWork",
        "name": project.title,
        "description": project.short_description,
        "url": origin + project.get_absolute_url(),
        "image": origin + project.cover_card.url,
        "dateCreated": str(project.year),
        "creator": {"@id": f"{origin}/#organization"},
        "keywords": ", ".join(project.tech_list),
    }
    if project.live_url:
        data["sameAs"] = project.live_url
    return _script(context, _with_context(data))


@register.simple_tag(takes_context=True)
def schema_service(context, service):
    origin = _origin(context)
    data = {
        "@type": "Service",
        "name": service.title,
        "description": service.summary,
        "url": origin + service.get_absolute_url(),
        "serviceType": service.group.name,
        "provider": {"@id": f"{origin}/#organization"},
        "areaServed": "MU",
    }
    return _script(context, _with_context(data))


def _offer(price, currency, url):
    return {
        "@type": "Offer",
        "price": f"{price:.2f}",
        "priceCurrency": currency,
        "availability": "https://schema.org/InStock",
        "url": url,
    }


@register.simple_tag(takes_context=True)
def schema_template(context, website_template):
    origin = _origin(context)
    url = origin + website_template.get_absolute_url()
    data = {
        "@type": "Product",
        "name": website_template.name,
        "description": website_template.short_description,
        "image": origin + website_template.cover_card.url,
        "url": url,
        "brand": {"@id": f"{origin}/#organization"},
    }
    if website_template.starting_price is not None and website_template.is_available:
        data["offers"] = _offer(website_template.starting_price, website_template.currency, url)
    return _script(context, _with_context(data))


@register.simple_tag(takes_context=True)
def schema_packages(context, packages):
    origin = _origin(context)
    items = [
        {
            "@type": "Product",
            "name": package.name,
            "description": package.summary,
            "brand": {"@id": f"{origin}/#organization"},
            "offers": _offer(
                package.price,
                package.currency,
                origin + (package.get_checkout_url() if package.is_purchasable else "/"),
            ),
        }
        for package in packages
    ]
    return _script(context, _with_context({"@graph": items})) if items else ""
