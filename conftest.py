import pytest
from django.core.cache import cache
from django.utils import translation


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path):
    """Keep uploaded and generated files out of the real media folders."""
    settings.MEDIA_ROOT = tmp_path / "media"
    settings.PRIVATE_MEDIA_ROOT = tmp_path / "private_media"


@pytest.fixture(autouse=True)
def _default_language():
    """Requests leave their language active on the thread; start every test in English
    so translated fields set without a suffix (e.g. ``title=``) land in ``title_en``."""
    with translation.override("en"):
        yield


@pytest.fixture(autouse=True)
def _clear_cache():
    """Rate-limit counters live in the cache; never let them leak between tests."""
    cache.clear()
    yield
    cache.clear()
