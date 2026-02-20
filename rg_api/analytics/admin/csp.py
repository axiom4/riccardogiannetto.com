"""
Admin configuration for CSPReport model.
"""
from django.contrib import admin
from ..models import CSPReport


@admin.register(CSPReport)
class CSPReportAdmin(admin.ModelAdmin):
    """
    Admin configuration for CSPReport model.
    """
    list_display = (
        'created_at',
        'document_uri',
        'violated_directive',
        'blocked_uri',
        'ip_address',
        'status_code',
    )
    list_filter = (
        'created_at',
        'violated_directive',
        'effective_directive',
        'status_code',
    )
    search_fields = (
        'document_uri',
        'blocked_uri',
        'source_file',
        'ip_address',
        'original_policy',
    )
    readonly_fields = (
        'document_uri', 'referrer', 'violated_directive', 'effective_directive',
        'original_policy', 'blocked_uri', 'status_code', 'source_file',
        'line_number', 'column_number', 'raw_report', 'ip_address',
        'user_agent', 'city', 'country', 'latitude', 'longitude', 'created_at'
    )
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
