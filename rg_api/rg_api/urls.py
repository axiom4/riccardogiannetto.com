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

from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from blog import urls as blog_urls

schema_url_patterns = [
    path('blog/', include(blog_urls.urlpatterns)),
    path('portfolio/', include('gallery.urls')),

]


urlpatterns = [
    path("blog/", include(blog_urls.urlpatterns)),
    path('portfolio/', include('gallery.urls')),
    path('admin/', admin.site.urls),
    path('openapi', SpectacularAPIView().as_view(), name='schema'),
    path('',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
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
