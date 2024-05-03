from rest_framework import serializers
from gallery.models import Gallery, ImageGallery
from blog.serializers import UserSerializer


class GallerySerializer(serializers.HyperlinkedModelSerializer):
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
        fields = '__all__'
        model = Gallery
