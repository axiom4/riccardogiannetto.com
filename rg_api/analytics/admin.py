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
        total_seconds = int(obj.duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    duration.short_description = 'Duration'

    change_form_template = 'admin/analytics/usersession/change_form.html'
    change_list_template = 'admin/analytics/usersession/change_list.html'

    def changelist_view(self, request, extra_context=None):
        from django.core.serializers.json import DjangoJSONEncoder
        import json

        response = super().changelist_view(request, extra_context=extra_context)

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # Aggregate geo data
        sessions = qs.exclude(latitude__isnull=True).exclude(longitude__isnull=True).exclude(
            latitude=0).exclude(longitude=0).values('latitude', 'longitude', 'city', 'country', 'ip_address')

        response.context_data['map_locations'] = json.dumps(
            list(sessions), cls=DjangoJSONEncoder)

        return response

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
