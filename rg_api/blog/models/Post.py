from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from . import Category

from PIL import Image

from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

import sys

from django.utils.html import mark_safe

import cv2
import numpy as np
from blog.classes import OverwriteStorage, image_directory_path


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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None and self.image:
            _img = self.image
            self.image = None
            super(Post, self).save(*args, **kwargs)
            self.image = _img
            self.image_save()
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
            super(Post, self).save(update_fields=['image'])
        else:
            if self.image:
                self.image_save()
            super(Post, self).save(*args, **kwargs)

    def image_save(self, width=900):
        if not self.image:
            return

        # STRATEGY FOR MAX COLOR FIDELITY:
        # 1. Preserve Original ICC Profile
        # 2. Use OpenCV Lanczos4 for sharpening/resizing.
        # 3. Embed the original ICC profile in the output WEBP.

        with Image.open(self.image) as pil_img:
            original_icc_profile = pil_img.info.get('icc_profile')

            # Only preserve ICC profile if the image is already in RGB/RGBA mode.
            # Mapping CMYK profile to RGB image would result in color distortion.
            if pil_img.mode not in ('RGB', 'RGBA'):
                original_icc_profile = None
                pil_img = pil_img.convert('RGB')

            img_array = np.array(pil_img)
            if img_array.shape[2] == 4:
                cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
            else:
                cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        original_height, original_width = cv_img.shape[:2]

        if original_width > width:
            wpercent = (width / float(original_width))
            hsize = int((float(original_height) * float(wpercent)))

            # HIGH QUALITY RESIZING: Area (Better for compression)
            resize = cv2.resize(cv_img, (width, hsize),
                                interpolation=cv2.INTER_AREA)
        else:
            resize = cv_img

        # Return to Pillow
        if resize.shape[2] == 4:
            result_rgb = cv2.cvtColor(resize, cv2.COLOR_BGRA2RGBA)
        else:
            result_rgb = cv2.cvtColor(resize, cv2.COLOR_BGR2RGB)

        pil_result = Image.fromarray(result_rgb)

        # Ensure RGB
        if pil_result.mode == 'RGBA':
            background = Image.new(
                "RGB", pil_result.size, (255, 255, 255))
            background.paste(pil_result, mask=pil_result.split()[3])
            pil_result = background
        elif pil_result.mode != 'RGB':
            pil_result = pil_result.convert('RGB')

        output = BytesIO()

        # Save as WEBP
        save_kwargs = {
            'quality': 75,
            'method': 6
        }
        # Embed the original ICC profile in the output WEBP.
        if original_icc_profile:
            save_kwargs['icc_profile'] = original_icc_profile

        pil_result.save(output, 'WEBP', **save_kwargs)
        output.seek(0)

        self.image = InMemoryUploadedFile(
            output,
            'ImageField',
            "%s.webp" % self.image.name.split('.')[0],
            'image/webp',
            sys.getsizeof(output),
            None
        )

    def image_tag(self):
        return mark_safe('<img src="/%s/%s" width="150" />' % (settings.MEDIA_ROOT, self.image)) if self.image else ''

    image_tag.short_description = 'Image Preview'
