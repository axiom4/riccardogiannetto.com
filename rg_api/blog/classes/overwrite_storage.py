"""
Storage class to overwrite existing files.
"""
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """
    FileSystemStorage subclass that deletes the file if it exists,
    effectively overwriting it.
    """

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that is available in the storage system, and available
        to be written to.
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


def directory_path(instance, filename=''):
    """
    Return the path for a post file upload.
    """
    # file will be uploaded to MEDIA_ROOT/posts/<post_id>/<filename>
    return f'posts/{instance.post.id}/{filename}'


def image_directory_path(instance, filename):
    """
    Return the path for a post image upload.
    """
    # file will be uploaded to MEDIA_ROOT/posts/<id>/<filename>
    return f'posts/{instance.id}/{filename}'
