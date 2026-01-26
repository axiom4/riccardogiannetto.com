
# Create your views here.
import os
from django.conf import settings
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from gallery.models import ImageGallery
from gallery.serializers import ImageGallerySerializer
from rest_framework import renderers

from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from utils.image_optimizer import ImageOptimizer


class ImageGalleryPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100


class ImageRenderer(renderers.BaseRenderer):
    media_type = 'image/webp'
    format = 'webp'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        if renderer_context['response'].status_code != 200:
            return b""

        width = int(renderer_context['kwargs']['width'])

        try:
            this_object = ImageGallery.objects.get(
                pk=renderer_context['kwargs']['pk'])
        except ImageGallery.DoesNotExist:
            return b""

        filename = f"{settings.MEDIA_ROOT}/preview/{this_object.pk}_{width}.webp"

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


class ImageGalleryViewSet(viewsets.ModelViewSet):

    queryset = ImageGallery.objects.all()
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
    @action(methods=['get'], detail=True, url_path='width/(?P<width>[0-9]+)', url_name='size', renderer_classes=[ImageRenderer])
    def jpeg(self, request, *args, **kwargs):
        data = self.retrieve(request, *args, **kwargs)
        return data
