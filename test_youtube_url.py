
import re

def _youtube_embed_url(url):
    """Convert YouTube watch URL to embed URL."""
    if not url or not url.strip():
        return None
    url = url.strip()
    
    # Handle mobile/shortened links logic
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Skip channel/user links
    if '/@' in url or '/channel/' in url or '/user/' in url or '/c/' in url or '/featured' in url:
        print(f"Channel URL: '{url}' -> None")
        return None

    video_id = None
    
    # Try to find video ID in various formats
    
    # Standard watch URL: v=VIDEO_ID
    m = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    if m:
        video_id = m.group(1)
        
    # Shortened URL: youtu.be/VIDEO_ID
    if not video_id:
        m = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
        if m:
            video_id = m.group(1)
            
    # Embed URL: youtube.com/embed/VIDEO_ID
    if not video_id:
        m = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', url)
        if m:
            video_id = m.group(1)

    # Shorts URL: youtube.com/shorts/VIDEO_ID
    if not video_id:
        m = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})', url)
        if m:
            video_id = m.group(1)

    if video_id:
        # Use youtube-nocookie.com for better privacy and potentially fewer restrictions
        # Add rel=0 to show related videos from the same channel
        return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0"
        
    print(f"No match for: '{url}' -> None")
    return None

test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "http://youtube.com/watch?v=dQw4w9WgXcQ&feature=shared",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ?t=10",
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1",
]

print("Testing URLs:")
for url in test_urls:
    result = _youtube_embed_url(url)
    print(f"'{url}' -> '{result}'")
