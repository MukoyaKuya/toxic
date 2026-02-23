import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toxic_project.settings')
django.setup()

from web.models import Album
album = Album.objects.first()
if album and album.cover_art:
    storage = album.cover_art.storage
    print(f"Album: {album.title}")
    print(f"Storage Class: {storage.__class__.__name__}")
    print(f"Storage Base URL: {getattr(storage, 'base_url', 'N/A')}")
    print(f"Field URL: {album.cover_art.url}")
else:
    print("No album found.")
