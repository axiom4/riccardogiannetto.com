from django.shortcuts import render

from rest_framework import viewsets
from blog.models import Page
from rest_framework import permissions
from blog.serializers import PageSerializer


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "tag"
    http_method_names = ['get']
