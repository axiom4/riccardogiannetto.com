from .models import UserActivity
import threading

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

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
            
            UserActivity.objects.create(
                user=user,
                action=f"{request.method} {request.path}", # e.g. "GET /blog/posts/"
                path=request.path,
                method=request.method,
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                payload={} # Middleware generally doesn't know parsed kwargs easily
            )
        except Exception:
            pass
