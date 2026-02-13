"""
User activity views.
"""
from rest_framework import viewsets, permissions, mixins
from ..models import UserActivity
from ..serializers import UserActivitySerializer


class UserActivityViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet for viewing and creating user activities.
    """
    queryset = UserActivity.objects.select_related('user', 'session').all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        """Custom create to capture IP and user."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the list and strip whitespace
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')

        user = self.request.user if self.request.user.is_authenticated else None

        serializer.save(
            ip_address=ip_address,
            user=user,
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
