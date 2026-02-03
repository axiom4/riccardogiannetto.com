"""
Docstring for rg_api.analytics.middleware.analytics_middleware
"""
import logging
import ipaddress
import hashlib
import uuid
from django.conf import settings
from django.utils import timezone
try:
    import geoip2.database
    import geoip2.errors
    GEOIP_LIB = geoip2
except ImportError:
    GEOIP_LIB = None

from ..models import UserActivity, UserSession

logger = logging.getLogger(__name__)


class AnalyticsMiddleware:
    """
    Middleware responsible for analytics tracking, user session management, and geolocation.

    This middleware intercepts HTTP requests to specific application routes (API, blog, portfolio)
    to capture analytics data. It operates after the response has been generated to ensure
    only successful (2xx) requests are logged.

    Key Functionalities:
    - **IP Address Resolution**: Extracts client IPs handling potential proxy
      headers (X-Forwarded-For).
    - **Geolocation**: Uses GeoIP2 to resolve IP addresses to physical locations
      (City, Country, Lat/Lon).
    - **Session Tracking**: Manages `UserSession` records using a combination of
      Django session IDs, persistent cookies ('rg_tid'), and device fingerprinting
      to track users consistently across browser restarts.
    - **Activity Logging**: Creates discrete `UserActivity` records for tracked
      interactions (excluding admin and static paths).

    Attributes:
        get_response (callable): The next middleware or view in the chain.
        reader (geoip2.database.Reader | None): The GeoIP2 database reader instance used for
            location lookups, or None if the library/database is missing.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.reader = None
        if GEOIP_LIB and hasattr(settings, 'GEOIP_PATH'):
            try:
                self.reader = GEOIP_LIB.database.Reader(settings.GEOIP_PATH)
            except (FileNotFoundError, PermissionError, ValueError) as e:
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

    def _get_geo_data(self, ip):
        """Resolve IP to location using GeoIP2."""
        city, country, lat, lon = None, None, None, None

        if not ip:
            return city, country, lat, lon

        # 1. Check Localhost / Dev
        if ip in ['127.0.0.1', '::1'] and settings.DEBUG:
            return "Rome (Localhost)", "Italy", 41.9028, 12.4964

        # 2. Use GeoIP if available
        if self.reader:
            try:
                geo_response = self.reader.city(ip)
                city = geo_response.city.name
                country = geo_response.country.name
                lat = geo_response.location.latitude
                lon = geo_response.location.longitude
            except (GEOIP_LIB.errors.GeoIP2Error, ValueError, TypeError):
                # Using broad geoip exception base class if possible or specific ones
                # Since we import errors conditionally, we need to be careful.
                # But here self.reader implies GEOIP_LIB is loaded.
                pass
            # We can also catch standard exceptions that might occur during lookup

        return city, country, lat, lon

    def _get_tracking_id(self, request, response, device_fingerprint):
        """Retrieve or generate tracking ID."""
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
            response.set_cookie(
                'rg_tid',
                tracking_id,
                max_age=31536000,  # 1 year
                samesite='None',
                secure=True
            )
        return tracking_id

    def _update_session(self, user_session, session_data):
        """Update existing user session."""
        session_key = session_data['session_key']
        user = session_data['user']
        ip = session_data['ip']
        city = session_data['city']

        # Update session_key if it changed
        if user_session.session_key != session_key:
            if not UserSession.objects.filter(session_key=session_key).exists():
                user_session.session_key = session_key

        user_session.last_seen_at = timezone.now()
        user_session.page_count += 1

        if user and not user_session.user:
            user_session.user = user

        # Update geo if missing or changed
        if not user_session.ip_address:
            user_session.ip_address = ip

        if city and (user_session.city != city):
            user_session.city = city
            user_session.country = session_data['country']
            user_session.latitude = session_data['lat']
            user_session.longitude = session_data['lon']

        user_session.save(update_fields=[
            'session_key', 'last_seen_at', 'page_count', 'user',
            'ip_address', 'city', 'country', 'latitude',
            'longitude'
        ])

    def _create_session(self, session_data):
        """Create a new user session."""
        current_time = timezone.now()
        defaults = {
            'user': session_data['user'],
            'ip_address': session_data['ip'],
            'city': session_data['city'],
            'country': session_data['country'],
            'latitude': session_data['lat'],
            'longitude': session_data['lon'],
            'user_agent': session_data['user_agent'],
            'started_at': current_time,
            'last_seen_at': current_time,
            'page_count': 1,
            'tracking_id': session_data['tracking_id'],
            'device_fingerprint': session_data['device_fingerprint']
        }

        user_session, created = UserSession.objects.get_or_create(
            session_key=session_data['session_key'],
            defaults=defaults
        )

        if not created:
            user_session.last_seen_at = current_time
            user_session.page_count += 1

            if not user_session.tracking_id:
                user_session.tracking_id = session_data['tracking_id']
                user_session.device_fingerprint = session_data['device_fingerprint']

            user_session.save(
                update_fields=[
                    'last_seen_at',
                    'page_count',
                    'tracking_id',
                    'device_fingerprint'
                ]
            )
        return user_session

    def _manage_session(self, request, response, ip, geo_data):
        """Orchestrate session management."""
        # Ensure Django session exists
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        device_fingerprint = self._get_device_fingerprint(request)
        tracking_id = self._get_tracking_id(
            request, response, device_fingerprint)
        city, country, lat, lon = geo_data
        user = request.user if request.user.is_authenticated else None

        session_data = {
            'session_key': session_key,
            'user': user,
            'ip': ip,
            'city': city,
            'country': country,
            'lat': lat,
            'lon': lon,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'tracking_id': tracking_id,
            'device_fingerprint': device_fingerprint
        }

        # Try to find an ACTIVE session by Tracking ID
        user_session = None
        if tracking_id:
            user_session = UserSession.objects.filter(
                tracking_id=tracking_id,
                last_seen_at__gte=timezone.now() - timezone.timedelta(minutes=30)
            ).order_by('-last_seen_at').first()

        if user_session:
            self._update_session(user_session, session_data)
        else:
            user_session = self._create_session(session_data)

        return user_session

    def track_activity(self, request, response):
        """
        Captures and records analytics data for a successfully processed HTTP request.
        """
        if not 200 <= response.status_code < 300:
            return

        # Simple ignoring of assets/admin/etc if not filtered above
        if (request.path_info.startswith('/admin/') or
                request.path_info.startswith('/static') or
                request.path_info.startswith('/media')):
            return

        try:
            ip = self._get_client_ip(request)
            if not ip:
                return

            geo_data = self._get_geo_data(ip)
            city, country, lat, lon = geo_data
            user_session = self._manage_session(
                request, response, ip, geo_data)
            user = request.user if request.user.is_authenticated else None

            UserActivity.objects.create(
                session=user_session,
                user=user,
                action=f"{request.method} {request.path}",
                path=request.path,
                method=request.method,
                ip_address=ip,
                city=city,
                country=country,
                latitude=lat,
                longitude=lon,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                payload={}
            )
        except (ValueError, AttributeError) as e:
            # Catch specific errors that might happen during data gathering/storage
            logger.error("Analytics tracking specific error: %s", e)
