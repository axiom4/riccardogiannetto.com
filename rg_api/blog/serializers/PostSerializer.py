from rest_framework import serializers
from blog.models import Post
from blog.serializers import UserSerializer


class PostSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='post-detail')

    author = UserSerializer(read_only=True)
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        fields = (
            "id",
            "url",
            "author",
            "title",
            "body",
            "created_at",
            'image',
            'categories',
            'summary'
        )

        model = Post
