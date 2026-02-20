"""
CSP Violation Report Models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import GeoLocationMixin


class CSPReport(GeoLocationMixin):
    """
    Model for storing Content Security Policy violation reports.
    """
    document_uri = models.URLField(
        max_length=500, blank=True, null=True, db_index=True)
    referrer = models.URLField(max_length=500, blank=True, null=True)
    violated_directive = models.CharField(
        max_length=255, blank=True, null=True, db_index=True)
    effective_directive = models.CharField(
        max_length=255, blank=True, null=True)
    original_policy = models.TextField(blank=True, null=True)
    blocked_uri = models.CharField(
        max_length=500, blank=True, null=True, db_index=True)
    status_code = models.IntegerField(blank=True, null=True)
    source_file = models.CharField(max_length=500, blank=True, null=True)
    line_number = models.IntegerField(blank=True, null=True)
    column_number = models.IntegerField(blank=True, null=True)
    raw_report = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('CSP Report')
        verbose_name_plural = _('CSP Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.violated_directive} at {self.document_uri}"
