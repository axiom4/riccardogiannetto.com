"""
Gallery signals.
"""
import os
import glob
import logging
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from gallery.models import ImageGallery

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=ImageGallery)
def delete_image_on_delete(instance, **kwargs):  # pylint: disable=unused-argument
    """
    Deletes file from filesystem when corresponding `ImageGallery` object is deleted.
    Also deletes generated previews.
    
    Args:
        instance: The ImageGallery instance being deleted.
        kwargs: Additional keyword arguments from the signal.
    """
    # 1. Delete the original image file
    if instance.image:
        try:
            # save=False is critical to prevent Django from trying to save the deleted model
            instance.image.delete(save=False)
        except (OSError, ValueError) as e:
            logger.error("Error deleting file for %s: %s", instance.title, e)

    # 2. Delete generated previews
    try:
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'preview')
        # Pattern matches {pk}_*.jpg and {pk}_*.webp
        patterns = [
            os.path.join(preview_dir, f"{instance.pk}_*.jpg"),
            os.path.join(preview_dir, f"{instance.pk}_*.webp"),
        ]

        for pattern in patterns:
            for filepath in glob.glob(pattern):
                try:
                    os.remove(filepath)
                except OSError as e:
                    logger.error("Error deleting preview %s: %s", filepath, e)
    except (OSError, ValueError) as e:
        logger.error("Error cleaning up previews for %s: %s",
                     instance.title, e)
