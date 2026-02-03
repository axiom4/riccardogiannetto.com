"""
Category view set.
"""
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, permissions
from blog.models import Category
from blog.serializers import CategorySerializer


@method_decorator(cache_page(60 * 60 * 2), name='list')
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')
class CategoryViewSet(viewsets.ModelViewSet): # pylint: disable=too-many-ancestors
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Category.objects.annotate(posts_count=Count('post'))
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ['get']
