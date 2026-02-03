"""
Post preview serializer.
"""
from rest_framework import serializers
from blog.models import Post
from .user_serializer import UserSerializer


class PostPreviewSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Post model (preview).
    """
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='post-detail')

    author = UserSerializer(read_only=True)
    categories = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name')

    class Meta:
        """
        Meta options.
        """
        fields = (
            "id",
            "url",
            "author",
            "title",
            "created_at",
            'image',
            'categories',
            'summary'
        )

        model = Post
