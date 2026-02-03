"""
Post view set.
"""
import logging
import os
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, renderers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from blog.models import Post
from blog.serializers import PostSerializer, PostPreviewSerializer
from utils.image_optimizer import ImageOptimizer

logger = logging.getLogger(__name__)


class PostImageRenderer(renderers.BaseRenderer):  # pylint: disable=too-few-public-methods
    """
    Renderer for post images in WebP format.
    """
    media_type = 'image/webp'
    format = 'webp'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):  # pylint: disable=unused-argument
        if renderer_context['response'].status_code != 200:
            return b""

        width = self._get_width(renderer_context)
        if width <= 0:
            return b""

        post = self._get_post(renderer_context)
        if not post or not post.image:
            return b""

        return self._get_or_create_preview(post, width)

    def _get_width(self, renderer_context):
        try:
            return int(renderer_context['kwargs'].get('width', 0))
        except (ValueError, TypeError):
            return 0

    def _get_post(self, renderer_context):
        try:
            return Post.objects.get(pk=renderer_context['kwargs']['pk'])
        except Post.DoesNotExist:  # pylint: disable=no-member
            return None

    def _get_or_create_preview(self, post, width):
        # Ensure directory exists
        preview_dir = os.path.join(settings.MEDIA_ROOT, "blog", "preview")
        os.makedirs(preview_dir, exist_ok=True)

        filename = os.path.join(preview_dir, f"{post.pk}_{width}.webp")

        if not os.path.exists(filename):
            try:
                ImageOptimizer.compress_and_resize(
                    post.image.path,
                    output_path=filename,
                    width=width
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error generating preview: %s", e)
                return b""

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return f.read()
        return b""


class PostPagination(PageNumberPagination):
    """
    Pagination for posts.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12


@method_decorator(cache_page(60 * 60 * 2), name='list')
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')
class PostViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    View set for posts.
    """
    queryset = Post.objects.select_related(
        'author').prefetch_related('categories').all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = PostPagination

    ordering_fields = '__all__'

    filterset_fields = ['categories__name']

    search_fields = [
        '$title',
        '$body'
    ]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostPreviewSerializer
        return self.serializer_class

    @method_decorator(cache_page(60 * 60 * 24 * 365))
    @action(
        methods=['get'],
        detail=True,
        url_path='width/(?P<width>[0-9]+)',
        url_name='size',
        renderer_classes=[PostImageRenderer]
    )
    def image(self, request, *args, **kwargs):
        """
        Serve the image in multiple sizes.
        """
        data = self.retrieve(request, *args, **kwargs)
        return data
