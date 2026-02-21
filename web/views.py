import logging
from pathlib import Path
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Prefetch, Max
from django.db import connection
from django.http import JsonResponse, FileResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.paginator import Paginator
from django.contrib.staticfiles import finders
from .models import Album, Track, TourDate, ShopItem, ShopItemImage, Advertisement
from .utils import extract_youtube_embed_url

logger = logging.getLogger(__name__)

def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'healthy'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)

def index(request):
    # Cache key includes latest tour date update so admin changes (e.g. map_link) show immediately
    tour_cache_stamp = TourDate.objects.aggregate(Max('updated_at'))['updated_at__max']
    cache_key = 'web:index:%s' % (tour_cache_stamp or 'none')
    response = cache.get(cache_key)
    if response is not None:
        return response
    latest_releases = Album.objects.order_by('-release_date')[:2]
    upcoming_tours = TourDate.objects.filter(date__gte=timezone.now()).order_by('date')[:5]
    shop_items = ShopItem.objects.filter(is_active=True).prefetch_related(
        Prefetch('images', queryset=ShopItemImage.objects.order_by('display_order', 'id'))
    )[:3]
    response = render(request, 'web/index.html', {
        'latest_releases': latest_releases,
        'upcoming_tours': upcoming_tours,
        'shop_items': shop_items
    })
    cache.set(cache_key, response, 60 * 15)  # 15 minutes
    return response

def _music_cache_stamp():
    album_max = Album.objects.aggregate(Max('updated_at'))['updated_at__max']
    track_max = Track.objects.aggregate(Max('updated_at'))['updated_at__max']
    return max(album_max, track_max) if (album_max or track_max) else 'none'

def music(request):
    # Cache key includes latest album/track update so admin changes show immediately
    page_number = request.GET.get('page', '1')
    cache_key = 'web:music:%s:%s' % (page_number, _music_cache_stamp())
    response = cache.get(cache_key)
    if response is not None:
        return response
    album_list = Album.objects.all().order_by('-release_date')
    paginator = Paginator(album_list, 6)  # 6 per page
    albums = paginator.get_page(page_number)
    response = render(request, 'web/music.html', {'albums': albums})
    cache.set(cache_key, response, 60 * 15)
    return response

def music_list(request):
    # Cache key includes latest album/track update so admin changes show immediately
    page_number = request.GET.get('page', '1')
    cache_key = 'web:music_list:%s:%s' % (page_number, _music_cache_stamp())
    response = cache.get(cache_key)
    if response is not None:
        return response
    album_list = Album.objects.all().order_by('-release_date')
    paginator = Paginator(album_list, 6)  # 6 per page
    albums = paginator.get_page(page_number)
    response = render(request, 'web/partials/music_list.html', {'albums': albums})
    cache.set(cache_key, response, 60 * 15)
    return response

def album_detail(request, album_id):
    album = get_object_or_404(Album.objects.prefetch_related('tracks'), pk=album_id)
    # Cache key includes album and ad update times so admin changes show immediately
    ad_cache_stamp = Advertisement.objects.aggregate(Max('updated_at'))['updated_at__max']
    cache_key = 'web:album_detail:%s:%s:%s' % (album_id, album.updated_at or 'none', ad_cache_stamp or 'none')
    response = cache.get(cache_key)
    if response is not None:
        return response
    youtube_embed_url = extract_youtube_embed_url(album.youtube_link)
    if album.youtube_link and not youtube_embed_url:
        logger.warning("Failed to extract YouTube embed URL from: %s", album.youtube_link)
    tracks_with_youtube = [
        {'track': track, 'youtube_embed_url': extract_youtube_embed_url(track.youtube_link)}
        for track in album.tracks.all()
    ]
    
    ad = Advertisement.objects.filter(is_active=True).first()
    ad_youtube_embed_url = extract_youtube_embed_url(ad.youtube_link) if ad and ad.youtube_link else None
    
    response = render(request, 'web/album_detail.html', {
        'album': album,
        'youtube_embed_url': youtube_embed_url,
        'tracks_with_youtube': tracks_with_youtube,
        'ad': ad,
        'ad_youtube_embed_url': ad_youtube_embed_url,
    })
    cache.set(cache_key, response, 60 * 15)  # 15 minutes
    return response

def tour(request):
    # Cache key includes latest tour date update so admin changes show immediately
    tour_cache_stamp = TourDate.objects.aggregate(Max('updated_at'))['updated_at__max']
    is_partial = request.GET.get('partial') == 'true'
    cache_key = 'web:tour:%s:%s' % (tour_cache_stamp or 'none', 'partial' if is_partial else 'full')
    response = cache.get(cache_key)
    if response is not None:
        return response
    upcoming_dates = TourDate.objects.filter(date__gte=timezone.now()).order_by('date')
    context = {'tour_dates': upcoming_dates}
    # Only return partial if explicitly requested via query parameter
    # This prevents hx-boost navigation from returning just the partial
    if is_partial:
        response = render(request, 'web/partials/tour_list.html', context)
    else:
        response = render(request, 'web/tour.html', context)
    cache.set(cache_key, response, 60 * 15)  # 15 minutes
    return response

@cache_page(60 * 15)
def contact(request):
    return render(request, 'web/contact.html')

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

# ── PWA views ────────────────────────────────────────────────────

def service_worker(request):
    """Serve sw.js from root path so it controls the full origin scope."""
    path = Path(finders.find('sw.js'))
    response = FileResponse(path.open('rb'), content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response

def pwa_manifest(request):
    """Serve manifest.json from root path as required by PWA spec."""
    path = Path(finders.find('manifest.json'))
    response = FileResponse(path.open('rb'), content_type='application/manifest+json')
    response['Cache-Control'] = 'public, max-age=86400'
    return response
