"""Turn YouTube/Vimeo links into embed URLs. Only these hosts may be embedded (iframes)."""

import re
from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

_YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
_VIMEO_ID = re.compile(r"^\d+$")


def embed_url(url):
    """Return a privacy-friendly embed URL, or None if the link isn't a supported video."""
    if not url:
        return None
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().removeprefix("www.").removeprefix("m.")
    parts = [p for p in parsed.path.split("/") if p]

    video_id = None
    if host == "youtu.be" and parts:
        video_id = parts[0]
    elif host in {"youtube.com", "youtube-nocookie.com"}:
        if parts[:1] == ["watch"]:
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
            video_id = parts[1]
    if video_id and _YOUTUBE_ID.match(video_id):
        return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0"

    if host in {"vimeo.com", "player.vimeo.com"} and parts:
        vimeo_id = parts[-1]
        if _VIMEO_ID.match(vimeo_id):
            return f"https://player.vimeo.com/video/{vimeo_id}"
    return None


def validate_video_url(url):
    if url and not embed_url(url):
        raise ValidationError(_("Use a YouTube or Vimeo video link."))
