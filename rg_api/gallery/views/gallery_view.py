""""" Views for Gallery model. """
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
    """
    Custom pagination class for Gallery views.

    Inherits from PageNumberPagination to provide page-based pagination.

    Attributes:
        page_size (int): The default number of items to include on a page (5).
        page_size_query_param (str): The name of the query parameter to allow clients
                                     to set the page size ('page_size').
        max_page_size (int): The maximum number of items allowed per page (12).
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12


@method_decorator(cache_page(60 * 60 * 2), name='list')
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')
class GalleryViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    A ViewSet for viewing Gallery instances.

    This ViewSet provides `list` and `retrieve` actions for Gallery objects,
    supporting filtering, searching, and ordering.

    Attributes:
        queryset (QuerySet): The base queryset for retrieving galleries,
            optimized with `select_related` and `prefetch_related`.
        serializer_class (Serializer): The serializer class used for
            validating and deserializing input, and for serializing output.
        permission_classes (list): The list of permission classes that
            determine access rights (Authenticated or ReadOnly).
        filter_backends (list): The backends used for filtering the queryset.
        http_method_names (list): The allowed HTTP method names ('get' only).
        pagination_class (Pagination): The pagination class used for
            paginating results.
        ordering_fields (str or list): The fields allowed for ordering.
        filterset_fields (list): The fields used for exact match filtering.
        search_fields (list): The fields used for full-text search.
    """
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
