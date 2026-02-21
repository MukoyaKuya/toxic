from django.contrib.sitemaps import Sitemap
from django.db.models import Max
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
        # All tour dates live at the same /tour/ page — return it once.
        return ['tour']

    def lastmod(self, obj):
        latest = TourDate.objects.aggregate(Max('date'))['date__max']
        return latest

    def location(self, item):
        return reverse(item)

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['index', 'music', 'tour', 'contact']

    def location(self, item):
        return reverse(item)
