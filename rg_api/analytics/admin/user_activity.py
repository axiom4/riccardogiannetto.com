from django.contrib import admin
from ..models import UserActivity

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_link', 'action', 'path', 'method',
                    'ip_address', 'country', 'city', 'timestamp')
    list_filter = ('action', 'method', 'timestamp', 'country')
    search_fields = ('user__username', 'path', 'ip_address', 'city', 'country')
    readonly_fields = ('timestamp', 'latitude', 'longitude', 'city', 'country')

    change_list_template = 'admin/analytics/useractivity/change_list.html'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('truncate/', self.truncate_view,
                 name='analytics_useractivity_truncate'),
        ]
        return custom_urls + urls

    def truncate_view(self, request):
        from django.shortcuts import redirect
        from django.contrib import messages

        if request.user.is_superuser:
            count = UserActivity.objects.count()
            UserActivity.objects.all().delete()
            self.message_user(
                request, f"Successfully deleted {count} activities.", messages.SUCCESS)
        else:
            self.message_user(
                request, "You do not have permission to perform this action.", messages.ERROR)

        return redirect('admin:analytics_useractivity_changelist')

    def session_link(self, obj):
        if obj.session:
            from django.utils.html import format_html
            from django.urls import reverse
            url = reverse('admin:analytics_usersession_change',
                          args=[obj.session.id])
            return format_html('<a href="{}">{}</a>', url, obj.session)
        return "-"
    session_link.short_description = 'Session'
