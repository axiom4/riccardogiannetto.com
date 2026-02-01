"""" URL routing for Gallery API endpoints. """
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from gallery import views

router = DefaultRouter(trailing_slash=False)
router.register(r'galleries', views.gallery_view.GalleryViewSet)
router.register(
    r'images/locations', views.image_location_view.ImageLocationViewSet,
    basename='image-location'
)

router.register(
    r'images', views.image_gallery_view.ImageGalleryViewSet,
    basename='image'
)

urlpatterns = [
    path('', include(router.urls)),
]
