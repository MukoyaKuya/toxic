from django.core.cache import cache

from .utils import extract_youtube_embed_url as _youtube_embed_url_util
from .utils import extract_youtube_video_id as _extract_video_id

_FOOTER_CACHE_KEY = 'web:footer_singleton'
_FOOTER_CACHE_TTL = 300  # 5 minutes
_TOUR_SETTINGS_CACHE_KEY = 'web:tour_settings_singleton'
_TOUR_SETTINGS_CACHE_TTL = 300  # 5 minutes


def footer_context(request):
    """Make footer settings available to all templates.

    The Footer singleton is cached for 5 minutes to avoid a DB query on
    every uncached (e.g. admin-authenticated) request.
    """
    from .models import Footer

    footer = cache.get(_FOOTER_CACHE_KEY)
    if footer is None:
        footer = Footer.load()
        cache.set(_FOOTER_CACHE_KEY, footer, _FOOTER_CACHE_TTL)

    raw_url = getattr(footer, 'youtube_video_url', None) or None
    if raw_url and isinstance(raw_url, str):
        raw_url = raw_url.strip() or None
    video_id = _extract_video_id(raw_url) if raw_url else None
    # Tour settings
    from .models import TourSettings
    tour_settings = cache.get(_TOUR_SETTINGS_CACHE_KEY)
    if tour_settings is None:
        tour_settings = TourSettings.load()
        cache.set(_TOUR_SETTINGS_CACHE_KEY, tour_settings, _TOUR_SETTINGS_CACHE_TTL)

    return {
        'footer': footer,
        'footer_youtube_embed_url': _youtube_embed_url_util(raw_url) if raw_url else None,
        'footer_youtube_video_id': video_id,
        'footer_youtube_raw_url': raw_url,
        'tour_settings': tour_settings,
    }
