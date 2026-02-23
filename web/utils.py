import io
import os
import re

from django.core.files.uploadedfile import InMemoryUploadedFile


def compress_image_field(image_field, max_size=800):
    """
    Resize and compress an ImageField value in-place if either dimension
    exceeds *max_size* pixels. Returns the (possibly replaced) image field
    value so it can be re-assigned before calling super().save().

    Converts JPEG and PNG to WebP for smaller file sizes (~25-35% savings).
    Preserves alpha channel for PNGs with transparency.
    """
    from PIL import Image

    img = Image.open(image_field)
    # Animated GIFs: keep original format (WebP multi-frame needs different handling)
    if getattr(img, 'is_animated', False):
        return image_field

    # Convert to RGBA for PNG/WebP alpha, RGB for JPEG
    if img.mode in ('P', 'LA', 'PA'):
        img = img.convert('RGBA')
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    output = io.BytesIO()
    if img.height > max_size or img.width > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    # Save as WebP for ~25-35% smaller files than JPEG/PNG
    # Lossy for RGB (photos), lossy with alpha for RGBA (transparent PNGs)
    has_alpha = img.mode == 'RGBA'
    save_kwargs = {'format': 'WEBP', 'quality': 85}
    if has_alpha:
        save_kwargs['method'] = 6  # Slower but smaller
    img.save(output, **save_kwargs)
    output.seek(0)

    original_name = image_field.name.rsplit('.', 1)[0]
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{original_name}.webp",
        'image/webp',
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
