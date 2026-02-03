from django.db import models
from django.conf import settings

class UserSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, db_index=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    # Advanced Tracking
    tracking_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Persistent cookie ID for tracking across sessions",
        db_index=True
    )
    device_fingerprint = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Hash of header-based device characteristics",
        db_index=True
    )

    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_seen_at = models.DateTimeField(auto_now=True, db_index=True)
    page_count = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_seen_at']

    def __str__(self):
        return f"{self.ip_address} ({self.session_key}) - Pages: {self.page_count}"

    @property
    def duration(self):
        return self.last_seen_at - self.started_at
