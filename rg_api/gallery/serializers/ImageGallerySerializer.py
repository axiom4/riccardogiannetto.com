from rest_framework import serializers
from gallery.models import ImageGallery


class ImageGallerySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='image-detail')

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = ImageGallery
