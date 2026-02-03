"""
Image admin.
"""
from django.contrib import admin
from ..models import ImageUpload


class ImageInline(admin.TabularInline):
    """
    Image inline admin.
    """
    model = ImageUpload
    readonly_fields = ['image_tag']
    extra = 0


class ImageAdmin(admin.ModelAdmin):
    """
    Image admin.
    """
    fields = [('title', 'short_name'),
              ('image', 'image_tag'), ('post', 'author')]
    list_display = ('title', 'short_name', 'post', 'image_tag')
    list_filter = ('post__title',)
    search_fields = ('title', 'short_name', 'post__title')
    save_on_top = False
    list_display_links = ('title',)
    readonly_fields = ['image_tag']

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Customize form to set default author to current user."""
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['author'].initial = request.user
        return form
