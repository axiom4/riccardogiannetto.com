"""
Gallery Admin Module.
"""
from django.contrib import admin
from ..models import Gallery, ImageGallery, Tag
from .gallery import GalleryAdmin
from .image_gallery import ImageGalleryAdmin


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Gallery, GalleryAdmin)
admin.site.register(ImageGallery, ImageGalleryAdmin)
