"""Serializer for ImageGallery location data."""
from rest_framework import serializers
from django.conf import settings
from drf_spectacular.utils import extend_schema_field

from gallery.models import ImageGallery


class ImageLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for ImageGallery location data.
    """
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ImageGallery
        fields = ['id', 'title', 'latitude', 'longitude', 'thumbnail']

    @extend_schema_field(serializers.CharField)
    def get_thumbnail(self, obj):
        """
        Constructs and returns the thumbnail URL for the given image object.

        Args:
          obj: The image object containing the primary key (pk) used in the URL.

        Returns:
          str: A URL string pointing to the generated thumbnail image with a fixed width of 300.
        """
        # Construct the thumbnail URL manually or use the image_tag logic equivalent
        # Assuming we can use the same generic view pattern
        return f"{settings.IMAGE_GENERATOR_BASE_URL}/{obj.pk}/width/300"
