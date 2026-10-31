import pytest
from django.utils import translation


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path):
    """Keep uploaded and generated files out of the real media folder."""
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture(autouse=True)
def _default_language():
    """Requests leave their language active on the thread; start every test in English
    so translated fields set without a suffix (e.g. ``title=``) land in ``title_en``."""
    with translation.override("en"):
        yield
