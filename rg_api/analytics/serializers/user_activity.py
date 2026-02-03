"""
Serializers for User Activity.
"""
from rest_framework import serializers
from ..models import UserActivity


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for UserActivity model.
    """
    class Meta:
        """Meta configuration for UserActivitySerializer."""
        model = UserActivity
        fields = [
            'id', 'user', 'action', 'path',
            'method', 'ip_address', 'user_agent',
            'payload', 'timestamp'
        ]
        read_only_fields = ['id', 'user', 'ip_address', 'timestamp']

    def create(self, validated_data):
        """Create UserActivity instance with user from request context."""
        # User and IP are handled by the view/context usually
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user

        # IP extraction logic could be here or in view
        return super().create(validated_data)
