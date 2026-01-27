
import glob
import os
from PIL import ImageCms
from django.core.management.base import BaseCommand
from django.conf import settings
from gallery.models import ImageGallery
from utils.image_optimizer import ImageOptimizer


class Command(BaseCommand):
    help = 'Regenerate all image previews using OpenCV with Color Profile correction & manual Enhancement'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true',
                            help='Delete existing previews before regenerating')

    def handle(self, *args, **options):
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'preview')

        # Ensure preview directory exists
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir)

        # Pre-load sRGB profile
        try:
            srgb_profile = ImageCms.createProfile('sRGB')
        except ImportError:
            srgb_profile = None

        if options['clean']:
            self.stdout.write('Cleaning existing previews...')
            # Clean both WebP (old) and JPG (new) to ensure a clean slate if switching formats
            files = glob.glob(os.path.join(preview_dir, '*.webp')) + \
                glob.glob(os.path.join(preview_dir, '*.jpg'))
            for f in files:
                try:
                    os.remove(f)
                except OSError as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error deleting {f}: {e}'))
            self.stdout.write(self.style.SUCCESS('Cleaned previews.'))

        images = ImageGallery.objects.all()
        # Common widths used in the application
        widths = [400, 500, 600, 700, 800, 900, 1000, 1200, 2500]
        total_images = images.count()

        # Configure enhancements
        # 1. Saturation boost: +10% (Restores perception of depth for sRGB on wide gamut)
        SATURATION_FACTOR = 1.10
        # 2. Sharpness boost: +20% (Compensates for Lanczos smoothing on extreme downscale)
        SHARPNESS_FACTOR = 1.20

        self.stdout.write(
            f'Found {total_images} images. Starting regeneration...')

        for index, image_obj in enumerate(images):
            # Check if source file exists
            if not image_obj.image or not os.path.exists(image_obj.image.path):
                self.stdout.write(self.style.WARNING(
                    f'Source image not found for ID {image_obj.pk}: {image_obj.title}'))
                continue

            try:
                for width in widths:
                    filename = os.path.join(
                        preview_dir, f"{image_obj.pk}_{width}.webp")

                    ImageOptimizer.compress_and_resize(
                        image_obj.image.path,
                        output_path=filename,
                        width=width
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'Generated {width}px preview for {image_obj.pk}'))

                if (index + 1) % 10 == 0:
                    self.stdout.write(
                        f'Processed {index + 1}/{total_images} images...')

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error processing image ID {image_obj.pk}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            'Successfully regenerated all previews.'))
