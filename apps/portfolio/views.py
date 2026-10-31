from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.utils.cache import patch_vary_headers

from .models import Project, ProjectCategory

PAGE_SIZE = 9


def project_list(request):
    categories = ProjectCategory.objects.filter(projects__is_published=True).distinct()
    active = categories.filter(slug=request.GET.get("category")).first()

    projects = Project.objects.published().prefetch_related("categories")
    if active:
        projects = projects.filter(categories=active)
    page = Paginator(projects, PAGE_SIZE).get_page(request.GET.get("page"))

    context = {"categories": categories, "active_category": active, "page": page}

    # HTMX: the filter tabs swap the whole grid; "load more" appends the next cards only.
    template = "portfolio/list.html"
    if request.headers.get("HX-Request"):
        target = request.headers.get("HX-Target")
        if target == "load-more":
            template = "portfolio/partials/cards.html"
        elif target == "project-grid":
            template = "portfolio/partials/grid.html"
    response = render(request, template, context)
    patch_vary_headers(response, ("HX-Request", "HX-Target"))
    return response


def project_detail(request, slug):
    published = Project.objects.published()
    project = get_object_or_404(
        published.prefetch_related("categories", "metrics", "images"), slug=slug
    )

    ordered_ids = list(published.values_list("pk", flat=True))
    index = ordered_ids.index(project.pk)
    previous_id = ordered_ids[index - 1] if index > 0 else None
    next_id = ordered_ids[index + 1] if index + 1 < len(ordered_ids) else None
    neighbours = published.in_bulk([pk for pk in (previous_id, next_id) if pk])

    related = (
        published.filter(categories__in=project.categories.all())
        .exclude(pk=project.pk)
        .distinct()[:3]
    )

    images = list(project.images.all())
    return render(
        request,
        "portfolio/detail.html",
        {
            "project": project,
            "desktop_images": [i for i in images if i.kind == i.Kind.DESKTOP],
            "mobile_images": [i for i in images if i.kind == i.Kind.MOBILE],
            "previous_project": neighbours.get(previous_id),
            "next_project": neighbours.get(next_id),
            "related_projects": related,
        },
    )
