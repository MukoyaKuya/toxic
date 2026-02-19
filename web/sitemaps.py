from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Album, TourDate

class AlbumSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self):
        return Album.objects.all().order_by('-release_date')
    
    def lastmod(self, obj):
        return obj.release_date
        
    def location(self, obj):
        return reverse('album_detail', args=[obj.pk])

class TourSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return TourDate.objects.all().order_by('date')

    def lastmod(self, obj):
        return obj.date
        
    def location(self, obj):
        return reverse('tour')

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['index', 'music', 'tour', 'contact']

    def location(self, item):
        return reverse(item)
