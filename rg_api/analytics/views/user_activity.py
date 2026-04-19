"""
User activity views.
"""
from rest_framework import viewsets, permissions, mixins, throttling
from ..models import UserActivity
from ..serializers import UserActivitySerializer


class UserActivityCreateThrottle(throttling.AnonRateThrottle):
    rate = '30/minute'


class UserActivityViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """
    Write-only ViewSet for creating user activity records.
    List and retrieve are intentionally excluded to prevent exposure of
    ip_address, user_agent, and path data to unauthenticated users.
    """
    queryset = UserActivity.objects.select_related('user', 'session').all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [UserActivityCreateThrottle]

    def perform_create(self, serializer):
        """Custom create to capture IP and user."""
        ip_address = self.request.META.get('HTTP_X_REAL_IP') or \
            self.request.META.get('REMOTE_ADDR')

        user = self.request.user if self.request.user.is_authenticated else None

        serializer.save(
            ip_address=ip_address,
            user=user,
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
