from .models import UserActivity, UserSession
import threading
import logging
import ipaddress
import hashlib
import uuid
from django.conf import settings
from django.utils import timezone
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

        if request.path_info.startswith('/api/') or request.path_info.startswith('/blog/') or request.path_info.startswith('/portfolio/'):
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
        if not (200 <= response.status_code < 300):
            return

        # Simple ignoring of assets/admin/etc if not filtered above
        # Using path_info for consistency with urls.py structure
        if request.path_info.startswith('/admin/') or request.path_info.startswith('/static') or request.path_info.startswith('/media'):
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

            if self.reader and ip:
                try:
                    # Handle local IPs
                    if ip in ['127.0.0.1', '::1']:
                        pass
                    else:
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
                if not request.session.session_key:
                    request.session.save()

                session_key = request.session.session_key

                # Handle Persistent Tracking ID
                tracking_id = request.COOKIES.get('rg_tid')
                # Generate Device Fingerprint
                device_fingerprint = self._get_device_fingerprint(request)

                if not tracking_id:
                    # Attempt to recover session via Fingerprint (Heuristic for Tor/Privacy Browsers)
                    # Look for a recent session (last 30 mins) with same fingerprint
                    # This risks merging concurrent Tor users, but ensures continuity for single users resetting identity
                    # Since Tor users share identical fingerprints, this effectively groups "Tor Traffic" together
                    # or maintains continuity for the single user case.
                    try:
                        recent_session = UserSession.objects.filter(
                            device_fingerprint=device_fingerprint,
                            last_seen_at__gte=timezone.now() - timezone.timedelta(minutes=30)
                        ).order_by('-last_seen_at').first()
                        
                        if recent_session and recent_session.tracking_id:
                            tracking_id = recent_session.tracking_id
                        else:
                            tracking_id = str(uuid.uuid4())
                    except Exception:
                         tracking_id = str(uuid.uuid4())

                    response.set_cookie(
                        'rg_tid',
                        tracking_id,
                        max_age=31536000,  # 1 year
                        samesite='Lax',
                        secure=settings.SESSION_COOKIE_SECURE or False
                    )

                # Check for existing session via tracking_id if session_key is new
                # This helps link sessions if cookies were cleared but tracking_id persists (rare for Tor, common for others)
                # Or if we want to link via fingerprint (very common for Tor since fingerprint is uniform)

                # Update or Create Session
                # We prioritize creation with geo info.
                current_time = timezone.now()

                # Update defaults to include new fields
                defaults = {
                    'user': user,
                    'ip_address': ip,
                    'city': city,
                    'country': country,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'started_at': current_time,
                    'last_seen_at': current_time,
                    'page_count': 1,
                    'tracking_id': tracking_id,
                    'device_fingerprint': device_fingerprint
                }

                # Note: This is synchronous DB hit. In high scale, use cache or async queue.
                user_session, created = UserSession.objects.get_or_create(
                    session_key=session_key,
                    defaults=defaults
                )

                if not created:
                    user_session.last_seen_at = current_time
                    user_session.page_count += 1
                    # Associate user if logged in later
                    if user and not user_session.user:
                        user_session.user = user

                    # Update tracking info if missing
                    if not user_session.tracking_id:
                        user_session.tracking_id = tracking_id
                    if not user_session.device_fingerprint:
                        user_session.device_fingerprint = device_fingerprint

                    user_session.save(
                        update_fields=['last_seen_at', 'page_count', 'user', 'tracking_id', 'device_fingerprint'])

            except Exception as e:
                logger.error(f"Session tracking failed: {e}")

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
            logger.error(f"Analytics tracking failed: {e}")
            pass
