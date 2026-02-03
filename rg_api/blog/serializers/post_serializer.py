"""
Post serializer.
"""
from rest_framework import serializers
from blog.models import Post
from .user_serializer import UserSerializer
from .fields import POST_BASE_FIELDS


class PostSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Post model (full).
    """
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='post-detail')

    author = UserSerializer(read_only=True)
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        """
        Meta options.
        """
        fields = POST_BASE_FIELDS + ("body",)
        model = Post
