import os
import sys
import django
from pathlib import Path

# Fix: Ensure the project root is in sys.path
# If the script is in /scripts/cleanup_duplicates.py, then its parent's parent is the root.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

print(f"--- Diagnostic Info ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Project Base Directory: {BASE_DIR}")
print(f"Python Executable: {sys.executable}")
print(f"--- Starting Cleanup ---\n")

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toxic_project.settings')
try:
    django.setup()
except Exception as e:
    print(f"Error during django.setup(): {e}")
    print("\nMore Debug Context:")
    print(f"sys.path: {sys.path}")
    raise e

from web.models import Album, SocialLink, ShopItem
from django.db.models import Count

def cleanup_duplicates():
    # 1. Cleanup Albums
    print("Searching for duplicate albums...")
    duplicates = Album.objects.values('title', 'release_date').annotate(count=Count('id')).filter(count__gt=1)
    
    for entry in duplicates:
        title = entry['title']
        release_date = entry['release_date']
        print(f"\nProcessing duplicates for album: {title} ({release_date})")
        records = Album.objects.filter(title=title, release_date=release_date).order_by('id')
        to_keep = None
        to_delete = []
        for r in records:
            is_hashed = r.cover_art and len(r.cover_art.name) > 30 and "Screenshot" in r.cover_art.name
            if is_hashed and to_keep is None:
                to_keep = r
                print(f"  Keeping ID {r.id} (found hashed image)")
            else:
                to_delete.append(r)
        if to_keep is None:
            to_keep = records[0]
            to_delete = to_delete[1:]
            print(f"  Keeping ID {to_keep.id} (fallback)")
        for r in to_delete:
            print(f"  Deleting ID {r.id}")
            r.delete()

    # 2. Cleanup SocialLinks
    print("\nSearching for duplicate social links...")
    social_dupes = SocialLink.objects.values('name', 'url').annotate(count=Count('id')).filter(count__gt=1)
    
    if not social_dupes:
        print("No duplicate social links found.")
    else:
        for entry in social_dupes:
            name = entry['name']
            url = entry['url']
            print(f"\nProcessing duplicates for social link: {name}")
            records = SocialLink.objects.filter(name=name, url=url).order_by('id')
            # Keep the first one, delete the rest
            to_keep = records[0]
            to_delete = records[1:]
            print(f"  Keeping ID {to_keep.id}")
            for r in to_delete:
                print(f"  Deleting ID {r.id}")
                r.delete()

    # 3. Activate Missing Merch
    print("\nEnsuring all relevant merch items are active...")
    target_merch = "Yankees Mboka Doba"
    shop_item = ShopItem.objects.filter(title__icontains=target_merch).first()
    if shop_item:
        if not shop_item.is_active:
            shop_item.is_active = True
            shop_item.save()
            print(f"Activated merch item: {shop_item.title}")
        else:
            print(f"Merch item '{shop_item.title}' is already active.")
    else:
        print(f"Could not find merch item matching '{target_merch}'.")

    print("\nCleanup and data fixes complete!")

if __name__ == "__main__":
    cleanup_duplicates()
