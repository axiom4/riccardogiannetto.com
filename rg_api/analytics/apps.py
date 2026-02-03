"""
Analytics application configuration.
"""
from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Configuration for Analytics app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
