"""" URL routing for Gallery API endpoints. """
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from gallery.views import (
    GalleryViewSet,
    ImageGalleryViewSet,
    ImageLocationViewSet
)

router = DefaultRouter(trailing_slash=False)
router.register(r'galleries', GalleryViewSet)
router.register(
    r'images/locations', ImageLocationViewSet,
    basename='image-location'
)

router.register(
    r'images', ImageGalleryViewSet,
    basename='image'
)

urlpatterns = [
    path('', include(router.urls)),
]
