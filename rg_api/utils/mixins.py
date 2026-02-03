"""
Common model mixins.
"""
import sys
from django.conf import settings
from django.db import models
from django.utils.html import mark_safe
from django.core.files.uploadedfile import InMemoryUploadedFile
from .image_optimizer import ImageOptimizer


class ImageOptimizationMixin(models.Model):
    """
    Mixin for models with an 'image' field to handle optimization and preview.
    Requires 'image' field on the model.
    """
    class Meta:
        """Meta options for ImageOptimizationMixin."""
        abstract = True

    def image_save(self, width=900):
        """Optimize and resize image."""
        if not hasattr(self, 'image') or not self.image:
            return

        output = ImageOptimizer.compress_and_resize(self.image, width=width)

        if output:
            name = self.image.name.split('.')[0]
            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{name}.webp",
                'image/webp',
                sys.getsizeof(output),
                None
            )

    def image_tag(self):
        """Return HTML for image preview."""
        if hasattr(self, 'image') and self.image:
            return mark_safe(
                f'<img src="/{settings.MEDIA_ROOT}/{self.image}" width="150" />'
            )
        return ''
    image_tag.short_description = 'Image Preview'
