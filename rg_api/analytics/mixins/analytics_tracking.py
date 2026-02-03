from ..models import UserActivity
import logging

logger = logging.getLogger(__name__)


class AnalyticsTrackingMixin:
    """
    Mixin to track user activities automatically in ViewSets.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        # Allow default response processing
        returned_response = super().finalize_response(
            request, response, *args, **kwargs)

        # Only track successful requests (optional, but cleaner)
        if 200 <= response.status_code < 300:
            try:
                # Determine action name (e.g., 'list', 'retrieve', 'create')
                action = getattr(self, 'action', request.method)

                # Prepare payload with params (ID, slug, etc)
                payload = {}
                if hasattr(self, 'kwargs') and self.kwargs:
                    payload['params'] = self.kwargs

                # Extract IP
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')

                # Extract User
                user = request.user if request.user.is_authenticated else None

                # Log activity in background (conceptually)
                UserActivity.objects.create(
                    user=user,
                    action=f"{self.__class__.__name__}.{action}",
                    path=request.path,
                    method=request.method,
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    payload=payload
                )
            except Exception as e:
                # Logging failure should not break the response
                logger.error(f"Error tracking analytics: {e}")

        return returned_response
