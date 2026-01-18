from django.contrib import admin
from .models import UserActivity


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'path', 'method',
                    'ip_address', 'timestamp')
    list_filter = ('action', 'method', 'timestamp')
    search_fields = ('user__username', 'path', 'ip_address')
    readonly_fields = ('timestamp',)
