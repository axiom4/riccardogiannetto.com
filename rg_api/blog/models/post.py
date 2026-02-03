""" Blog Post model definition. """
from django.conf import settings
from django.db import models

from blog.classes import OverwriteStorage, image_directory_path
from utils.mixins import ImageOptimizationMixin
from .category import Category


class Post(ImageOptimizationMixin, models.Model):
    """
    Blog Post model.
    """
    objects = models.Manager()

    title = models.CharField(max_length=50)
    body = models.TextField()
    summary = models.CharField(max_length=250, blank=True)
    image = models.ImageField(
        null=True, upload_to=image_directory_path, storage=OverwriteStorage())
    categories = models.ManyToManyField(Category)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Post."""
        ordering = ['-created_at']

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """Save method to handle image optimization."""
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
