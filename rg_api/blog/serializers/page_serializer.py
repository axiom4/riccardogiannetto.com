"""
Page serializer.
"""
from rest_framework import serializers
from blog.models import Page
from .user_serializer import UserSerializer


class PageSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Page model.
    """
    url = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='page-detail', lookup_field='tag')

    author = UserSerializer(read_only=True)

    class Meta:
        """
        Meta options.
        """
        fields = (
            "id",
            "url",
            "tag",
            "author",
            "title",
            "body",
            "created_at",
        )

        model = Page
