import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
import shutil


class Command(BaseCommand):
    help = 'Downloads a free GeoIP database (GeoLite2-City.mmdb) and configures it.'

    def handle(self, *args, **options):
        # Database URL (using a reliable mirror or direct link to a free simplified DB)
        # Using the same source that worked previously: P3TERX/GeoLite.mmdb mirror
        DB_URL = "https://raw.githubusercontent.com/P3TERX/GeoLite.mmdb/download/GeoLite2-City.mmdb"

        # Determine destination path
        if hasattr(settings, 'GEOIP_PATH'):
            dest_path = settings.GEOIP_PATH
        else:
            # Fallback if not configured, though it should be if following previous steps
            base_dir = getattr(settings, 'BASE_DIR')
            dest_path = os.path.join(base_dir, 'geoip', 'GeoLite2-City.mmdb')

        dest_dir = os.path.dirname(dest_path)

        self.stdout.write(f"Target directory: {dest_dir}")
        self.stdout.write(f"Target file: {dest_path}")

        # Ensure directory exists
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            self.stdout.write(self.style.SUCCESS(
                f"Created directory: {dest_dir}"))

        self.stdout.write(
            "downloading GeoIP database... this might take a minute.")

        try:
            # Stream download to handle large file size
            with requests.get(DB_URL, stream=True) as r:
                r.raise_for_status()
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            self.stdout.write(self.style.SUCCESS(
                f"Successfully downloaded GeoIP database to {dest_path}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"Failed to download database: {e}"))
