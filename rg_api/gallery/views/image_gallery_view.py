""" ViewSet for Image Gallery API endpoints. """
import os
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, permissions, renderers
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from gallery.models import ImageGallery
from gallery.serializers import ImageGallerySerializer
from utils.pagination import StandardPagination
from utils.viewset_decorators import cached_viewset
from utils.image_optimizer import ImageOptimizer

logger = logging.getLogger(__name__)


class ImageGalleryPagination(StandardPagination):
    """
    Pagination configuration for Image Gallery with smaller page size.

    Overrides StandardPagination to use 4 items per page instead of 5,
    and allows a higher max_page_size of 100.
    """
    page_size = 4
    max_page_size = 100


@cached_viewset(list_timeout=60 * 60 * 24, retrieve_timeout=60 * 60 * 24)
class ImageGalleryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing image galleries.

    This viewset provides `list` and `retrieve` actions for ImageGallery objects.
    It supports filtering by gallery, searching by title, and ordering by various fields.
    It also includes a custom action to retrieve images in specific widths.

    Attributes:
        queryset (QuerySet): The base queryset for the viewset, optimizing database access
            by using `select_related` for author and gallery, and `prefetch_related` for tags.
        serializer_class (Serializer): The serializer class used for validating and
            deserializing input, and for serializing output.
        permission_classes (list): The list of permission classes that determine access rights.
            Defaults to allowing authenticated users to edit, and read-only access for others.
        filter_backends (list): The backends used for filtering,
            searching, and ordering the queryset.
        http_method_names (list): The allowed HTTP methods (currently restricted to 'get').
        pagination_class (Pagination): The pagination class used to paginate the results.
        renderer_classes (list): The renderers used to render the response.
        ordering_fields (list): The fields that can be used for ordering the results.
        filterset_fields (list): The fields that can be used for precise filtering.
        search_fields (list): The fields that can be searched using the search filter.
    """
    queryset = ImageGallery.objects.select_related(
        'author', 'gallery').prefetch_related('tags').all()

    serializer_class = ImageGallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = ImageGalleryPagination
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer]

    ordering_fields = ['title', 'created_at', 'gallery', 'date', 'id']

    filterset_fields = ['gallery']

    search_fields = [
        '$title'
    ]

    @method_decorator(cache_page(60 * 60 * 24 * 365))
    @action(
        methods=['get'],
        detail=True,
        url_path='width/(?P<width>[0-9]+)',
        url_name='size',
    )
    def jpeg(self, request, *args, **kwargs):
        """
        Retrieve and return image gallery data in WebP format.
        """
        try:
            image_gallery = self.get_object()
            width = int(kwargs.get('width', 0))
        except (ValueError, TypeError, ObjectDoesNotExist) as exc:
            raise Http404 from exc

        if width <= 0:
            raise Http404

        # Ensure directory exists
        preview_dir = os.path.join(settings.MEDIA_ROOT, "preview")
        os.makedirs(preview_dir, exist_ok=True)

        filename = os.path.join(
            preview_dir, f"{image_gallery.pk}_{width}.webp")

        if not os.path.exists(filename):
            try:
                ImageOptimizer.compress_and_resize(
                    image_gallery.image.path,
                    output_path=filename,
                    width=width
                )
            except Exception as e:
                logger.error("Error creating preview: %s", e)
                raise Http404 from e

        if os.path.exists(filename):
            return FileResponse(open(filename, "rb"), content_type="image/webp")

        raise Http404
