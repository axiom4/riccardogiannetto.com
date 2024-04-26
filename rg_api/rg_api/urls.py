"""
URL configuration for rg_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from rest_framework import permissions

from django.conf import settings
from .permissions import AccessListPermission
from django.conf.urls.static import static

from blog import urls as blog_urls

schema_url_patterns = [
    path('blog/', include(blog_urls.urlpatterns)),
]


urlpatterns = [
    path("blog/", include(blog_urls.urlpatterns)),
    path('admin/', admin.site.urls),
    path('', get_schema_view(
         title="Riccardo Giannetto Gallery API",
         description="API app riccardogiannetto.com",
         version="1.0.0",
         patterns=schema_url_patterns,
         public=True,
         permission_classes=[AccessListPermission |
                             permissions.IsAuthenticated]
         ), name='openapi-schema'),
    path(r'mdeditor/', include('mdeditor.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
