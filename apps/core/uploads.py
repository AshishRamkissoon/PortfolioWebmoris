"""Upload helpers shared by every app: random file names and size/type limits."""

import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
VIDEO_EXTENSIONS = ["mp4", "webm"]

MB = 1024 * 1024


@deconstructible
class RandomFilename:
    """upload_to callable: ``<folder>/<uuid4>.<ext>``. Never trusts the client's file name."""

    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        extension = Path(filename).suffix.lower()
        return f"{self.folder}/{uuid.uuid4().hex}{extension}"


@deconstructible
class MaxFileSizeValidator:
    def __init__(self, max_mb):
        self.max_mb = max_mb

    def __call__(self, file):
        if file.size > self.max_mb * MB:
            raise ValidationError(
                _("File too large: the maximum size is %(max)s MB."), params={"max": self.max_mb}
            )

    def __eq__(self, other):
        return isinstance(other, MaxFileSizeValidator) and self.max_mb == other.max_mb


image_validators = [FileExtensionValidator(IMAGE_EXTENSIONS), MaxFileSizeValidator(10)]
video_validators = [FileExtensionValidator(VIDEO_EXTENSIONS), MaxFileSizeValidator(50)]
