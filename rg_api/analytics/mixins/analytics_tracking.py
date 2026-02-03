"""
Mixin for analytics tracking within ViewSets.
"""
import logging
from ..models import UserActivity

logger = logging.getLogger(__name__)


class AnalyticsTrackingMixin:
    """
    Mixin to track user activities automatically in ViewSets.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Intercepts the final response to log the activity.
        """
        # Allow default response processing
        returned_response = super().finalize_response(
            request, response, *args, **kwargs)

        # Only track successful requests (optional, but cleaner)
        if 200 <= response.status_code < 300:
            try:
                self._log_activity(request)
            except (ValueError, TypeError, AttributeError) as e:
                # Logging failure should not break the response
                logger.exception("Error tracking analytics: %s", e)

        return returned_response

    def _log_activity(self, request):
        """Logs the activity details to the database."""
        # Determine action name (e.g., 'list', 'retrieve', 'create')
        action = getattr(self, 'action', request.method)

        # Prepare payload with params (ID, slug, etc)
        payload = {}
        if hasattr(self, 'kwargs') and self.kwargs:
            payload['params'] = self.kwargs

        # Log activity in background (conceptually)
        UserActivity.objects.create(
            user=self._get_user(request),
            session=None,  # Or fetch session if available
            action=f"{self.__class__.__name__}.{action}",
            path=request.path,
            method=request.method,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            payload=payload
        )

    def _get_client_ip(self, request):
        """Extracts the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def _get_user(self, request):
        """Returns the authenticated user or None."""
        return request.user if request.user.is_authenticated else None
