""" ViewSet for Image Gallery API endpoints. """
import os
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import renderers
from rest_framework.response import Response

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend

from gallery.models import ImageGallery
from gallery.serializers import ImageGallerySerializer, ImageLocationSerializer


from utils.image_optimizer import ImageOptimizer

logger = logging.getLogger(__name__)


class ImageGalleryPagination(PageNumberPagination):
    """
    Custom pagination class for Image Gallery.

    This pagination configuration sets a default page size of 4 items, allows the client
    to override the page size via the 'page_size' query parameter, and caps the maximum
    page size at 100.
    """
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100


class ImageRenderer(renderers.BaseRenderer):
    """
    Custom DRF renderer for serving resized and optimized WebP images.

    This renderer handles the dynamic generation, caching, and serving of image
    previews based on the requested width. It extends BaseRenderer to serve
    binary image data directly rather than JSON or HTML.
    """
    media_type = 'image/webp'
    format = 'webp'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context['response'].status_code != 200:
            return b""

        try:
            width = int(renderer_context['kwargs'].get('width', 0))
            if width <= 0:
                return b""
        except (ValueError, TypeError, KeyError):
            return b""

        try:
            this_object = ImageGallery.objects.get(
                pk=renderer_context['kwargs']['pk'])
        except ObjectDoesNotExist:
            return b""

        # Ensure directory exists
        preview_dir = os.path.join(settings.MEDIA_ROOT, "preview")
        os.makedirs(preview_dir, exist_ok=True)

        filename = os.path.join(preview_dir, f"{this_object.pk}_{width}.webp")

        if not os.path.exists(filename):
            try:
                ImageOptimizer.compress_and_resize(
                    this_object.image.path,
                    output_path=filename,
                    width=width
                )
            except (OSError, ValueError) as e:
                logger.error("Error generating preview: %s", e)
                return b""

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return f.read()
        return b""


class ImageGalleryViewSet(viewsets.ModelViewSet):
    """
    Docstring for ImageGalleryViewSet

    :var Args: Description
    :var request: Description
    :vartype request: The
    :var Returns: Description
    :var Response: Description
    :vartype Response: The
    A viewset for viewing image galleries.

    This viewset provides `list` and `retrieve` actions for ImageGallery objects.
    It supports filtering by gallery, searching by title, and ordering by various fields.
    It also includes a custom action to retrieve images in specific widths.

    Attributes:
        queryset(QuerySet): The base queryset for the viewset, optimizing database access
            by using `select_related` for author and gallery, and `prefetch_related` for tags.
        serializer_class(Serializer): The serializer class used for validating and
            deserializing input, and for serializing output.
        permission_classes(list): The list of permission classes that determine access rights.
            Defaults to allowing authenticated users to edit, and read-only access for others.
        filter_backends(list): The backends used for filtering, 
            searching, and ordering the queryset.
        http_method_names(list): The allowed HTTP methods(currently restricted to 'get').
        pagination_class(Pagination): The pagination class used to paginate the results.
        renderer_classes(list): The renderers used to render the response.
        ordering_fields(list): The fields that can be used for ordering the results.
        filterset_fields(list): The fields that can be used for precise filtering.
        search_fields(list): The fields that can be searched using the search filter.
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

    @action(detail=False, methods=['get'])
    def locations(self, request):
        """
        Returns a list of images with valid GPS coordinates.
        """
        images = ImageGallery.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).exclude(latitude=0, longitude=0)

        serializer = ImageLocationSerializer(images, many=True)
        return Response(serializer.data)

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
