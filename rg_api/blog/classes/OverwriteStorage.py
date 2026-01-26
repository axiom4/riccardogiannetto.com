
from django.conf import settings

from PIL import Image

from django.core.files.storage import FileSystemStorage
import os


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


def directory_path(instance, filename=''):
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
    return 'posts/{0}/{1}'.format(instance.post.id, filename)


def image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
    return 'posts/{0}/{1}'.format(instance.id, filename)
