import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toxic_project.settings')
django.setup()

from web.models import Album

album = Album.objects.first()
if album and album.cover_art:
    print(f"Album: {album.title}")
    print(f"Cover Art URL: {album.cover_art.url}")
else:
    print("No album or cover art found.")
