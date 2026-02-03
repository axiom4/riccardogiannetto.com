"""
User activity tracking models.
"""
from django.db import models
from django.conf import settings
from .user_session import UserSession
from .base import GeoLocationMixin


class UserActivity(GeoLocationMixin, models.Model):
    """
    Model for storing individual user actions and events.
    """
    objects = models.Manager()

    session = models.ForeignKey(
        UserSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )
    action = models.CharField(max_length=255, db_index=True)
    path = models.CharField(max_length=1024, blank=True)
    method = models.CharField(max_length=10, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        """Meta options for UserActivity."""
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.action} - {self.timestamp}"

    @property
    def short_description(self):
        """Returns a short description of the activity."""
        return f"{self.action} at {self.path}"
