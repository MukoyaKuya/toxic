from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from web.sitemaps import AlbumSitemap, TourSitemap, StaticViewSitemap
from web.views import service_worker, pwa_manifest

sitemaps = {
    'static': StaticViewSitemap,
    'albums': AlbumSitemap,
    'tours': TourSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # PWA: serve from root so the service worker controls the full origin scope
    path('sw.js', service_worker, name='service_worker'),
    path('manifest.json', pwa_manifest, name='pwa_manifest'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'web.views.handler404'
handler500 = 'web.views.handler500'
