"""
Gallery admin forms.
"""
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib.auth import get_user_model
from taggit.models import Tag
from ..models import Gallery, ImageGallery

User = get_user_model()


class MultiFileInput(forms.FileInput):
    """Custom FileInput widget for multiple file selection."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Custom FileField for handling multiple file uploads."""

    def to_python(self, data):
        """Convert data to Python object (not used for multiple file upload)."""
        return None


class BulkUploadForm(forms.Form):
    """Form for bulk uploading images to a gallery."""
    images = MultipleFileField(
        label='Select Images',
        widget=MultiFileInput(attrs={'multiple': True}),
    )
    gallery = forms.ModelChoiceField(
        queryset=Gallery.objects.all(),
        required=False,
        empty_label="-- Select existing gallery --",
    )
    new_gallery_name = forms.CharField(
        label='Or create new gallery',
        required=False,
    )
    auto_tag = forms.BooleanField(
        label='Auto-generate tags with ML',
        initial=True,
        required=False,
    )


class ImageGalleryForm(forms.ModelForm):
    """ModelForm for ImageGallery with autocomplete tag selection."""
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=AutocompleteSelectMultiple(
            ImageGallery._meta.get_field(
                'tags'),  # pylint: disable=protected-access
            admin.site,
        ),
    )

    class Meta:
        """Configuration class for ImageGallery model admin form fields."""
        model = ImageGallery
        fields = '__all__'
