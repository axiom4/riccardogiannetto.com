from django.urls import include, path
from rest_framework.routers import DefaultRouter
from gallery import views

router = DefaultRouter(trailing_slash=False)
router.register(r'galleries', views.GalleryViewSet)
router.register(r'images', views.ImageGalleryViewSet, basename='image')

urlpatterns = [
    path('', include(router.urls)),
]
