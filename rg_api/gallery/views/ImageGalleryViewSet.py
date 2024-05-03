
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


class ImageGalleryPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12

import PIL.Image

class JPEGRenderer(renderers.BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        width = int(renderer_context['request'].GET.get('width' , 500))

        this_object = ImageGallery.objects.get(pk=renderer_context['kwargs']['pk'])
        img = PIL.Image.open(this_object.image.file.name)
        wpercent = (width/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        resize = img.resize((width,hsize))

        b = io.BytesIO()
        resize.save(b, 'JPEG', quality=100)
        resize.close()
        img.close()
        image_data = b.getvalue()
        b.close()

        return image_data

class ImageGalleryViewSet(viewsets.ModelViewSet):

    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = ImageGalleryPagination
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer, JPEGRenderer]

    ordering_fields = ['title', 'created_at', 'gallery']

    filterset_fields = ['gallery', 'width']
    

    search_fields = [
        '$title'
    ]




