from rest_framework import serializers
from blog.models import Category


class CategorySerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_posts(self, obj):
        posts = obj.post_set.all().count()
        return posts
