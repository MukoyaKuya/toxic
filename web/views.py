from django.shortcuts import render, get_object_or_404
from .models import Album, Track, TourDate, ShopItem, ShopItemImage
from django.utils import timezone
from django.db.models import Prefetch

def index(request):
    latest_releases = Album.objects.order_by('-release_date')[:2]
    upcoming_tours = TourDate.objects.filter(date__gte=timezone.now()).order_by('date')[:5]
    shop_items = ShopItem.objects.filter(is_active=True).prefetch_related(
        Prefetch('images', queryset=ShopItemImage.objects.order_by('display_order', 'id'))
    )[:3]
    return render(request, 'web/index.html', {
        'latest_releases': latest_releases,
        'upcoming_tours': upcoming_tours,
        'shop_items': shop_items
    })

def music(request):
    albums = Album.objects.all().order_by('-release_date')
    context = {'albums': albums}
    return render(request, 'web/music.html', context)

def music_list(request):
    albums = Album.objects.all().order_by('-release_date')
    context = {'albums': albums}
    return render(request, 'web/partials/music_list.html', context)

def album_detail(request, album_id):
    import re
    album = get_object_or_404(Album, pk=album_id)
    
    def extract_youtube_embed_url(url):
        """Extract YouTube embed URL from various YouTube URL formats"""
        if not url or not url.strip():
            return None
        
        # Clean the URL - remove any whitespace
        url = url.strip()
        
        # Remove URL fragments (#) and any trailing slashes
        url = url.split('#')[0].rstrip('/')
        
        # Check if this is a channel URL (can't be embedded) - return None
        if '/@' in url or '/channel/' in url or '/user/' in url or '/c/' in url or '/featured' in url:
            return None
        
        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Handle various YouTube URL formats
        video_id = None
        
        # Pattern 1: youtube.com/watch?v=VIDEO_ID (most common)
        # Match v=VIDEO_ID where VIDEO_ID is exactly 11 chars
        match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
        if match:
            video_id = match.group(1)
        
        # Pattern 2: youtu.be/VIDEO_ID
        if not video_id:
            match = re.search(r'youtu\.be\/([a-zA-Z0-9_-]{11})', url)
            if match:
                video_id = match.group(1)
        
        # Pattern 3: youtube.com/embed/VIDEO_ID
        if not video_id:
            match = re.search(r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})', url)
            if match:
                video_id = match.group(1)
        
        # Pattern 4: youtube.com/v/VIDEO_ID (older format)
        if not video_id:
            match = re.search(r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})', url)
            if match:
                video_id = match.group(1)
        
        # Validate video ID (must be exactly 11 characters, alphanumeric + _ and -)
        if video_id:
            video_id = video_id.strip()
            # Ensure it's exactly 11 characters and valid format
            if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                # Return clean embed URL
                return f"https://www.youtube.com/embed/{video_id}?rel=0"
        
        return None
    
    # Extract YouTube video ID for album (default embed)
    youtube_embed_url = extract_youtube_embed_url(album.youtube_link)
    
    # Debug: Log if extraction failed but URL exists
    if album.youtube_link and not youtube_embed_url:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to extract YouTube embed URL from: {album.youtube_link}")
    
    # Additional validation: ensure embed URL is properly formatted
    if youtube_embed_url:
        # Double-check the format
        if not youtube_embed_url.startswith('https://www.youtube.com/embed/'):
            youtube_embed_url = None
        else:
            # Extract and validate video ID one more time
            video_id_match = re.search(r'/embed/([a-zA-Z0-9_-]{11})', youtube_embed_url)
            if not video_id_match or len(video_id_match.group(1)) != 11:
                youtube_embed_url = None
    
    # Extract YouTube embed URLs for each track
    tracks_with_youtube = []
    for track in album.tracks.all():
        track_youtube_url = extract_youtube_embed_url(track.youtube_link) if hasattr(track, 'youtube_link') else None
        tracks_with_youtube.append({
            'track': track,
            'youtube_embed_url': track_youtube_url
        })
    
    return render(request, 'web/album_detail.html', {
        'album': album,
        'youtube_embed_url': youtube_embed_url,
        'tracks_with_youtube': tracks_with_youtube
    })

def tour(request):
    upcoming_dates = TourDate.objects.filter(date__gte=timezone.now()).order_by('date')
    context = {'tour_dates': upcoming_dates}
    # Only return partial if explicitly requested via query parameter
    # This prevents hx-boost navigation from returning just the partial
    if request.GET.get('partial') == 'true':
        return render(request, 'web/partials/tour_list.html', context)
    return render(request, 'web/tour.html', context)

def contact(request):
    return render(request, 'web/contact.html')
