
# Create your views here.
import io
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from gallery.models import ImageGallery
from gallery.serializers import ImageGallerySerializer
from rest_framework import renderers

from rest_framework.decorators import action
import PIL.Image
import cv2
from rest_framework.response import Response
from rest_framework import status

class ImageGalleryPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12

import PIL.Image
import cv2

class ImageRenderer(renderers.BaseRenderer):
    media_type = 'image/webp'
    format = 'webp'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        width = int(renderer_context['kwargs']['width'])

        this_object = ImageGallery.objects.get(pk=renderer_context['kwargs']['pk'])
        img = cv2.imread(this_object.image.file.name)
        wpercent = (width/float(img.shape[1]))
        hsize = int((float(img.shape[0])*float(wpercent)))
        resize = cv2.resize(img, (width, hsize))

        _, im_buf_arr = cv2.imencode(".webp", resize, [int(cv2.IMWRITE_WEBP_QUALITY), 90])
        byte_im = im_buf_arr.tobytes()

        return byte_im


class ImageGalleryViewSet(viewsets.ModelViewSet):

    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = ImageGalleryPagination
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer]

    ordering_fields = ['title', 'created_at', 'gallery']

    filterset_fields = ['gallery']
    

    search_fields = [
        '$title'
    ]

    @action(methods=['get'], detail=True, url_path='width/(?P<width>[0-9]+)', url_name='size', renderer_classes=[ImageRenderer])
    def jpeg(self, request, *args, **kwargs):
        data = self.retrieve(request, *args, **kwargs)
        return data




