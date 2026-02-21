import os
import django
from django.utils import timezone
from datetime import timedelta
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toxic_project.settings')
django.setup()

from web.models import Album, Track, TourDate, ShopItem, ShopItemImage, Footer, SocialLink, Advertisement, TourSettings

# Helper to find static files in container
def get_seeding_file(filename):
    # These were copied to static/seeding_assets during build
    for base in ['/app', '.']:
        full_path = os.path.join(base, 'static/seeding_assets', filename)
        if os.path.exists(full_path):
            return File(open(full_path, 'rb'))
    return None

def seed_database():
    print("Cleaning existing data...")
    Album.objects.all().delete()
    Track.objects.all().delete()
    TourDate.objects.all().delete()
    ShopItem.objects.all().delete()
    Advertisement.objects.all().delete()
    SocialLink.objects.all().delete()

    print("Setting up Footer (Singleton)...")
    footer = Footer.load()
    footer.lets_connect_text = "LET'S CONNECT"
    footer.youtube_video_url = "https://www.youtube.com/watch?v=OtwmNODXyW8"
    footer.instagram_link = "https://www.instagram.com/_toxic_lyrikali/?hl=en"
    footer.facebook_link = "https://www.facebook.com/p/T%C3%B3xic-Lyrikali-100077999702139/"
    footer.youtube_link = "https://www.youtube.com/@mbokadoba"
    footer.music_link = "https://music.apple.com/ke/artist/toxic-lyrikali/1667118048"
    footer.copyright_text = "MBOKADOBA"
    footer.mass_appeal_text = "Toxic Lyrically"
    
    logo = get_seeding_file('GfuFL__XIAQrtSC.png')
    if logo:
        footer.logo.save('logo.png', logo)
    
    feat_img = get_seeding_file('lumina-enhanced-1771596851887_1_C61jDaK.png')
    if feat_img:
        footer.featured_image.save('footer_feat.png', feat_img)
    
    footer.save()

    print("Creating Social Links...")
    SocialLink.objects.create(footer=footer, name="Instagram", url=footer.instagram_link, order=0)
    SocialLink.objects.create(footer=footer, name="Facebook", url=footer.facebook_link, order=1)
    SocialLink.objects.create(footer=footer, name="YouTube", url=footer.youtube_link, order=2)
    SocialLink.objects.create(footer=footer, name="Music", url=footer.music_link, order=3)
    SocialLink.objects.create(footer=footer, name="Email", url="mailto:bookings@toxiclyrikali.com", order=4)

    print("Creating Albums & Tracks...")
    # Album 2: Roteen
    roteen = Album.objects.create(
        title="Roteen",
        release_date=timezone.datetime(2025, 12, 29).date(),
        spotify_link="https://open.spotify.com/track/3idc9sTmZiNlvOsH657MUJ",
        youtube_link="https://www.youtube.com/@mbokadoba/featured",
        apple_music_link="https://music.apple.com/ke/album/chinje-single/1841252888"
    )
    cover_roteen = get_seeding_file('lumina-enhanced-1771405340003.png')
    if cover_roteen:
        roteen.cover_art.save('roteen.png', cover_roteen)
    
    Track.objects.create(album=roteen, title="Chinje", duration=timedelta(minutes=3, seconds=30), youtube_link="https://www.youtube.com/watch?v=3gpYhCNNxko", is_featured=True)
    Track.objects.create(album=roteen, title="Sick", duration=timedelta(minutes=3, seconds=15), youtube_link="https://www.youtube.com/watch?v=iqMIjKe-HGs", is_featured=True)
    Track.objects.create(album=roteen, title="Thugnificent", duration=timedelta(minutes=2, seconds=52), youtube_link="https://www.youtube.com/watch?v=kNwpbsFdU3Q", is_featured=True)

    # Album 3: Dumpsite
    dumpsite = Album.objects.create(
        title="Dumpsite",
        release_date=timezone.datetime(2026, 2, 16).date(),
        spotify_link="https://open.spotify.com/album/3Sog79yWAUA8ozZ5L9fSVQ",
        youtube_link="https://www.youtube.com/watch?v=EzxnWWQHhw4",
        apple_music_link="https://music.apple.com/ke/artist/toxic-lyrikali/1667118048"
    )
    cover_dumpsite = get_seeding_file('lumina-enhanced-1771487030934.png')
    if cover_dumpsite:
        dumpsite.cover_art.save('dumpsite.png', cover_dumpsite)
    
    Track.objects.create(album=dumpsite, title="Dumpsite", duration=timedelta(minutes=2, seconds=40), youtube_link="https://www.youtube.com/watch?v=DrJ2yPlBTq8", is_featured=True)

    # Album 4: Bad Everyday
    bad_everyday = Album.objects.create(
        title="Bad Everyday",
        release_date=timezone.datetime(2026, 2, 19).date(),
        youtube_link="https://www.youtube.com/watch?v=DrJ2yPlBTq8"
    )
    cover_bad = get_seeding_file('Screenshot_2026-02-19_195248.png')
    if cover_bad:
        bad_everyday.cover_art.save('bad_everyday.png', cover_bad)
    
    Track.objects.create(album=bad_everyday, title="Bad Everyday", duration=timedelta(minutes=2, seconds=52), youtube_link="https://www.youtube.com/watch?v=DrJ2yPlBTq8", is_featured=True)

    print("Creating Shop Item...")
    shop_item = ShopItem.objects.create(
        title="safisha pro restoration",
        shop_link="https://music.apple.com/ke/artist/toxic-lyrikali/1667118048",
        is_active=True,
        display_order=0
    )
    shirt_img = get_seeding_file('safisha-pro-restoration-1771437212829.png')
    if shirt_img:
        shop_item.image.save('merch.png', shirt_img)

    print("Creating Tour Dates...")
    TourDate.objects.create(
        date=timezone.now() + timedelta(days=30),
        venue="The Alchemist Bar",
        location="Nairobi, KE",
        ticket_link="https://mtickets.com/events/toxic-live",
    )

    print("Setting up Tour Settings...")
    ts = TourSettings.load()
    ts.save() # Use default or existing

    print("Database synced with local state successfully!")

if __name__ == "__main__":
    seed_database()
