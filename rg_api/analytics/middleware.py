from .models import UserActivity
import threading
import logging
from django.conf import settings
try:
    import geoip2.database
except ImportError:
    geoip2 = None

logger = logging.getLogger(__name__)


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.reader = None
        if geoip2 and hasattr(settings, 'GEOIP_PATH'):
            try:
                self.reader = geoip2.database.Reader(settings.GEOIP_PATH)
            except Exception as e:
                logger.warning(f"GeoIP database not found or invalid: {e}")

    def __call__(self, request):
        # Process request before view (and before cache check if cache middleware was used globaly,
        # but here cache_page is used on views, so this runs BEFORE cache_page check)

        response = self.get_response(request)

        # We log AFTER the response is generated (successfully).
        # Note: If cache_page intercepts inside the view layer, this middleware
        # still sees the request and the response coming back from the view "wrapper".

        if request.path.startswith('/api/') or request.path.startswith('/blog/') or request.path.startswith('/portfolio/'):
            # Filter out admin, static, etc if needed.
            # Assuming typically API routes are relevant.
            # Adjust filter as needed.
            self.track_activity(request, response)

        return response

    def track_activity(self, request, response):
        if not (200 <= response.status_code < 300):
            return

        # Simple ignoring of assets/admin/etc if not filtered above
        if request.path.startswith('/admin') or request.path.startswith('/static') or request.path.startswith('/media'):
            return

        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            user = request.user if request.user.is_authenticated else None

            # We don't have access to "viewset action" easily here without using process_view
            # and storing it, but path is the most important.

            city = None
            country = None
            lat = None
            lon = None

            if self.reader and ip:
                try:
                    # Handle local IPs
                    if ip in ['127.0.0.1', 'localhost', '::1']:
                        pass
                    else:
                        response = self.reader.city(ip)
                        city = response.city.name
                        country = response.country.name
                        lat = response.location.latitude
                        lon = response.location.longitude
                except Exception:
                    pass

            UserActivity.objects.create(
                user=user,
                # e.g. "GET /blog/posts/"
                action=f"{request.method} {request.path}",
                path=request.path,
                method=request.method,
                ip_address=ip,
                city=city,
                country=country,
                latitude=lat,
                longitude=lon,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                payload={}  # Middleware generally doesn't know parsed kwargs easily
            )
        except Exception:
            pass
