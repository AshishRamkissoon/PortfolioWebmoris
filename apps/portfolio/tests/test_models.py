import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.portfolio.models import Project

from .factories import ProjectFactory

pytestmark = pytest.mark.django_db


def test_published_and_featured_querysets():
    shown = ProjectFactory(is_featured=True)
    ProjectFactory(is_featured=False)
    ProjectFactory(is_published=False, is_featured=True)
    assert Project.objects.published().count() == 2
    assert list(Project.objects.featured()) == [shown]


def test_comma_separated_lists():
    project = ProjectFactory.build(services="Design, Development,, SEO ", tech_stack="")
    assert project.services_list == ["Design", "Development", "SEO"]
    assert project.tech_list == []


def test_video_helpers():
    project = ProjectFactory.build(video_url="https://youtu.be/dQw4w9WgXcQ")
    assert project.has_video
    assert project.video_embed_url.startswith("https://www.youtube-nocookie.com/embed/")
    assert not ProjectFactory.build().has_video


def test_absolute_url_uses_language_prefix():
    from django.utils import translation

    project = ProjectFactory(slug="my-shop")
    with translation.override("mfe"):
        assert project.get_absolute_url() == "/kr/portfolio/my-shop/"


def test_uploaded_cover_gets_random_name():
    project = ProjectFactory()
    assert project.cover_image.name.startswith("projects/covers/")
    assert "test" not in project.cover_image.name


@pytest.mark.parametrize(
    ("field", "upload"),
    [
        ("video_url", "https://example.com/video"),
        ("video_file", SimpleUploadedFile("clip.exe", b"MZ")),
        ("cover_image", SimpleUploadedFile("cover.svg", b"<svg onload=alert(1)>")),
    ],
)
def test_unsafe_media_is_rejected(field, upload):
    project = ProjectFactory()
    setattr(project, field, upload)
    with pytest.raises(ValidationError) as error:
        project.full_clean()
    assert field in error.value.message_dict
