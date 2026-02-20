from django.db import models
from .utils import compress_image_field


class Album(models.Model):
    title = models.CharField(max_length=200)
    release_date = models.DateField(db_index=True)
    cover_art = models.ImageField(upload_to='covers/')
    spotify_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True, help_text="YouTube link for the release")
    apple_music_link = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.cover_art:
            self.cover_art = compress_image_field(self.cover_art, max_size=800)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Track(models.Model):
    album = models.ForeignKey(Album, related_name='tracks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    duration = models.DurationField(null=True, blank=True)
    audio_file = models.FileField(upload_to='tracks/', blank=True)
    youtube_link = models.URLField(blank=True, help_text="YouTube link for this track")
    is_featured = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class TourDate(models.Model):
    date = models.DateTimeField(db_index=True)
    venue = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    ticket_link = models.URLField(blank=True)
    map_link = models.URLField(
        blank=True,
        help_text="Google Maps (or other) URL for directions to the venue. Paste the full link (e.g. https://maps.google.com/... or https://goo.gl/maps/...)."
    )
    is_sold_out = models.BooleanField(default=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.venue}"

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['date', 'is_sold_out']),
        ]

class ShopItem(models.Model):
    title = models.CharField(max_length=200, help_text="Product title or name")
    image = models.ImageField(upload_to='shop/', help_text="Thumbnail image (transparent PNG recommended)")
    shop_link = models.URLField(help_text="Link to product page")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Show this item in the merch section")
    display_order = models.PositiveIntegerField(default=0, db_index=True, help_text="Order in which items are displayed (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_image_field(self.image, max_size=1000)
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_image_field(self.image, max_size=1000)
        super().save(*args, **kwargs)

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
    featured_image_height = models.PositiveIntegerField(
        default=400,
        help_text="Height of the featured image in pixels (e.g. 300, 400, 500). Width scales automatically."
    )
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

class SocialLink(models.Model):
    """Dynamic social media links for the footer"""
    footer = models.ForeignKey(Footer, on_delete=models.CASCADE, related_name='social_links')
    name = models.CharField(max_length=50, help_text="Name of the social network (e.g. Email, Facebook, Spotify)")
    url = models.URLField(help_text="URL for the link (can be a mailto: link for emails)")
    icon = models.FileField(upload_to='footer/socials/', help_text="Upload an SVG or transparent PNG logo")
    order = models.PositiveIntegerField(default=0, help_text="Order in which they appear (lower number first)")

    class Meta:
        ordering = ['order']
        verbose_name = 'Social Link'
        verbose_name_plural = 'Social Links'

    def __str__(self):
        return self.name

class Advertisement(models.Model):
    title = models.CharField(max_length=200, help_text="Internal name for this ad")
    image = models.ImageField(upload_to='ads/', blank=True, null=True, help_text="Image creative for the ad (optional if YouTube Link is provided)")
    url = models.URLField(blank=True, help_text="Destination URL when a user clicks the standard image ad")
    youtube_link = models.URLField(blank=True, help_text="YouTube link for video ad (Prioritized over image)")
    facebook_link = models.URLField(blank=True, help_text="Facebook URL (If provided, the image acts as a cover routing to Facebook)")
    is_active = models.BooleanField(default=False, help_text="Only the first active ad will be displayed on the frontend")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.image and not self.youtube_link:
            raise ValidationError("You must provide either an Image or a YouTube Link for the advertisement.")
        if self.image and not (self.url or self.facebook_link):
             raise ValidationError("If providing an Image, you must also provide either a standard URL or a Facebook Link for the user to click.")

    def save(self, *args, **kwargs):
        # Note: clean() is intentionally NOT called here; Django admin calls it
        # automatically during form validation. Calling it from save() would
        # raise a ValidationError on programmatic saves (e.g. fixtures, shell).
        if self.image:
            self.image = compress_image_field(self.image, max_size=1000)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"

class TourSettings(models.Model):
    """Tour page settings - singleton model for tour page configuration"""
    background_image = models.ImageField(
        upload_to='tour/',
        blank=True,
        help_text="Background image or GIF for the tour page. If not set, defaults to static image."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tour Settings'
        verbose_name_plural = 'Tour Settings'

    def __str__(self):
        return "Tour Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        if self.background_image:
            self.background_image = compress_image_field(self.background_image, max_size=2000)
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
