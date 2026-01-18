from django.contrib import admin
from .models import UserActivity, UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'started_at', 'last_seen_at', 'duration', 'page_count', 'city', 'country')
    readonly_fields = ('started_at', 'last_seen_at', 'duration')
    
    def duration(self, obj):
        return obj.duration
    duration.short_description = 'Duration'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'path', 'method',
                    'ip_address', 'country', 'city', 'timestamp')
    list_filter = ('action', 'method', 'timestamp', 'country')
    search_fields = ('user__username', 'path', 'ip_address', 'city', 'country')
    readonly_fields = ('timestamp', 'latitude', 'longitude', 'city', 'country')

    change_form_template = 'admin/analytics/useractivity/change_form.html'

    class Media:
        css = {
            'all': ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',)
        }
        js = ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',)
