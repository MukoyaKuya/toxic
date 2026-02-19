import re
from django import template

register = template.Library()

def _extract_youtube_id(url):
    """Helper function to extract YouTube video ID from various YouTube URL formats"""
    if not url:
        return None
    
    # Pattern for youtube.com/watch?v=VIDEO_ID, youtu.be/VIDEO_ID, youtube.com/embed/VIDEO_ID
    match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    return None

@register.filter
def youtube_id(url):
    """Extract YouTube video ID from various YouTube URL formats"""
    return _extract_youtube_id(url)

@register.filter
def youtube_embed_url(url):
    """Convert YouTube URL to embed URL"""
    video_id = _extract_youtube_id(url)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return None
