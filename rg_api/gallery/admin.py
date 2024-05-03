from django.contrib import admin
from gallery.models import Gallery, ImageGallery

class GalleryImageInline(admin.TabularInline):
    model = ImageGallery
    readonly_fields = ['image_tag', 'width', 'height', 'created_at', 'updated_at']
    extra = 0
    list_per_page = 12



class GalleryAdmin(admin.ModelAdmin):
    fields = [
        ('title'),
        ('author', 'tag'),
        'description'
    ]
    list_display = ('title', 'tag', 'author', 'created_at')
    save_on_top = True
    search_fields = ['title',]

    inlines = [GalleryImageInline]

class ImageGalleryAdmin(admin.ModelAdmin):
    fields = [('title',),
              ('image', 'image_tag'), ('gallery', 'author'), ('width', 'height'), ('created_at', 'updated_at')]
    list_display = ('title', 'gallery', 'image_tag', 'author', 'width', 'height','created_at', 'updated_at')
    list_filter = ('gallery__title',)
    readonly_fields = ['image_tag', 'width', 'height', 'created_at', 'updated_at']
    search_fields = ('title', 'gallery__title')
    save_on_top = True
    list_display_links = ('title',)
    list_per_page = 12

    def get_form(self, request, obj=None, **kwargs):
        form = super(ImageGalleryAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['gallery'].initial = Gallery.objects.first()
        form.base_fields['author'].initial = request.user
        return form


admin.site.register(ImageGallery, ImageGalleryAdmin)
admin.site.register(Gallery, GalleryAdmin)