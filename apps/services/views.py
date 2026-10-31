from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from .models import Service, ServiceGroup


def published_groups():
    """Service groups that have published services, with those services prefetched."""
    services = Service.objects.published()
    return (
        ServiceGroup.objects.filter(services__in=services)
        .distinct()
        .prefetch_related(Prefetch("services", queryset=services))
    )


def service_list(request):
    return render(request, "services/list.html", {"groups": published_groups()})


def service_detail(request, slug):
    service = get_object_or_404(
        Service.objects.published().select_related("group").prefetch_related("faqs"), slug=slug
    )
    other_services = Service.objects.published().filter(group=service.group).exclude(pk=service.pk)
    return render(
        request,
        "services/detail.html",
        {
            "service": service,
            "related_projects": service.related_projects.published()[:3],
            "other_services": other_services,
        },
    )
