"""
Page view set.
"""
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, permissions
from blog.models import Page
from blog.serializers import PageSerializer


@method_decorator(cache_page(60 * 60 * 2), name='list')
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')
class PageViewSet(viewsets.ModelViewSet):
    """
    Page view set.
    """
    queryset = Page.objects.select_related('author').all()
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "tag"
    http_method_names = ['get']
