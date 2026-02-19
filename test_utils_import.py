
import os
import sys
import django
from django.conf import settings

# Setup Django environment (minimal)
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toxic_project.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup failed (might not be needed for simple utils import): {e}")

from web.utils import extract_youtube_embed_url

test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "http://youtube.com/watch?v=dQw4w9WgXcQ&feature=shared",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ?t=10",
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1",
]

print("Testing web.utils.extract_youtube_embed_url:")
for url in test_urls:
    result = extract_youtube_embed_url(url)
    print(f"'{url}' -> '{result}'")
