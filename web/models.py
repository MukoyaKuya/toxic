from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io

class Album(models.Model):
    title = models.CharField(max_length=200)
    release_date = models.DateField(db_index=True)
    cover_art = models.ImageField(upload_to='covers/')
    spotify_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True, help_text="YouTube link for the release")
    apple_music_link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if self.cover_art:
            img = Image.open(self.cover_art)
            if img.height > 800 or img.width > 800:
                output = io.BytesIO()
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                
                # Maintain original format if possible, default to JPEG
                fmt = img.format if img.format else 'JPEG'
                if fmt == 'JPEG':
                    img.save(output, format=fmt, quality=85)
                else:
                    img.save(output, format=fmt)
                output.seek(0)
                
                self.cover_art = InMemoryUploadedFile(output, 'ImageField', 
                                                    f"{self.cover_art.name.split('.')[0]}.{fmt.lower()}", 
                                                    f"image/{fmt.lower()}",
                                                    output.getbuffer().nbytes, None)
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

    def __str__(self):
        return self.title

class TourDate(models.Model):
    date = models.DateTimeField(db_index=True)
    venue = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    ticket_link = models.URLField(blank=True)
    is_sold_out = models.BooleanField(default=False, db_index=True)

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
            img = Image.open(self.image)
            if img.height > 1000 or img.width > 1000:
                output = io.BytesIO()
                img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                
                fmt = img.format if img.format else 'PNG'
                if fmt == 'JPEG':
                    img.save(output, format=fmt, quality=85)
                else:
                    img.save(output, format=fmt)
                output.seek(0)
                
                self.image = InMemoryUploadedFile(output, 'ImageField', 
                                                    f"{self.image.name.split('.')[0]}.{fmt.lower()}", 
                                                    f"image/{fmt.lower()}",
                                                    output.getbuffer().nbytes, None)
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
            img = Image.open(self.image)
            if img.height > 1000 or img.width > 1000:
                output = io.BytesIO()
                img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                
                fmt = img.format if img.format else 'PNG'
                if fmt == 'JPEG':
                    img.save(output, format=fmt, quality=85)
                else:
                    img.save(output, format=fmt)
                output.seek(0)
                
                self.image = InMemoryUploadedFile(output, 'ImageField', 
                                                    f"{self.image.name.split('.')[0]}.{fmt.lower()}", 
                                                    f"image/{fmt.lower()}",
                                                    output.getbuffer().nbytes, None)
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

class Advertisement(models.Model):
    title = models.CharField(max_length=200, help_text="Internal name for this ad")
    image = models.ImageField(upload_to='ads/', blank=True, null=True, help_text="Image creative for the ad (optional if YouTube Link is provided)")
    url = models.URLField(blank=True, help_text="Destination URL when a user clicks the standard image ad")
    youtube_link = models.URLField(blank=True, help_text="YouTube link for video ad (Prioritized over image)")
    facebook_link = models.URLField(blank=True, help_text="Facebook URL (If provided, the image acts as a cover routing to Facebook)")
    is_active = models.BooleanField(default=False, help_text="Only the first active ad will be displayed on the frontend")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.image and not self.youtube_link:
            raise ValidationError("You must provide either an Image or a YouTube Link for the advertisement.")
        if self.image and not (self.url or self.facebook_link):
             raise ValidationError("If providing an Image, you must also provide either a standard URL or a Facebook Link for the user to click.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.image:
            img = Image.open(self.image)
            # Resize ad imagery if excessively large to save bandwidth
            if img.height > 1000 or img.width > 1000:
                output = io.BytesIO()
                img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                
                fmt = img.format if img.format else 'PNG'
                if fmt == 'JPEG':
                    img.save(output, format=fmt, quality=85)
                else:
                    img.save(output, format=fmt)
                output.seek(0)
                
                self.image = InMemoryUploadedFile(output, 'ImageField', 
                                                    f"{self.image.name.split('.')[0]}.{fmt.lower()}", 
                                                    f"image/{fmt.lower()}",
                                                    output.getbuffer().nbytes, None)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"
