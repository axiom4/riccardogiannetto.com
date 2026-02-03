from django.contrib import admin
from ..models import ImageUpload


class ImageInline(admin.TabularInline):
    model = ImageUpload
    readonly_fields = ['image_tag']
    extra = 0


class ImageAdmin(admin.ModelAdmin):
    fields = [('title', 'short_name'),
              ('image', 'image_tag'), ('post', 'author')]
    list_display = ('title', 'short_name', 'post', 'image_tag')
    list_filter = ('post__title',)
    search_fields = ('title', 'short_name', 'post__title')
    save_on_top = False
    list_display_links = ('title',)
    readonly_fields = ['image_tag']

    def get_form(self, request, obj=None, **kwargs):
        form = super(ImageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].initial = request.user
        return form
