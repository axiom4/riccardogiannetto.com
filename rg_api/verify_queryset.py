from gallery.models import ImageGallery
import os
import sys
import django

# Configure Django settings
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rg_api.settings')

print("Setting up Django...")
try:
    django.setup()
    print("Django setup complete.")
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)


print("Testing VALID query (no slug)...")
try:
    qs = ImageGallery.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).exclude(latitude=0, longitude=0).only('id', 'title', 'latitude', 'longitude')
    print(f"Query successful. Found {qs.count()} locations.")
except Exception as e:
    print(f"VALID Query FAILED: {e}")

print("Testing INVALID query (with slug)...")
try:
    qs_bad = ImageGallery.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).exclude(latitude=0, longitude=0).only('id', 'title', 'latitude', 'longitude', 'slug')
    # Force evaluation
    count = qs_bad.count()
    # Accessing the field 'slug' on a result would definitely fail if deferred,
    # but .only() validation usually happens at interaction.
    # For .only(), if field doesn't exist, django throws FieldError immediately?
    print(f"INVALID Query oddly successful? Count: {count}")
except Exception as e:
    print(f"INVALID Query FAILED as expected: {e}")
