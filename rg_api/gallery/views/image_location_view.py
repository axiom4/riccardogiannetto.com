""" ViewSet for ImageGallery location data. """
from rest_framework import viewsets
from rest_framework import permissions
from gallery.models import ImageGallery

from gallery.serializers import ImageLocationSerializer


class ImageLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving image locations.
    """
    queryset = ImageGallery.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).exclude(latitude=0, longitude=0).only('id', 'title', 'latitude', 'longitude', 'slug')
    serializer_class = ImageLocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # Return all locations without pagination
