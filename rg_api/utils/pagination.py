"""
Base pagination classes for common use cases.
"""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Standard pagination configuration used across the application.

    Attributes:
        page_size (int): The default number of items to include on a page (5).
        page_size_query_param (str): The name of the query parameter to allow clients
                                     to set the page size ('page_size').
        max_page_size (int): The maximum number of items allowed per page (12).
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12
