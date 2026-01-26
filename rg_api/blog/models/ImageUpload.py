from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from blog.models import Post
from django.utils.html import mark_safe

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from blog.classes import OverwriteStorage, directory_path
from utils.image_optimizer import ImageOptimizer


class ImageUpload(models.Model):
    title = models.CharField(max_length=250, null=False)
    image = models.ImageField(
        null=False, upload_to=directory_path, storage=OverwriteStorage())
    short_name = models.CharField(max_length=20, null=False)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img src="/%s/%s" width="150" />' % (settings.MEDIA_ROOT, self.image)) if self.image else ''

    image_tag.short_description = 'Image Preview'

    def save(self):
        output = ImageOptimizer.compress_and_resize(self.image, width=900)
        
        if output:
            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                "%s.webp" % self.image.name.split('.')[0],
                'image/webp',
                sys.getsizeof(output),
                None
            )

        super(ImageUpload, self).save()

    class Meta:
        unique_together = [["short_name", "post"]]
