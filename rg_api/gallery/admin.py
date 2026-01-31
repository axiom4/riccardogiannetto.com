"""
Django admin configuration for Gallery and ImageGallery models.

Provides customized admin interfaces with bulk upload functionality,
automatic GPS extraction, and ML-based image classification.
"""

import os
from typing import Tuple, List

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import path

from taggit.models import Tag

from gallery.exif_utils import get_gps_data
from gallery.ml import classify_image
from gallery.models import Gallery, ImageGallery

User = get_user_model()

# Constants
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg',
                            '.png', '.webp',
                            '.tif', '.tiff',
                            '.heic'}


class MultiFileInput(forms.FileInput):
    """Custom FileInput widget for multiple file selection."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Custom FileField for handling multiple file uploads."""

    def to_python(self, data):
        return None


class BulkUploadForm(forms.Form):
    """Form for bulk uploading images to a gallery."""
    images = MultipleFileField(
        label='Images folder',
        help_text='Select a folder from your computer.',
        widget=MultiFileInput(
            attrs={
                'webkitdirectory': True,
                'directory': True,
                'multiple': True,
            },
        ),
        required=False,
    )
    gallery = forms.ModelChoiceField(queryset=Gallery.objects.all())
    author = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
    )


class ImageGalleryForm(forms.ModelForm):
    """ModelForm for ImageGallery with autocomplete tag selection."""
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=AutocompleteSelectMultiple(
            ImageGallery._meta.get_field('tags'),
            admin.site,
        ),
    )

    class Meta:
        """Configuration class for ImageGallery model admin form fields."""
        model = ImageGallery
        fields = '__all__'


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


