import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.uploads import MaxFileSizeValidator, RandomFilename
from apps.core.video import embed_url, validate_video_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0",
        ),
        (
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0",
        ),
        (
            "https://youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0",
        ),
        (
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ&t=10",
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0",
        ),
        ("https://vimeo.com/123456789", "https://player.vimeo.com/video/123456789"),
        ("https://player.vimeo.com/video/123456789", "https://player.vimeo.com/video/123456789"),
    ],
)
def test_embed_url_supported_links(url, expected):
    assert embed_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "",
        "https://evil.example.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com.evil.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=<script>",
        "https://vimeo.com/not-a-number",
        "javascript:alert(1)",
    ],
)
def test_embed_url_rejects_everything_else(url):
    assert embed_url(url) is None


def test_validate_video_url():
    validate_video_url("https://youtu.be/dQw4w9WgXcQ")
    validate_video_url("")
    with pytest.raises(ValidationError):
        validate_video_url("https://example.com/video.mp4")


def test_random_filename_ignores_client_name():
    upload_to = RandomFilename("projects/covers")
    first = upload_to(None, "../../etc/My Photo.JPG")
    second = upload_to(None, "../../etc/My Photo.JPG")
    assert first.startswith("projects/covers/")
    assert first.endswith(".jpg")
    assert ".." not in first and "My Photo" not in first
    assert first != second


def test_max_file_size_validator():
    validator = MaxFileSizeValidator(1)
    validator(SimpleUploadedFile("ok.png", b"x" * 1024))
    with pytest.raises(ValidationError):
        validator(SimpleUploadedFile("big.png", b"x" * (1024 * 1024 + 1)))
