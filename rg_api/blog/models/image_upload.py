"""
Image Upload model.
"""
from django.db import models
from django.conf import settings

from blog.classes import OverwriteStorage, directory_path
from utils.mixins import ImageOptimizationMixin
from .post import Post


class ImageUpload(ImageOptimizationMixin, models.Model):
    """
    Model for uploading images associated with a post.
    """
    objects = models.Manager()

    title = models.CharField(max_length=250, null=False)
    image = models.ImageField(
        null=False, upload_to=directory_path, storage=OverwriteStorage())
    short_name = models.CharField(max_length=20, null=False)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for ImageUpload."""
        verbose_name_plural = "Image uploads"

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """Save method to handle image optimization."""
        self.image_save()
        super().save(*args, **kwargs)
