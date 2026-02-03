"""
Docstring for rg_api.analytics.middleware.analytics_middleware
"""
import logging

import ipaddress
import hashlib
import uuid
from django.conf import settings
from django.utils import timezone
from ..models import UserActivity, UserSession

try:
    import geoip2.database
except ImportError:
    geoip2 = None

logger = logging.getLogger(__name__)


class AnalyticsMiddleware:
    """
    Middleware responsible for analytics tracking, user session management, and geolocation.

    This middleware intercepts HTTP requests to specific application routes (API, blog, portfolio)
    to capture analytics data. It operates after the response has been generated to ensure
    only successful (2xx) requests are logged.

    Key Functionalities:
    - **IP Address Resolution**: Extracts client IPs handling potential proxy headers (X-Forwarded-For).
    - **Geolocation**: Uses GeoIP2 to resolve IP addresses to physical locations (City, Country, Lat/Lon).
    - **Session Tracking**: Manages `UserSession` records using a combination of Django session IDs,
      persistent cookies ('rg_tid'), and device fingerprinting to track users consistently across
      browser restarts.
    - **Activity Logging**: Creates discrete `UserActivity` records for tracked interactions (excluding
      admin and static paths).

    Attributes:
        get_response (callable): The next middleware or view in the chain.
        reader (geoip2.database.Reader | None): The GeoIP2 database reader instance used for
            location lookups, or None if the library/database is missing.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.reader = None
        if geoip2 and hasattr(settings, 'GEOIP_PATH'):
            try:
                self.reader = geoip2.database.Reader(settings.GEOIP_PATH)
            except Exception as e:
                logger.warning("GeoIP database not found or invalid: %s", e)

    def __call__(self, request):
        # Process request before view (and before cache check if cache middleware was used globaly,
        # but here cache_page is used on views, so this runs BEFORE cache_page check)

        response = self.get_response(request)

        # We log AFTER the response is generated (successfully).
        # Note: If cache_page intercepts inside the view layer, this middleware
        # still sees the request and the response coming back from the view "wrapper".

        if (request.path_info.startswith('/api/') or
                request.path_info.startswith('/blog/') or
                request.path_info.startswith('/portfolio/')):
            # Filter out admin, static, etc if needed.
            # Assuming typically API routes are relevant.
            # Adjust filter as needed.
            self.track_activity(request, response)

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get(
                'HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')

        if not ip:
            return None

        # Clean brackets if present
        ip = ip.strip('[]')

        if ip == 'localhost':
            return '127.0.0.1'

        try:
            ip_obj = ipaddress.ip_address(ip)
            # Unmap IPv4 mapped IPv6 addresses
            if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
                return str(ip_obj.ipv4_mapped)
            return str(ip_obj)
        except ValueError:
            return None

    def _get_device_fingerprint(self, request):
        """
        Create a hash based on available headers to identify consistent devices/browsers
        even if cookies are cleared.
        """
        components = [
            request.META.get('HTTP_USER_AGENT', ''),
            request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
            request.META.get('HTTP_ACCEPT_ENCODING', ''),
            request.META.get('HTTP_OOC', ''),  # Sometimes used by opera
        ]
        # Create a string from non-empty components
        fingerprint_source = "|".join([str(c) for c in components if c])
        return hashlib.sha256(fingerprint_source.encode('utf-8')).hexdigest()

    def track_activity(self, request, response):
        """
        Captures and records analytics data for a successfully processed HTTP request.

        This method serves as the core tracking logic for the middleware. It filters out
        error responses (non-2xx) and static/admin paths before processing the request
        to extract:
        1. Geolocation data (City, Country, Lat/Lon) based on the client IP.
        2. User session identifiers using a persistent tracking cookie ('rg_tid')
           and device fingerprinting.

        It handles the lifecycle of `UserSession` objects (creation or update) and
        logs a discrete `UserActivity` record for the specific action taken.

        Args:
            request (HttpRequest): The incoming Django request object.
            response (HttpResponse): The outgoing Django response object, used to modify
                cookies and check status codes.

        Returns:
            None
        """
        if not (200 <= response.status_code < 300):
            return

        # Simple ignoring of assets/admin/etc if not filtered above
        # Using path_info for consistency with urls.py structure
        if (request.path_info.startswith('/admin/') or
                request.path_info.startswith('/static') or
                request.path_info.startswith('/media')):
            return

        try:
            ip = self._get_client_ip(request)
            if not ip:
                return

            user = request.user if request.user.is_authenticated else None

            # We don't have access to "viewset action" easily here without using process_view
            # and storing it, but path is the most important.

            city = None
            country = None
            lat = None
            lon = None

            # Try to get location
            if ip:
                # 1. Check Localhost / Dev
                if ip in ['127.0.0.1', '::1'] and settings.DEBUG:
                    city = "Rome (Localhost)"
                    country = "Italy"
                    lat = 41.9028
                    lon = 12.4964

                # 2. Use GeoIP if available and not already set (or if we want real geoip for non-localhost)
                elif self.reader:
                    try:
                        geo_response = self.reader.city(ip)
                        city = geo_response.city.name
                        country = geo_response.country.name
                        lat = geo_response.location.latitude
                        lon = geo_response.location.longitude
                    except Exception:
                        pass

            # Manage UserSession
            user_session = None
            try:
                # Ensure Django session exists
                if not request.session.session_key:
                    request.session.save()
                session_key = request.session.session_key

                # Generate Device Fingerprint
                device_fingerprint = self._get_device_fingerprint(request)

                # Handle Persistent Tracking ID from Cookie
                tracking_id = request.COOKIES.get('rg_tid')
                current_time = timezone.now()

                if not tracking_id:
                    # Attempt recovery via Fingerprint
                    if device_fingerprint:
                        recent_session = UserSession.objects.filter(
                            device_fingerprint=device_fingerprint,
                            last_seen_at__gte=current_time -
                            timezone.timedelta(minutes=30)
                        ).order_by('-last_seen_at').first()
                        if recent_session and recent_session.tracking_id:
                            tracking_id = recent_session.tracking_id

                    if not tracking_id:
                        tracking_id = str(uuid.uuid4())

                    # Set cookie
                    # Use SameSite=None and Secure=True to allow cross-site tracking (e.g. Frontend on different port)
                    # Note: Secure=True works on localhost and HTTPS.
                    response.set_cookie(
                        'rg_tid',
                        tracking_id,
                        max_age=31536000,  # 1 year
                        samesite='None',
                        secure=True
                    )

                user_session = None

                # 1. Try to find an ACTIVE session by Tracking ID
                if tracking_id:
                    user_session = UserSession.objects.filter(
                        tracking_id=tracking_id,
                        last_seen_at__gte=current_time -
                        timezone.timedelta(minutes=30)
                    ).order_by('-last_seen_at').first()

                if user_session:
                    # Update existing session

                    # Update session_key if it changed (e.g. login)
                    if user_session.session_key != session_key:
                        if not UserSession.objects.filter(session_key=session_key).exists():
                            user_session.session_key = session_key

                    user_session.last_seen_at = current_time
                    user_session.page_count += 1

                    if user and not user_session.user:
                        user_session.user = user

                    # Update geo if missing or changed
                    if not user_session.ip_address:
                        user_session.ip_address = ip

                    if city and (user_session.city != city):
                        user_session.city = city
                        user_session.country = country
                        user_session.latitude = lat
                        user_session.longitude = lon

                    user_session.save(update_fields=[
                        'session_key', 'last_seen_at', 'page_count', 'user',
                        'ip_address', 'city', 'country', 'latitude',
                        'longitude'
                    ])

                else:
                    # 2. Create New Session
                    defaults = {
                        'user': user,
                        'ip_address': ip,
                        'city': city,
                        'country': country,
                        'latitude': lat,
                        'longitude': lon,
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'started_at': current_time,
                        'last_seen_at': current_time,
                        'page_count': 1,
                        'tracking_id': tracking_id,
                        'device_fingerprint': device_fingerprint
                    }

                    user_session, created = UserSession.objects.get_or_create(
                        session_key=session_key,
                        defaults=defaults
                    )

                    if not created:
                        user_session.last_seen_at = current_time
                        user_session.page_count += 1

                        if not user_session.tracking_id:
                            user_session.tracking_id = tracking_id
                            user_session.device_fingerprint = device_fingerprint

                        user_session.save(
                            update_fields=[
                                'last_seen_at',
                                'page_count',
                                'tracking_id',
                                'device_fingerprint'
                            ]
                        )

            except Exception as e:
                logger.error("Session tracking failed: %s", e)

            UserActivity.objects.create(
                session=user_session,
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
        except Exception as e:
            logger.error("Analytics tracking failed: %s", e)
