from django.db import models

class Album(models.Model):
    title = models.CharField(max_length=200)
    release_date = models.DateField()
    cover_art = models.ImageField(upload_to='covers/')
    spotify_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True, help_text="YouTube link for the release")
    apple_music_link = models.URLField(blank=True)

    def __str__(self):
        return self.title

class Track(models.Model):
    album = models.ForeignKey(Album, related_name='tracks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    duration = models.DurationField(null=True, blank=True)
    audio_file = models.FileField(upload_to='tracks/', blank=True)
    youtube_link = models.URLField(blank=True, help_text="YouTube link for this track")
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class TourDate(models.Model):
    date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    ticket_link = models.URLField(blank=True)
    is_sold_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.venue}"

    class Meta:
        ordering = ['date']

class ShopItem(models.Model):
    title = models.CharField(max_length=200, help_text="Product title or name")
    image = models.ImageField(upload_to='shop/', help_text="Thumbnail image (transparent PNG recommended)")
    shop_link = models.URLField(help_text="Link to product page")
    is_active = models.BooleanField(default=True, help_text="Show this item in the merch section")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which items are displayed (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['display_order', 'created_at']
        verbose_name = 'Shop Item'
        verbose_name_plural = 'Shop Items'

class ShopItemImage(models.Model):
    shop_item = models.ForeignKey(ShopItem, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shop/designs/', help_text="Design variation image (up to 4 images per item)")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which images are displayed")

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Shop Item Image'
        verbose_name_plural = 'Shop Item Images'
        
    def __str__(self):
        return f"{self.shop_item.title} - Image {self.display_order + 1}"

class Footer(models.Model):
    """Footer settings - singleton model for footer configuration"""
    logo = models.ImageField(upload_to='footer/', blank=True, help_text="Upload logo image for MBOKADOBA (replaces text)")
    featured_image = models.ImageField(upload_to='footer/', blank=True, help_text="Optional image for footer upper section (e.g. album cover)")
    youtube_video_url = models.URLField(blank=True, help_text="YouTube video URL to embed in footer (e.g. https://www.youtube.com/watch?v=VIDEO_ID)")
    instagram_link = models.URLField(blank=True, help_text="Instagram profile URL")
    twitter_link = models.URLField(blank=True, help_text="X (Twitter) profile URL")
    facebook_link = models.URLField(blank=True, help_text="Facebook profile URL")
    youtube_link = models.URLField(blank=True, help_text="YouTube channel URL (for social icon)")
    spotify_link = models.URLField(blank=True, help_text="Spotify profile URL")
    music_link = models.URLField(blank=True, help_text="Music platform link (e.g., Apple Music, SoundCloud)")
    copyright_text = models.CharField(max_length=200, default="MBOKADOBA", help_text="Copyright holder name")
    mass_appeal_text = models.CharField(max_length=200, default="mass appeal", help_text="Mass appeal label text")
    lets_connect_text = models.CharField(max_length=100, default="LET'S CONNECT", blank=True, help_text="Heading above social / video area")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Footer Settings'
        verbose_name_plural = 'Footer Settings'

    def __str__(self):
        return "Footer Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
