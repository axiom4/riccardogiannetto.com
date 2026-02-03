from django.contrib import admin
from ..models import Comment


class CommentInline(admin.TabularInline):
    model = Comment
    readonly_fields = ['text', 'mail', 'created_at', 'ip']
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CommentAdmin(admin.ModelAdmin):
    fields = [('mail', 'post'), 'text']
    list_display = ('mail', 'post', 'text', 'created_at')
    list_filter = ('post__title', 'mail')
    search_fields = ('mail', 'post')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
