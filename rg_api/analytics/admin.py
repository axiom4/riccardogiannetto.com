from django.contrib import admin
from .models import UserActivity, UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'started_at', 'last_seen_at',
                    'duration', 'page_count', 'city', 'country', 'device_fingerprint')
    readonly_fields = ('started_at', 'last_seen_at',
                       'duration', 'tracking_id', 'device_fingerprint')
    search_fields = ('ip_address', 'city', 'country',
                     'user_agent', 'tracking_id', 'device_fingerprint')
    list_filter = ('country', 'started_at')

    def duration(self, obj):
        return obj.duration
    duration.short_description = 'Duration'

    change_form_template = 'admin/analytics/usersession/change_form.html'

    class Media:
        css = {
            'all': ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',)
        }
        js = ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_link', 'action', 'path', 'method',
                    'ip_address', 'country', 'city', 'timestamp')
    list_filter = ('action', 'method', 'timestamp', 'country')
    search_fields = ('user__username', 'path', 'ip_address', 'city', 'country')
    readonly_fields = ('timestamp', 'latitude', 'longitude', 'city', 'country')

    def session_link(self, obj):
        if obj.session:
            from django.utils.html import format_html
            from django.urls import reverse
            url = reverse('admin:analytics_usersession_change',
                          args=[obj.session.id])
            return format_html('<a href="{}">{}</a>', url, obj.session)
        return "-"
    session_link.short_description = 'Session'
