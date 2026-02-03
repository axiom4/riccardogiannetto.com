"""
Custom Middleware for the API.
"""


class RemoveNoStoreCacheHeaderMiddleware:  # pylint: disable=too-few-public-methods
    """
    Middleware to replace 'no-store' in Cache-Control header with 'no-cache'.
    'no-store' prevents the browser's Back-Forward Cache (bfcache) from working.
    'no-cache' forces revalidation but allows bfcache in many browsers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.has_header('Cache-Control'):
            cache_control = response['Cache-Control'].lower()

            # If no-store is present, we must remove it to allow BFCache
            if 'no-store' in cache_control:
                # Split directives, remove no-store, and rebuild
                directives = [d.strip() for d in cache_control.split(',')]

                # Filter out no-store
                directives = [d for d in directives if d != 'no-store']

                # Ensure no-cache is present if we removed no-store (security/freshness)
                if 'no-cache' not in directives:
                    directives.append('no-cache')

                response['Cache-Control'] = ', '.join(directives)

        return response
