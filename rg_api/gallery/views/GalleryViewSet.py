
# Create your views here.
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from gallery.models import Gallery
from gallery.serializers import GallerySerializer


class GalleryPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12


@method_decorator(cache_page(60 * 60 * 2), name='list')
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')
class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.select_related(
        'author').prefetch_related('images').all()
    serializer_class = GallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = GalleryPagination

    ordering_fields = '__all__'

    filterset_fields = ['title']

    search_fields = [
        '$title',
        '$description'
    ]
