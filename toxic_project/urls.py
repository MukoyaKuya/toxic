from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from web.sitemaps import AlbumSitemap, TourSitemap, StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'albums': AlbumSitemap,
    'tours': TourSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'web.views.handler404'
handler500 = 'web.views.handler500'
