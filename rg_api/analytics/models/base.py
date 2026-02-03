"""
Base models and mixins for analytics application.
"""
from django.db import models


class GeoLocationMixin(models.Model):
    """
    Abstract mixin containing common geo-location and client info fields.
    """
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, db_index=True
    )
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        """Meta options for GeoLocationMixin."""
        abstract = True
