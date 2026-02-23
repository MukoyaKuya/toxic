import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toxic_project.settings')
django.setup()

print(f"GCS_BUCKET_NAME environment: '{os.environ.get('GCS_BUCKET_NAME')}'")
print(f"settings.GCS_BUCKET_NAME: '{settings.GCS_BUCKET_NAME}'")
print(f"settings.MEDIA_URL: '{settings.MEDIA_URL}'")
print(f"settings.STORAGES: {settings.STORAGES}")
