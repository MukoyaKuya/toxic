import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toxic_project.settings')
django.setup()

from web.models import Album, Track, TourDate

# Clear existing data
Album.objects.all().delete()
TourDate.objects.all().delete()

print("Creating Albums...")
album1 = Album.objects.create(
    title="The Toxic Truth",
    release_date=timezone.now().date() - timedelta(days=700),
    spotify_link="https://open.spotify.com/artist/toxiclyrically",
)

album2 = Album.objects.create(
    title="Chinje",
    release_date=timezone.now().date() - timedelta(days=100),
    spotify_link="https://open.spotify.com/artist/toxiclyrically",
)

print("Creating Tracks...")
Track.objects.create(album=album1, title="Mfisadi", duration=timedelta(minutes=3, seconds=10))
Track.objects.create(album=album1, title="Euphoria", duration=timedelta(minutes=2, seconds=45))
Track.objects.create(album=album2, title="Chinje", duration=timedelta(minutes=3, seconds=30), is_featured=True)
Track.objects.create(album=album2, title="Long Story", duration=timedelta(minutes=4, seconds=0))

print("Creating Tour Dates...")
TourDate.objects.create(
    date=timezone.now() + timedelta(days=20),
    venue="The Alchemist",
    location="Nairobi, KE",
    ticket_link="https://tickets.com/toxic-nairobi",
    is_sold_out=False
)

TourDate.objects.create(
    date=timezone.now() + timedelta(days=45),
    venue="Nyali Beach Hotel",
    location="Mombasa, KE",
    ticket_link="https://tickets.com/toxic-mombasa",
    is_sold_out=False
)

TourDate.objects.create(
    date=timezone.now() + timedelta(days=60),
    venue="Unseen Nairobi",
    location="Nairobi, KE",
    ticket_link="#",
    is_sold_out=True
)

print("Database seeded successfully!")
