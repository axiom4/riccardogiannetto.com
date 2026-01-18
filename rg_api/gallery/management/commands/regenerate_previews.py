
import os
import cv2
from django.core.management.base import BaseCommand
from django.conf import settings
from gallery.models import ImageGallery
import glob


class Command(BaseCommand):
    help = 'Regenerate all image previews for supported formats'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true',
                            help='Delete existing previews before regenerating')

    def handle(self, *args, **options):
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'preview')

        # Ensure preview directory exists
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir)

        if options['clean']:
            self.stdout.write('Cleaning existing previews...')
            files = glob.glob(os.path.join(preview_dir, '*.webp'))
            for f in files:
                try:
                    os.remove(f)
                except OSError as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error deleting {f}: {e}'))
            self.stdout.write(self.style.SUCCESS('Cleaned previews.'))

        images = ImageGallery.objects.all()
        # Common widths used in the application
        widths = [400, 600, 700, 800, 1000, 1200, 2500]
        total_images = images.count()

        self.stdout.write(
            f'Found {total_images} images. Starting regeneration...')

        for index, image_obj in enumerate(images):
            # Check if source file exists
            if not image_obj.image or not os.path.exists(image_obj.image.path):
                self.stdout.write(self.style.WARNING(
                    f'Source image not found for ID {image_obj.pk}: {image_obj.title}'))
                continue

            try:
                # Read image once per object
                img = cv2.imread(image_obj.image.path)
                if img is None:
                    self.stdout.write(self.style.WARNING(
                        f'Could not read image ID {image_obj.pk} with OpenCV'))
                    continue

                original_height, original_width = img.shape[:2]

                for width in widths:
                    filename = os.path.join(
                        preview_dir, f"{image_obj.pk}_{width}.webp")

                    # If clean wasn't requested, we can optionally skip if exists, but user asked to recreate.
                    # If clean is false, we might overwrite or skip. "ricreare" implies overwrite if it exists or we assume clean was passed.
                    # I will simply overwrite to ensure "regenerate" behavior.

                    # Calculate height keeping aspect ratio
                    wpercent = (width / float(original_width))
                    hsize = int((float(original_height) * float(wpercent)))

                    # Resize
                    resize = cv2.resize(img, (width, hsize),
                                        interpolation=cv2.INTER_AREA)

                    # Quality settings matches ImageGalleryViewSet
                    if width <= 800:
                        quality = 50
                    elif width <= 1200:
                        quality = 70
                    else:
                        quality = 75

                    _, im_buf_arr = cv2.imencode(
                        ".webp", resize, [int(cv2.IMWRITE_WEBP_QUALITY), quality])
                    byte_im = im_buf_arr.tobytes()

                    with open(filename, "wb") as f:
                        f.write(byte_im)

                if (index + 1) % 10 == 0:
                    self.stdout.write(
                        f'Processed {index + 1}/{total_images} images...')

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error processing image ID {image_obj.pk}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            'Successfully regenerated all previews.'))
