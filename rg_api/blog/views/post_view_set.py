"""
Post view set.
"""
import logging
import os
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

from blog.models import Post
from blog.serializers import PostSerializer, PostPreviewSerializer
from utils.image_optimizer import ImageOptimizer
from utils.pagination import StandardPagination
from utils.renderers import WebPImageRenderer
from utils.viewset_decorators import cached_viewset

logger = logging.getLogger(__name__)


class PostImageRenderer(WebPImageRenderer):
    """
    Renderer for post images in WebP format.
    """

    def _render_image(self, renderer_context, width, data=None):
        """Render post image as WebP."""
        post = data if isinstance(data, Post) else self._get_post(renderer_context)
        if not post or not post.image:
            return b""

        return self._get_or_create_preview(post, width)

    def _get_post(self, renderer_context):
        """Retrieve post from renderer context."""
        try:
            # Fallback if object not passed in data
            return Post.objects.get(pk=renderer_context['kwargs']['pk'])
        except Post.DoesNotExist:
            return None

    def _get_or_create_preview(self, post, width):
        """Get or create image preview at specified width."""
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
            except (OSError, ValueError, RuntimeError) as e:
                logger.error("Error generating preview: %s", e)
                return b""

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return f.read()
        return b""


@cached_viewset()
class PostViewSet(viewsets.ModelViewSet):
    """
    View set for posts.
    """
    queryset = Post.objects.select_related(
        'author').prefetch_related('categories').all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = StandardPagination

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
        return self.get_object()
