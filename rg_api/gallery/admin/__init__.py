"""
Gallery Admin Module.
"""
from django.contrib import admin
from ..models import Gallery, ImageGallery
from .gallery import GalleryAdmin
from .image_gallery import ImageGalleryAdmin

admin.site.register(Gallery, GalleryAdmin)
admin.site.register(ImageGallery, ImageGalleryAdmin)
