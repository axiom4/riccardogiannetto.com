""" ViewSet for Image Gallery API endpoints. """
import os
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, permissions, renderers
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from gallery.models import ImageGallery
from gallery.serializers import ImageGallerySerializer
from utils.renderers import WebPImageRenderer
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


class ImageRenderer(WebPImageRenderer):
    """
    Custom DRF renderer for serving resized and optimized WebP images.

    This renderer handles the dynamic generation, caching, and serving of image
    previews based on the requested width.
    """

    def _render_image(self, renderer_context, width):
        """
        Renders the resized image based on the provided width.

        Args:
            renderer_context: Context containing request details and kwargs.
            width: The width for the rendered image.
        """
        try:
            this_object = ImageGallery.objects.get(
                pk=renderer_context['kwargs']['pk'])

            # Ensure directory exists
            preview_dir = os.path.join(settings.MEDIA_ROOT, "preview")
            os.makedirs(preview_dir, exist_ok=True)

            filename = os.path.join(
                preview_dir, f"{this_object.pk}_{width}.webp")

            if not os.path.exists(filename):
                ImageOptimizer.compress_and_resize(
                    this_object.image.path,
                    output_path=filename,
                    width=width
                )

            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    return f.read()

        except (KeyError, ObjectDoesNotExist):
            pass
        except OSError as e:
            logger.error("Error generating preview: %s", e)

        return b""


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
        renderer_classes=[ImageRenderer]
    )
    def jpeg(self, request, *args, **kwargs):
        """
        Retrieve and return image gallery data in JPEG format.

        Args:
            request: The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The serialized image gallery data.
        """
        data = self.retrieve(request, *args, **kwargs)
        return data
