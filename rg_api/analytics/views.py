from rest_framework import viewsets, permissions
from .models import UserActivity
from .serializers import UserActivitySerializer


class UserActivityViewSet(viewsets.ModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    # Or IsAuthenticated depending on needs
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        user = self.request.user if self.request.user.is_authenticated else None

        serializer.save(
            ip_address=ip,
            user=user,
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
