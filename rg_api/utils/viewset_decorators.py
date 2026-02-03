"""
Decorator utilities for ViewSets.
"""
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


def cached_viewset(list_timeout=60 * 60 * 2, retrieve_timeout=60 * 60 * 24):
    """
    Decorator to apply caching to ViewSet list and retrieve methods.

    Args:
        list_timeout: Cache timeout for list view in seconds (default: 2 hours).
        retrieve_timeout: Cache timeout for retrieve view in seconds (default: 24 hours).

    Returns:
        Decorated class with cache applied to list and retrieve methods.
    """
    def decorator(cls):
        cls = method_decorator(cache_page(list_timeout), name='list')(cls)
        cls = method_decorator(cache_page(
            retrieve_timeout), name='retrieve')(cls)
        return cls
    return decorator
