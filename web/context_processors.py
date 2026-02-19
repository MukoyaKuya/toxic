import re
from .models import Footer

def _youtube_embed_url(url):
    """Convert YouTube watch URL to embed URL."""
    if not url or not url.strip():
        return None
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if '/@' in url or '/channel/' in url or '/user/' in url or '/c/' in url or '/featured' in url:
        return None
    m = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    m = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    m = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    return None

def footer_context(request):
    """Make footer settings available to all templates"""
    footer = Footer.load()
    footer_youtube_embed_url = _youtube_embed_url(footer.youtube_video_url) if getattr(footer, 'youtube_video_url', None) else None
    return {
        'footer': footer,
        'footer_youtube_embed_url': footer_youtube_embed_url,
    }
