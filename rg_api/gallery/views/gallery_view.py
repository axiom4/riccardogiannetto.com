""""" Views for Gallery model. """
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from utils.pagination import StandardPagination
from utils.viewset_decorators import cached_viewset
from gallery.models import Gallery
from gallery.serializers import GallerySerializer


@cached_viewset()
class GalleryViewSet(viewsets.ModelViewSet):
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
    pagination_class = StandardPagination

    ordering_fields = '__all__'

    filterset_fields = ['title', 'slug']

    search_fields = [
        '$title',
        '$description'
    ]
