from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from . import Category

from django.core.files.uploadedfile import InMemoryUploadedFile

import sys
from django.utils.html import mark_safe

from blog.classes import OverwriteStorage, image_directory_path
from utils.image_optimizer import ImageOptimizer


class Post(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField()
    summary = models.CharField(max_length=250, blank=True)
    image = models.ImageField(
        null=True, upload_to=image_directory_path, storage=OverwriteStorage())
    categories = models.ManyToManyField(Category)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None and self.image:
            _img = self.image
            self.image = None
            super().save(*args, **kwargs)
            self.image = _img
            self.image_save()
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
            super().save(update_fields=['image'])
        else:
            if self.image:
                self.image_save()
            super().save(*args, **kwargs)

    def image_save(self, width=900):
        if not self.image:
            return

        output = ImageOptimizer.compress_and_resize(self.image, width=width)

        if output:
            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{self.image.name.split('.')[0]}.webp",
                'image/webp',
                sys.getsizeof(output),
                None
            )

    def image_tag(self):
        return mark_safe(f'<img src="/{settings.MEDIA_ROOT}/{self.image}" width="150" />') if self.image else ''

    image_tag.short_description = 'Image Preview'
