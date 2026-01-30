""" Serializer for Gallery model. """
from rest_framework import serializers
from gallery.models import Gallery


class GallerySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Gallery model.

    This serializer provides a complete representation of a Gallery instance,
    including its ID, URL, author string representation, and hyperlinks to
    associated images. It handles serialization for the API's gallery endpoints.
    """
    id = serializers.IntegerField()
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='gallery-detail')

    author = serializers.StringRelatedField(read_only=True)

    images = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='image-detail'
    )

    class Meta:
        """
        Meta configuration for the GallerySerializer.

        Specifies the model to be serialized and assumes all fields from the
        Gallery model should be included in the serialized output.
        """
        fields = '__all__'
        model = Gallery
