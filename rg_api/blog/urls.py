from django.urls import include, path
from rest_framework.routers import DefaultRouter
from blog import views

router = DefaultRouter(trailing_slash=False)
router.register(r'pages', views.PageViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
