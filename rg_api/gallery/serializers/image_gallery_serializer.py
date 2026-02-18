""" Serializer for ImageGallery model. """
from rest_framework import serializers
from gallery.models import ImageGallery


class ImageGallerySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the ImageGallery model.

    This serializer handles the serialization of ImageGallery instances,
    converting them to JSON format and vice-versa. It includes a hyperlinked
    identity field for the detail view and a string representation of the author.

    Attributes:
        url (HyperlinkedIdentityField): URL to the detail view of the image.
        author (StringRelatedField): String representation of the author.
    """
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='image-detail', lookup_field='slug')

    tags = serializers.StringRelatedField(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        """
        Metadata for the ImageGallerySerializer.

        Attributes:
            fields (str or list): Specifies that all fields from the model should be included.
            model (ImageGallery): The model class associated with this serializer.
        """
        fields = '__all__'
        model = ImageGallery
        lookup_field = 'slug'
