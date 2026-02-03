"""
User serializer.
"""
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the User model.
    """

    class Meta:
        """
        Meta options.
        """
        model = User
        fields = ['username']
