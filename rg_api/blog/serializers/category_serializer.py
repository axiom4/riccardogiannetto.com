"""
Category serializer.
"""
from rest_framework import serializers
from blog.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    posts = serializers.IntegerField(source='posts_count', read_only=True)

    class Meta:
        """
        Meta options.
        """
        model = Category
        fields = '__all__'
