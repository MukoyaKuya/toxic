import re


def extract_youtube_video_id(url):
    """
    Extract 11-char video ID from YouTube URL. Returns None if not a video URL.
    Handles watch, youtu.be, embed, shorts, m.youtube.
    """
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    if not url:
        return None
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if '/@' in url or '/channel/' in url or '/user/' in url or '/c/' in url or '/featured' in url:
        return None
    for pattern in [
        r'[?&]v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'm\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    ]:
        m = re.search(pattern, url, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def extract_youtube_embed_url(url):
    """
    Convert YouTube watch URL, Shorts URL, or other formats to embed URL.
    Returns None if the URL is invalid or not a video link.
    Use with iframe referrerpolicy="strict-origin-when-cross-origin" to avoid Error 153.
    """
    video_id = extract_youtube_video_id(url)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}?rel=0"
    return None
