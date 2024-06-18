from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from datetime import datetime

from gallery.models import Gallery
from PIL import Image, ExifTags

class ImageGallery(models.Model):
    title = models.CharField(max_length=250, null=False, blank=False)
    image = models.ImageField(
        null=False
    )
    gallery = models.ForeignKey(Gallery, related_name='images', on_delete=models.CASCADE)

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

    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def image_tag(self):
        return mark_safe('<img src="%s/%s/width/700" width="150" />' % (settings.IMAGE_GENERATOR_BASE_URL, self.id)) if self.image else ''

    image_tag.short_description = 'Image Preview'

    def save(self, *args, **kwargs):
        img = Image.open(self.image)
        width, height = img.size

        exif_data = img._getexif()

        if exif_data:
            self.extract_exif_data(exif_data)

        self.width = width
        self.height = height

        super().save(*args, **kwargs)
        img.close()

    def extract_exif_data(self, exif_data):
        exif_mapping = {
            'Model': 'camera_model',
            'LensModel': 'lens_model',
            'ISOSpeedRatings': 'iso_speed',
            'FNumber': 'aperture_f_number',
            'ShutterSpeedValue': 'shutter_speed',
            'FocalLength': 'focal_length',
            'Artist': 'artist',
            'DateTimeOriginal': 'date',
            'Copyright': 'copyright'
        }

        for key, val in exif_data.items():
            if key in ExifTags.TAGS:
                attribute = exif_mapping.get(ExifTags.TAGS[key])
                if attribute:
                    if attribute == 'date':
                        self.date = datetime.strptime(val, '%Y:%m:%d %H:%M:%S')
                    else:
                        setattr(self, attribute, val)


    class Meta:
        verbose_name_plural = 'images'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['gallery']),
        ]

        
