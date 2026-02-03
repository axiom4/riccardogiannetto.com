"""
User serializer.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the User model.
    """

    class Meta:
        """
        Meta options.
        """
        model = get_user_model()
        fields = ['username']
