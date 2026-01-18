import os

from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.files import File
from django.shortcuts import redirect, render
from django.urls import path

from gallery.models import Gallery, ImageGallery

User = get_user_model()


class GalleryImageInline(admin.TabularInline):
    model = ImageGallery
    readonly_fields = ['image_tag', 'width',
                       'height', 'created_at', 'updated_at']
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


class MultiFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def to_python(self, data):
        return None  # Bypass validation, handled in view


class BulkUploadForm(forms.Form):
    images = MultipleFileField(
        label='Images folder',
        help_text='Select a folder from your computer.',
        widget=MultiFileInput(
            attrs={'webkitdirectory': True,
                   'directory': True, 'multiple': True},
        ),
        required=False,
    )
    gallery = forms.ModelChoiceField(queryset=Gallery.objects.all())
    author = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False)


class ImageGalleryAdmin(admin.ModelAdmin):
    fields = [
        ('title',),
        ('image', 'image_tag'),
        ('gallery', 'author', 'date'),
        ('tags',),
        ('width', 'height'),
        ('created_at', 'updated_at'),
        ('camera_model', 'lens_model'),
        ('iso_speed', 'aperture_f_number', 'shutter_speed', 'focal_length'),
        ('artist', 'copyright')
    ]
    list_display = ('title', 'gallery', 'image_tag', 'author',
                    'width', 'height', 'tag_list', 'created_at', 'updated_at')
    list_filter = ('gallery__title', 'tags')
    readonly_fields = ['image_tag', 'width',
                       'height', 'created_at', 'updated_at']
    search_fields = ('title', 'gallery__title', 'tags__name')
    save_on_top = True
    list_display_links = ('title',)
    list_per_page = 12
    change_list_template = 'admin/gallery/imagegallery/change_list.html'
    actions = ['auto_tag_images']

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'

    @admin.action(description='Auto-tag selected images')
    def auto_tag_images(self, request, queryset):
        from gallery.ml import classify_image
        count = 0
        updated = 0
        for obj in queryset:
            if obj.image:
                try:
                    # Only tag if no tags exist or if requested to overwrite (here we append)
                    new_tags = classify_image(obj.image.path)
                    if new_tags:
                        obj.tags.add(*new_tags)
                        updated += 1
                    count += 1
                except Exception as e:
                    self.message_user(
                        request, f"Error processing {obj.title}: {e}", messages.WARNING)

        if updated > 0:
            self.message_user(
                request, f"Successfully analyzed {count} images and added tags to {updated}.", messages.SUCCESS)
        else:
            self.message_user(
                request, "No tags added. Check logs or image paths.", messages.WARNING)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.image:
            # If it's a new upload or user didn't manually add tags, try to auto-tag
            if not obj.tags.exists():
                from gallery.ml import classify_image
                try:
                    new_tags = classify_image(obj.image.path)
                    if new_tags:
                        obj.tags.add(*new_tags)
                except Exception as e:
                    # Log error but don't stop save
                    print(f"Auto-tag entry error: {e}")

    def get_form(self, request, obj=None, **kwargs):
        form = super(ImageGalleryAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['gallery'].initial = Gallery.objects.first()
        form.base_fields['author'].initial = request.user
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'bulk-upload/',
                self.admin_site.admin_view(self.bulk_upload_view),
                name='gallery_imagegallery_bulk_upload',
            ),
        ]
        return custom_urls + urls

    def bulk_upload_view(self, request):
        if request.method == 'POST':
            form = BulkUploadForm(request.POST, request.FILES)
            if form.is_valid():
                gallery = form.cleaned_data['gallery']
                author = form.cleaned_data['author'] or request.user

                uploads = request.FILES.getlist('images')
                if not uploads:
                    messages.error(request, 'No files selected.')
                    return redirect(request.path)

                allowed_exts = {'.jpg', '.jpeg', '.png',
                                '.webp', '.tif', '.tiff', '.heic'}
                created = 0
                skipped = 0
                for upload in uploads:
                    base_name = os.path.basename(upload.name)
                    _, ext = os.path.splitext(base_name)
                    if ext.lower() not in allowed_exts:
                        skipped += 1
                        continue

                    title = os.path.splitext(base_name)[0]
                    if ImageGallery.objects.filter(title=title, gallery=gallery).exists():
                        skipped += 1
                        continue
                    image = ImageGallery(
                        title=title, gallery=gallery, author=author)
                    image.image.save(base_name, upload, save=True)
                    created += 1

                messages.success(
                    request,
                    f'Upload completed. Created: {created}. Skipped: {skipped}.',
                )
                return redirect('..')
        else:
            form = BulkUploadForm(initial={'author': request.user})

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'form': form,
        }
        return render(request, 'admin/gallery/imagegallery/bulk_upload.html', context)


admin.site.register(ImageGallery, ImageGalleryAdmin)
admin.site.register(Gallery, GalleryAdmin)
