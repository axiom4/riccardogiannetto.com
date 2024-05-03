from rest_framework import serializers
from gallery.models import ImageGallery
from blog.serializers import UserSerializer


class ImageGallerySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='gallery-detail')

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = ImageGallery
