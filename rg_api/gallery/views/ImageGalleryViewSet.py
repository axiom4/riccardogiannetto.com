
# Create your views here.
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from gallery.models import ImageGallery
from gallery.serializers import ImageGallerySerializer


class ImageGalleryPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12


class ImageGalleryViewSet(viewsets.ModelViewSet):
    view_name = 'image-detail'

    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    http_method_names = ['get']
    pagination_class = ImageGalleryPagination

    ordering_fields = ['title', 'created_at', 'gallery']

    filterset_fields = ['gallery']

    search_fields = [
        '$title'
    ]

    # def get_serializer_class(self):
    #     if self.action == 'list':
    #         return PostPreviewSerializer
    #     else:
    #         return self.serializer_class
