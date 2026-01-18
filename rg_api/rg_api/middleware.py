class RemoveNoStoreCacheHeaderMiddleware:
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
            cache_control = response['Cache-Control']
            if 'no-store' in cache_control:
                # Replace no-store with no-cache while preserving other directives
                response['Cache-Control'] = cache_control.replace(
                    'no-store', 'no-cache')

        return response
