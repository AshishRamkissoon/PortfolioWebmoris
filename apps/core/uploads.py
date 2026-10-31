"""Upload helpers shared by every app: random file names and size/type limits."""

import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
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


DOCUMENT_EXTENSIONS = ["pdf", "doc", "docx", "png", "jpg", "jpeg", "zip"]

image_validators = [FileExtensionValidator(IMAGE_EXTENSIONS), MaxFileSizeValidator(10)]
video_validators = [FileExtensionValidator(VIDEO_EXTENSIONS), MaxFileSizeValidator(50)]
document_validators = [FileExtensionValidator(DOCUMENT_EXTENSIONS), MaxFileSizeValidator(10)]


class PrivateFileSystemStorage(FileSystemStorage):
    """Files under settings.PRIVATE_MEDIA_ROOT (read on every use, so tests can override it).

    These files have no public URL; staff download them through permission-checked views.
    """

    @property
    def base_location(self):
        return self._value_or_setting(self._location, settings.PRIVATE_MEDIA_ROOT)

    @property
    def location(self):
        return os.path.abspath(self.base_location)

    def url(self, name):
        raise ValueError("Private files are not publicly addressable.")


def private_storage():
    from django.core.files.storage import storages

    return storages["private"]
