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
