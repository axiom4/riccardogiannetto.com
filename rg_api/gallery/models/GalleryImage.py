from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe

from gallery.models import Gallery
import PIL.Image

class GalleryImage(models.Model):
    title = models.CharField(max_length=250, null=False)
    image = models.ImageField(
        null=False
    )
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)

    width = models.IntegerField()
    height = models.IntegerField()


    author = models.ForeignKey(
        User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def image_tag(self):
        return mark_safe('<img src="/%s/%s" width="150" />' % (settings.MEDIA_ROOT, self.image)) if self.image else ''

    image_tag.short_description = 'Image Preview'

    def save(self, *args, **kwargs):
        img = PIL.Image.open(self.image)
        width, height = img.size
        self.width = width
        self.height = height
        # target_width = 600
        # h_coefficient = width/600
        # target_height = height/h_coefficient
        # img = img.resize((int(target_width), int(target_height)), PIL.Image.ANTIALIAS)
        # img.save(self.image.path, quality=100)
        super().save(*args, **kwargs)

        
