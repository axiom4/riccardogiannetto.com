"""
Management command to auto-tag images using ML.
"""
import os
from django.core.management.base import BaseCommand
from gallery.models import ImageGallery
from gallery.ml import classify_image


class Command(BaseCommand):
    """
    Management command to auto-tag images using ML.
    """
    help = 'Automatically tags images in the gallery using the configured ML model'

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of tags for images that already have tags',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of images to process',
        )

    def handle(self, *args, **options):
        """Execute the command to auto-tag images."""
        force = options['force']
        limit = options['limit']

        queryset = ImageGallery.objects.all()

        # If not forcing, only take images with no tags
        if not force:
            queryset = queryset.filter(tags__isnull=True)

        total = queryset.count()
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"Found {total} images to process (Force={force})"))

        processed_count = 0

        for image_obj in queryset:
            if limit and processed_count >= limit:
                break

            if not image_obj.image:
                self.stdout.write(self.style.WARNING(
                    f"Skipping ID {image_obj.id}: No image file"))
                continue

            try:
                path = image_obj.image.path
                if not os.path.exists(path):
                    self.stdout.write(self.style.ERROR(
                        f"File not found: {path}"))
                    continue

                self.stdout.write(
                    f"Processing ID {image_obj.id}: {image_obj.title}...")

                tags = classify_image(path)

                if tags:
                    image_obj.tags.add(*tags)
                    self.stdout.write(self.style.SUCCESS(
                        f"  + Added tags: {', '.join(tags)}"))
                else:
                    self.stdout.write(self.style.WARNING(
                        "  - No generated tags"))

                processed_count += 1

            except Exception as e:  # pylint: disable=broad-exception-caught
                self.stdout.write(self.style.ERROR(
                    f"Error processing ID {image_obj.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Done. Processed {processed_count} images."))
