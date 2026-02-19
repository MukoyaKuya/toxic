from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Album, Track, TourDate, ShopItem, ShopItemImage, Footer

class TrackInline(TabularInline):
    model = Track
    extra = 1
    fields = ('title', 'duration', 'audio_file', 'youtube_link', 'is_featured')

@admin.register(Album)
class AlbumAdmin(ModelAdmin):
    list_display = ('title', 'release_date', 'track_count')
    search_fields = ('title',)
    fields = ('title', 'release_date', 'cover_art', 'spotify_link', 'youtube_link', 'apple_music_link')
    inlines = [TrackInline]

    def track_count(self, obj):
        return obj.tracks.count()
    track_count.short_description = 'Tracks'

@admin.register(Track)
class TrackAdmin(ModelAdmin):
    list_display = ('title', 'album', 'duration', 'is_featured')
    list_filter = ('is_featured', 'album')
    search_fields = ('title', 'album__title')
    fields = ('album', 'title', 'duration', 'audio_file', 'youtube_link', 'is_featured')

@admin.register(TourDate)
class TourDateAdmin(ModelAdmin):
    list_display = ('venue', 'location', 'date', 'is_sold_out')
    list_filter = ('is_sold_out', 'date')
    search_fields = ('venue', 'location')
    date_hierarchy = 'date'
    ordering = ('date',)

class ShopItemImageInline(TabularInline):
    model = ShopItemImage
    extra = 0
    max_num = 4
    fields = ('image', 'display_order')
    verbose_name = 'Design Image'
    verbose_name_plural = 'Design Images (up to 4)'

@admin.register(ShopItem)
class ShopItemAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'display_order', 'image_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    list_editable = ('is_active', 'display_order')
    fields = ('title', 'image', 'shop_link', 'is_active', 'display_order')
    inlines = [ShopItemImageInline]
    ordering = ('display_order', 'created_at')
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Design Images'

@admin.register(Footer)
class FooterAdmin(ModelAdmin):
    list_display = ('copyright_text', 'updated_at')
    fieldsets = (
        ('Footer video & image', {
            'fields': ('youtube_video_url', 'featured_image', 'lets_connect_text'),
            'description': 'YouTube video URL (watch or embed) to show in the footer. Featured image is optional for the upper section.'
        }),
        ('Logo', {
            'fields': ('logo',)
        }),
        ('Social Media Links', {
            'fields': ('instagram_link', 'twitter_link', 'facebook_link', 'youtube_link', 'spotify_link', 'music_link')
        }),
        ('Text Content', {
            'fields': ('copyright_text', 'mass_appeal_text')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one footer instance
        return not Footer.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
