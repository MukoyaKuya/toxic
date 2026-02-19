from django import template
from web.utils import extract_youtube_video_id, extract_youtube_embed_url as _embed_url

register = template.Library()


@register.filter
def youtube_id(url):
    """Extract YouTube video ID from various YouTube URL formats."""
    return extract_youtube_video_id(url)


@register.filter
def youtube_embed_url(url):
    """Convert YouTube URL to embed URL (use with iframe referrerpolicy='strict-origin-when-cross-origin')."""
    return _embed_url(url)
