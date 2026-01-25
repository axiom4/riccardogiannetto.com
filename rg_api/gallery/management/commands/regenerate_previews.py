
import os
import cv2
import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from gallery.models import ImageGallery
from PIL import Image, ImageCms
import glob


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
                # STRATEGY FOR MAX COLOR FIDELITY:
                # 1. Preserve Original ICC Profile (Do NOT convert to sRGB blindly)
                #    This allows browsers to map Wide-Gamut (AdobeRGB/ProPhoto) images correctly.
                # 2. Use OpenCV Lanczos4 for sharpening/resizing.
                # 3. Embed the original ICC profile in the output WebP.

                with Image.open(image_obj.image.path) as pil_img:
                    # Capture the original ICC profile to embed later
                    original_icc_profile = pil_img.info.get('icc_profile')

                    # Ensure strict RGB mode
                    if pil_img.mode not in ('RGB', 'RGBA'):
                        pil_img = pil_img.convert('RGB')

                    # Convert to Numpy/OpenCV (BGR)
                    # We treat pixels as raw values, preserving their meaning in the original color space
                    img_array = np.array(pil_img)
                    if img_array.shape[2] == 4:
                        cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
                    else:
                        cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

                if cv_img is None:
                    continue

                original_height, original_width = cv_img.shape[:2]

                for width in widths:
                    filename = os.path.join(
                        preview_dir, f"{image_obj.pk}_{width}.webp")

                    wpercent = (width / float(original_width))
                    hsize = int((float(original_height) * float(wpercent)))

                    # HIGH QUALITY RESIZING: Lanczos4
                    resize = cv2.resize(
                        cv_img, (width, hsize), interpolation=cv2.INTER_LANCZOS4)

                    # Quality settings
                    if width <= 800:
                        quality = 65
                    elif width <= 1200:
                        quality = 75
                    else:
                        quality = 82

                    # Return to Pillow
                    if resize.shape[2] == 4:
                        result_rgb = cv2.cvtColor(resize, cv2.COLOR_BGRA2RGBA)
                    else:
                        result_rgb = cv2.cvtColor(resize, cv2.COLOR_BGR2RGB)

                    pil_result = Image.fromarray(result_rgb)

                    # Ensure RGB for JPEG (Drop Alpha channel)
                    if pil_result.mode == 'RGBA':
                        background = Image.new(
                            "RGB", pil_result.size, (255, 255, 255))
                        background.paste(pil_result, mask=pil_result.split()[
                                         3])  # 3 is the alpha channel
                        pil_result = background
                    elif pil_result.mode != 'RGB':
                        pil_result = pil_result.convert('RGB')

                    # KEY STEP: Re-embed the original ICC profile
                    save_kwargs = {
                        'quality': quality,
                        'method': 6
                    }
                    if original_icc_profile:
                        save_kwargs['icc_profile'] = original_icc_profile

                    pil_result.save(filename, 'WEBP', **save_kwargs)

                if (index + 1) % 10 == 0:
                    self.stdout.write(
                        f'Processed {index + 1}/{total_images} images...')

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error processing image ID {image_obj.pk}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            'Successfully regenerated all previews.'))
