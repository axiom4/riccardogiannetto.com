from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from datetime import datetime

from gallery.models import Gallery
from PIL import Image, ExifTags
from taggit.managers import TaggableManager


class ImageGallery(models.Model):
    title = models.CharField(max_length=250, null=False, blank=False)
    image = models.ImageField(
        null=False
    )
    gallery = models.ForeignKey(
        Gallery, related_name='images', on_delete=models.CASCADE)

    tags = TaggableManager(blank=True)

    width = models.IntegerField()
    height = models.IntegerField()

    author = models.ForeignKey(
        User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    camera_model = models.CharField(max_length=250, blank=True)
    lens_model = models.CharField(max_length=250, blank=True)
    iso_speed = models.IntegerField(null=True, blank=True)
    aperture_f_number = models.FloatField(null=True, blank=True)
    shutter_speed = models.FloatField(null=True, blank=True)
    focal_length = models.FloatField(null=True, blank=True)

    artist = models.CharField(max_length=250, blank=True)
    copyright = models.CharField(max_length=250, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=250, blank=True)

    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe(f'<img src="{settings.IMAGE_GENERATOR_BASE_URL}/{self.id}/width/700" width="150" />') if self.image else ''

    image_tag.short_description = 'Image Preview'

    def save(self, *args, **kwargs):
        if self.image:
            with Image.open(self.image) as img:
                width, height = img.size
                exif_data = img._getexif()

                if exif_data:
                    self.extract_exif_data(exif_data)

                self.width = width
                self.height = height

        super().save(*args, **kwargs)

    def extract_exif_data(self, exif_data):
        exif_mapping = {
            'Model': 'camera_model',
            'LensModel': 'lens_model',
            'ISOSpeedRatings': 'iso_speed',
            'FNumber': 'aperture_f_number',
            'FocalLength': 'focal_length',
            'Artist': 'artist',
            'DateTimeOriginal': 'date',
            'Copyright': 'copyright'
        }

        def get_float(val):
            try:
                # Handle tuple/list (numerator, denominator)
                if isinstance(val, (tuple, list)) and len(val) == 2:
                    if float(val[1]) != 0:
                        return float(val[0]) / float(val[1])
                    return 0.0
                # Handle Pillow IFDRational (has numerator/denominator attrs)
                if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                    return float(val)
                return float(val)
            except (ValueError, TypeError):
                return None

        # Handle Shutter Speed Priority: ExposureTime (33434) > ShutterSpeedValue (37377)
        exp_time = exif_data.get(33434)
        shutter_val = exif_data.get(37377)

        if exp_time:
            self.shutter_speed = get_float(exp_time)
        elif shutter_val:
            apex = get_float(shutter_val)
            if apex is not None:
                self.shutter_speed = 1 / (2 ** apex)

        for key, val in exif_data.items():
            tag_name = ExifTags.TAGS.get(key)
            if tag_name:
                attribute = exif_mapping.get(tag_name)
                if attribute:
                    if attribute == 'date':
                        try:
                            self.date = datetime.strptime(
                                str(val), '%Y:%m:%d %H:%M:%S')
                        except (ValueError, TypeError):
                            pass
                    elif attribute in ['aperture_f_number', 'focal_length']:
                        f_val = get_float(val)
                        if f_val is not None:
                            setattr(self, attribute, f_val)
                    else:
                        setattr(self, attribute, val)

    class Meta:
        verbose_name_plural = 'images'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
            models.Index(fields=['date']),
        ]
