import io
import os
import re

from django.core.files.uploadedfile import InMemoryUploadedFile


def compress_image_field(image_field, max_size=800):
    """
    Resize and compress an ImageField value in-place if either dimension
    exceeds *max_size* pixels. Returns the (possibly replaced) image field
    value so it can be re-assigned before calling super().save().

    Detects format from the file extension when PIL cannot determine it
    (e.g. freshly opened InMemoryUploadedFile), avoiding accidental JPEG
    conversion of PNG images that may have transparency.
    """
    from PIL import Image

    img = Image.open(image_field)
    if img.height <= max_size and img.width <= max_size:
        return image_field  # No resize needed

    # Prefer PIL's detected format, fall back to extension, then JPEG.
    fmt = img.format
    if not fmt:
        ext = os.path.splitext(image_field.name)[-1].lstrip('.').upper()
        fmt = ext if ext in ('JPEG', 'JPG', 'PNG', 'WEBP', 'GIF') else 'JPEG'
    if fmt == 'JPG':
        fmt = 'JPEG'

    output = io.BytesIO()
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    if fmt == 'JPEG':
        img.save(output, format=fmt, quality=85)
    else:
        img.save(output, format=fmt)
    output.seek(0)

    original_name = image_field.name.rsplit('.', 1)[0]
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{original_name}.{fmt.lower()}",
        f"image/{fmt.lower()}",
        output.getbuffer().nbytes,
        None,
    )


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
