from .models import Footer
from .utils import extract_youtube_embed_url as _youtube_embed_url_util
from .utils import extract_youtube_video_id as _extract_video_id


def footer_context(request):
    """Make footer settings available to all templates."""
    footer = Footer.load()
    raw_url = getattr(footer, 'youtube_video_url', None) or None
    if raw_url and isinstance(raw_url, str):
        raw_url = raw_url.strip() or None
    video_id = _extract_video_id(raw_url) if raw_url else None
    return {
        'footer': footer,
        'footer_youtube_embed_url': _youtube_embed_url_util(raw_url) if raw_url else None,
        'footer_youtube_video_id': video_id,
        'footer_youtube_raw_url': raw_url,
    }
