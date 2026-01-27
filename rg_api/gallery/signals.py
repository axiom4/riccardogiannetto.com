import os
import glob
import logging
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from gallery.models import ImageGallery

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=ImageGallery)
def delete_image_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding `ImageGallery` object is deleted.
    Also deletes generated previews.
    """
    # 1. Delete the original image file
    if instance.image:
        try:
            # save=False is critical to prevent Django from trying to save the deleted model
            instance.image.delete(save=False)
        except Exception as e:
            logger.error(f"Error deleting file for {instance.title}: {e}")

    # 2. Delete generated previews
    try:
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'preview')
        # Pattern matches {pk}_*.jpg and {pk}_*.webp
        patterns = [
            os.path.join(preview_dir, f"{instance.pk}_*.jpg"),
            os.path.join(preview_dir, f"{instance.pk}_*.webp"),
        ]

        for pattern in patterns:
            for f in glob.glob(pattern):
                try:
                    os.remove(f)
                except OSError as e:
                    logger.error(f"Error deleting preview {f}: {e}")

    except Exception as e:
        logger.error(f"Error cleaning up previews for {instance.title}: {e}")
