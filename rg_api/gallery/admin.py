from django.contrib import admin
from gallery.models import Gallery, GalleryImage

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    readonly_fields = ['width', 'height', 'created_at', 'updated_at']
    extra = 0


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

class GalleryImageAdmin(admin.ModelAdmin):
    fields = [('title',),
              ('image', 'image_tag'), ('gallery', 'author')]
    list_display = ('title', 'gallery', 'image_tag', 'author', 'width', 'height','created_at', 'updated_at')
    list_filter = ('gallery__title',)
    readonly_fields = ['width', 'height', 'created_at', 'updated_at']
    search_fields = ('title', 'gallery__title')
    save_on_top = True
    list_display_links = ('title',)
    readonly_fields = ['image_tag', 'created_at', 'updated_at']

    def get_form(self, request, obj=None, **kwargs):
        form = super(GalleryImageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['gallery'].initial = Gallery.objects.first()
        form.base_fields['author'].initial = request.user
        return form


admin.site.register(GalleryImage, GalleryImageAdmin)
admin.site.register(Gallery, GalleryAdmin)