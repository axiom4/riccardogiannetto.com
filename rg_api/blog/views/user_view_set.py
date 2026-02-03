"""
User view set.
"""
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from blog.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet): # pylint: disable=too-many-ancestors
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
