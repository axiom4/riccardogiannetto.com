from rest_framework import viewsets
from blog.models import Post
from rest_framework import permissions
from blog.serializers import PostSerializer, PostPreviewSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

import os
from django.conf import settings
from rest_framework import renderers
from rest_framework.decorators import action
from utils.image_optimizer import ImageOptimizer


class PostImageRenderer(renderers.BaseRenderer):
    media_type = 'image/webp'
    format = 'webp'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        if renderer_context['response'].status_code != 200:
            return b""

        try:
            width = int(renderer_context['kwargs'].get('width', 0))
            if width <= 0:
                return b""
        except (ValueError, TypeError):
            return b""

        try:
            this_object = Post.objects.get(
                pk=renderer_context['kwargs']['pk'])
        except Post.DoesNotExist:
            return b""

        if not this_object.image:
            return b""

        # Ensure directory exists
        preview_dir = f"{settings.MEDIA_ROOT}/blog/preview"
        os.makedirs(preview_dir, exist_ok=True)

        filename = f"{preview_dir}/{this_object.pk}_{width}.webp"

        if not os.path.exists(filename):
            try:
                ImageOptimizer.compress_and_resize(
                    this_object.image.path,
                    output_path=filename,
                    width=width
                )
            except Exception as e:
                print(f"Error generating preview: {e}")
                return b""

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return f.read()
        return b""


class PostPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12


@method_decorator(cache_page(60 * 60 * 2), name='list')
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
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
        else:
            return self.serializer_class

    @method_decorator(cache_page(60 * 60 * 24 * 365))
    @action(methods=['get'], detail=True, url_path='width/(?P<width>[0-9]+)', url_name='size', renderer_classes=[PostImageRenderer])
    def image(self, request, *args, **kwargs):
        data = self.retrieve(request, *args, **kwargs)
        return data