class ImageGalleryAdmin(admin.ModelAdmin):
    """Admin interface for ImageGallery model with advanced features."""
    form = ImageGalleryForm
    fields = [
        ('title',),
        ('image', 'image_tag'),
        ('gallery', 'author', 'date'),
        ('tags',),
        ('width', 'height'),
        ('created_at', 'updated_at'),
        ('camera_model', 'lens_model'),
        ('iso_speed', 'aperture_f_number', 'shutter_speed', 'focal_length'),
        ('artist', 'copyright'),
        ('latitude', 'longitude', 'altitude', 'location'),
    ]
    list_display = (
        'title', 'gallery', 'image_tag', 'author',
        'width', 'height', 'camera_model', 'lens_model',
        'iso_speed', 'aperture_f_number', 'shutter_speed',
        'tag_list', 'created_at', 'updated_at',
    )
    list_filter = ('gallery__title', 'created_at')
    readonly_fields = ['image_tag', 'width',
                       'height', 'created_at', 'updated_at']
    search_fields = ('title', 'gallery__title', 'tags__name')
    save_on_top = True
    list_display_links = ('title',)
    list_per_page = 12
    change_list_template = 'admin/gallery/imagegallery/change_list.html'
    actions = ['auto_tag_images']

    class Media:
        """
        Media configuration for gallery admin interface.

        Includes Leaflet map library CSS and JavaScript resources along with
        custom admin map functionality for the gallery admin panel.
        """
        css = {
            'all': ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',),
        }
        js = (
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'gallery/js/admin_map.js',
        )

    def tag_list(self, obj) -> str:
        """Display up to 3 tags with count of remaining."""
        tags = list(obj.tags.all()[:4])
        if len(tags) > 3:
            remaining = obj.tags.count() - 3
            return f"{', '.join(t.name for t in tags[:3])} (+{remaining})"
        return ", ".join(t.name for t in tags)
    tag_list.short_description = 'Tags'

    @admin.action(description='Auto-tag selected images')
    def auto_tag_images(self, request, queryset):
        """Automatically tag images using ML classifier."""
        count = 0
        updated = 0

        for obj in queryset:
            if not obj.image:
                continue

            try:
                new_tags = classify_image(obj.image.path)
                if new_tags:
                    obj.tags.add(*new_tags)
                    updated += 1
                count += 1
            except (OSError, ValueError) as e:
                self.message_user(
                    request,
                    f"Error processing {obj.title}: {e}",
                    messages.WARNING,
                )

        if updated > 0:
            self.message_user(
                request,
                f"Successfully analyzed {count} images and tagged {updated}.",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No tags added. Check logs or image paths.",
                messages.WARNING,
            )

    def save_related(self, request, form, formsets, change):
        """Extract GPS and auto-tag on save."""
        super().save_related(request, form, formsets, change)
        obj = form.instance

        if not obj.image:
            return

        self._extract_gps_data(obj)
        self._auto_tag_if_empty(obj)

    def _extract_gps_data(self, obj) -> None:
        """Extract GPS data from image EXIF."""
        try:
            lat, lon, alt = get_gps_data(obj.image.path)
            updated = False

            if lat is not None:
                obj.latitude = lat
                updated = True
            if lon is not None:
                obj.longitude = lon
                updated = True
            if alt is not None:
                obj.altitude = alt
                updated = True

            if updated:
                obj.save()
        except (OSError, ValueError) as e:
            print(f"GPS extraction error: {e}")

    def _auto_tag_if_empty(self, obj) -> None:
        """Auto-tag image if no tags exist."""
        if obj.tags.exists():
            return

        try:
            new_tags = classify_image(obj.image.path)
            if new_tags:
                obj.tags.add(*new_tags)
        except (OSError, ValueError) as e:
            print(f"Auto-tag error: {e}")

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Set default gallery and author."""
        form = super().get_form(request, obj, change=change, **kwargs)
        form.base_fields['gallery'].initial = Gallery.objects.first()
        form.base_fields['author'].initial = request.user
        return form

    def get_urls(self):
        """Add custom bulk upload URL."""
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
        """Handle bulk image upload."""
        if request.method == 'POST':
            return self._handle_bulk_upload_post(request)

        form = BulkUploadForm(initial={'author': request.user})
        context = {
            **self.admin_site.each_context(request),
            'opts': self.opts,
            'form': form,
        }
        return render(request, 'admin/gallery/imagegallery/bulk_upload.html', context)

    def _handle_bulk_upload_post(self, request):
        """Process bulk upload POST request."""
        form = BulkUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, 'Invalid form data.')
            return redirect(request.path)

        gallery = form.cleaned_data['gallery']
        author = form.cleaned_data['author'] or request.user
        uploads = request.FILES.getlist('images')

        if not uploads:
            messages.error(request, 'No files selected.')
            return redirect(request.path)

        created, skipped, details = self._process_uploads(
            uploads, gallery, author,
        )

        if request.POST.get('ajax') == 'true':
            return JsonResponse({
                'status': 'success',
                'created': created,
                'skipped': skipped,
                'details': "; ".join(details),
                'message': f'Uploaded {created} images.',
            })

        messages.success(
            request,
            f'Upload completed. Created: {created}. Skipped: {skipped}.',
        )
        return redirect('..')

    def _process_uploads(
        self,
        uploads,
        gallery,
        author,
    ) -> Tuple[int, int, List[str]]:
        """Process each upload and return stats."""
        created = 0
        skipped = 0
        details_list = []

        for upload in uploads:
            base_name = os.path.basename(upload.name)
            _, ext = os.path.splitext(base_name)

            if ext.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                skipped += 1
                continue

            title = os.path.splitext(base_name)[0]
            if ImageGallery.objects.filter(title=title, gallery=gallery).exists():
                skipped += 1
                continue

            image = ImageGallery(
                title=title,
                gallery=gallery,
                author=author,
                image=upload,
            )

            details = self._process_single_upload(image, title)
            image.save()

            details_list.append(" | ".join(details))
            created += 1

        return created, skipped, details_list

    def _process_single_upload(self, image, title) -> List[str]:
        """Process single image upload (GPS, tags)."""
        details = []

        self._extract_upload_gps(image, title, details)
        self._classify_upload_image(image, title, details)

        return details

    def _extract_upload_gps(
        self,
        image,
        title: str,
        details: List[str],
    ) -> None:
        """Extract GPS from uploaded image."""
        try:
            lat, lon, alt = get_gps_data(image.image.path)
            if lat is not None:
                image.latitude = lat
            if lon is not None:
                image.longitude = lon
            if alt is not None:
                image.altitude = alt
            if any([lat, lon, alt]):
                details.append("GPS found")
        except (OSError, ValueError) as e:
            print(f"GPS extraction error for {title}: {e}")

    def _classify_upload_image(
        self,
        image,
        title: str,
        details: List[str],
    ) -> None:
        """Auto-tag uploaded image."""
        try:
            print(f"Auto-tagging image: {title}")
            new_tags = classify_image(image.image.path)
            if new_tags:
                image.tags.add(*new_tags)
                details.append(f"Tags: {len(new_tags)}")
        except (OSError, ValueError) as e:
            print(f"Auto-tag error for {title}: {e}")


admin.site.register(ImageGallery, ImageGalleryAdmin)
admin.site.register(Gallery, GalleryAdmin)
