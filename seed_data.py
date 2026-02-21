import os
import django
from django.utils import timezone
from datetime import timedelta
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toxic_project.settings')
django.setup()

from web.models import Album, Track, TourDate, ShopItem, ShopItemImage, Footer, SocialLink, Advertisement, TourSettings

# Helper to find static files in container
def get_static_file(path):
    # Try common container paths
    for base in ['/app', '.']:
        full_path = os.path.join(base, path)
        if os.path.exists(full_path):
            return File(open(full_path, 'rb'))
    return None

def seed_database():
    print("Cleaning existing data...")
    Album.objects.all().delete()
    TourDate.objects.all().delete()
    ShopItem.objects.all().delete()
    Advertisement.objects.all().delete()
    # Footer and TourSettings are singletons, we'll just update them

    print("Creating Albums...")
    album1 = Album.objects.create(
        title="The Toxic Truth",
        release_date=timezone.now().date() - timedelta(days=700),
        spotify_link="https://open.spotify.com/artist/toxiclyrically",
        youtube_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )
    cover1 = get_static_file('static/images/Section one HR.jpg')
    if cover1:
        album1.cover_art.save('toxic_truth.jpg', cover1)

    album2 = Album.objects.create(
        title="Chinje",
        release_date=timezone.now().date() - timedelta(days=100),
        spotify_link="https://open.spotify.com/artist/toxiclyrically",
        youtube_link="https://www.youtube.com/watch?v=60ItHLz5WEA",
    )
    
    print("Creating Tracks...")
    Track.objects.create(album=album1, title="Mfisadi", duration=timedelta(minutes=3, seconds=10))
    Track.objects.create(album=album1, title="Euphoria", duration=timedelta(minutes=2, seconds=45))
    Track.objects.create(album=album2, title="Chinje", duration=timedelta(minutes=3, seconds=30), is_featured=True)
    Track.objects.create(album=album2, title="Long Story", duration=timedelta(minutes=4, seconds=0))

    print("Creating Tour Dates...")
    TourDate.objects.create(
        date=timezone.now() + timedelta(days=20, hours=20),
        venue="The Alchemist",
        location="Nairobi, KE",
        ticket_link="https://tickets.com/toxic-nairobi",
        is_sold_out=False
    )
    TourDate.objects.create(
        date=timezone.now() + timedelta(days=45, hours=21),
        venue="Nyali Beach Hotel",
        location="Mombasa, KE",
        ticket_link="https://tickets.com/toxic-mombasa",
        is_sold_out=False
    )

    print("Creating Shop Items...")
    shop1 = ShopItem.objects.create(
        title="Toxic Signature Tee",
        shop_link="https://shop.toxiclyrically.com/product/tee",
        display_order=1
    )
    img1 = get_static_file('web/static/icons/icon-512.png')
    if img1:
        shop1.image.save('tee.png', img1)

    print("Setting up Footer...")
    footer = Footer.load()
    footer.lets_connect_text = "LET'S VIBE"
    footer.youtube_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    footer.copyright_text = "TOXIC LYRICALLY"
    footer.mass_appeal_text = "mass appeal"
    footer.save()

    # Add some social links
    SocialLink.objects.all().delete()
    SocialLink.objects.create(footer=footer, name="Instagram", url="https://instagram.com/toxiclyrically", order=1)
    SocialLink.objects.create(footer=footer, name="YouTube", url="https://youtube.com/@toxiclyrically", order=2)
    SocialLink.objects.create(footer=footer, name="Spotify", url="https://open.spotify.com/artist/toxiclyrically", order=3)

    print("Setting up Tour Settings...")
    ts = TourSettings.load()
    bg = get_static_file('static/images/Section one HR.jpg')
    if bg:
        ts.background_image.save('tour_bg.jpg', bg)
    ts.save()

    print("Creating Advertisement...")
    ad = Advertisement.objects.create(
        title="New Single Out Now",
        youtube_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        is_active=True
    )

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
