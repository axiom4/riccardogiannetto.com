"""Management command to update the GeoLite2-City.mmdb file from a free alternative source."""
import shutil
import urllib.request
import urllib.error
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """
    Management command to update the GeoLite2-City database file.

    This command downloads the latest GeoLite2-City.mmdb file from a public mirror
    and saves it to the configured GEOIP_PATH directory. It handles the creation
    of the directory if it doesn't exist and ensures a safe download process using
    a temporary file.
    """
    help = 'Updates the GeoLite2-City.mmdb file from a free alternative source'

    def handle(self, *args, **options):
        """Execute the command to update GeoIP database."""
        # Using a public mirror for GeoLite2-City which doesn't require a license key
        # This is a direct download of the .mmdb file
        url = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb"

        # Determine the destination path
        if hasattr(settings, 'GEOIP_PATH'):
            geoip_path = Path(settings.GEOIP_PATH)
        else:
            geoip_path = settings.BASE_DIR / 'geoip'

        if not geoip_path.exists():
            try:
                geoip_path.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                self.stdout.write(getattr(self.style, 'ERROR')(
                    f'Failed to create directory {geoip_path}: {exc}'))
                return

        target_file = geoip_path / 'GeoLite2-City.mmdb'

        self.stdout.write(f"Downloading GeoIP database from {url}...")
        self.stdout.write(f"Target file: {target_file}")

        try:
            # Download directly to the target file
            # We use a temporary file first to ensure we don't
            # corrupt the existing one if download fails
            temp_file = target_file.with_suffix('.tmp')

            try:
                urllib.request.urlretrieve(url, temp_file)

                # If download successful, move/rename to target
                shutil.move(temp_file, target_file)

                self.stdout.write(getattr(self.style, 'SUCCESS')(
                    f'Successfully updated {target_file}'))

            except urllib.error.URLError as exc:
                self.stdout.write(getattr(self.style, 'ERROR')(
                    f'Download failed: {exc}'))
            except OSError as exc:
                self.stdout.write(getattr(self.style, 'ERROR')(
                    f'File operation failed: {exc}'))

        except Exception as exc:  # pylint: disable=broad-exception-caught
            # Fallback catch-all for unexpected errors
            self.stdout.write(getattr(self.style, 'ERROR')(
                f'An unexpected error occurred: {exc}'))
