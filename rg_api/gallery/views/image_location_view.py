""" ViewSet for ImageGallery location data. """
from rest_framework import viewsets
from rest_framework import permissions
from gallery.models import ImageGallery

from gallery.serializers import ImageLocationSerializer

_MAX_LOCATIONS = 500


class ImageLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving image locations.
    """
    queryset = ImageGallery.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).exclude(latitude=0, longitude=0).only(
        'id', 'title', 'latitude', 'longitude', 'slug'
    )[:_MAX_LOCATIONS]
    serializer_class = ImageLocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # Map needs all pins; queryset hard-capped at _MAX_LOCATIONS
