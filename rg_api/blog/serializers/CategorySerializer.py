from rest_framework import serializers
from blog.models import Category


class CategorySerializer(serializers.ModelSerializer):
    posts = serializers.IntegerField(source='posts_count', read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
