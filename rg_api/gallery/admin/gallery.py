"""
Gallery Admin Configuration.
"""
from django.contrib import admin
from ..models import ImageGallery


class GalleryImageInline(admin.TabularInline):
    """Inline admin for ImageGallery within Gallery."""
    model = ImageGallery
    readonly_fields = ['image_tag', 'width',
                       'height', 'created_at', 'updated_at']
    extra = 0
    list_per_page = 12


class GalleryAdmin(admin.ModelAdmin):
    """Admin interface for Gallery model."""
    fields = [
        ('title',),
        ('author', 'tag'),
        'description',
    ]
    list_display = ('title', 'tag', 'author', 'created_at')
    save_on_top = True
    search_fields = ['title']
    inlines = [GalleryImageInline]
