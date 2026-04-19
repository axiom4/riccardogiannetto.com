"""
Custom permissions for the API.
"""
from django.conf import settings
from rest_framework import permissions


def get_client_ip(request):
    """Retrieves the client IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    # Sanitize IP address to prevent log injection or malformed log entries
    if ip is not None:
        # Coerce to string and remove carriage returns, newlines, and other control chars
        ip = ''.join(ch for ch in str(ip) if ch.isprintable() and ch not in '\r\n')

    return ip


class AccessListPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.

    Uses X-Real-IP (set by the trusted nginx reverse proxy) to get the client IP.
    Falls back to REMOTE_ADDR when the header is not present (e.g. in development).
    Never reads X-Forwarded-For here to avoid client-controlled header spoofing.
    """

    def has_permission(self, request, view):
        """Check if request IP is in access list."""
        # X-Real-IP is set by nginx and cannot be spoofed by the client
        ip_addr = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '')

        # Sanitize to prevent log injection
        ip_addr = ''.join(ch for ch in str(ip_addr) if ch.isprintable() and ch not in '\r\n').strip()

        return ip_addr in settings.ACCESS_LIST
