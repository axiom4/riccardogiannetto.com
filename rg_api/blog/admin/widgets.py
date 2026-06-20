"""
Shared Martor admin widget configuration.
"""
from django.conf import settings
from martor.widgets import AdminMartorWidget


def _prefixed(path):
    script_name = getattr(settings, 'FORCE_SCRIPT_NAME', '') or ''
    script_name = script_name.rstrip('/')
    if not script_name or not path.startswith('/'):
        return path
    if path == script_name or path.startswith(script_name + '/'):
        return path
    return script_name + path


MARTOR_ADMIN_WIDGET = AdminMartorWidget(attrs={
    'data-markdownfy-url': _prefixed('/martor/markdownify/'),
    'data-upload-url': _prefixed('/martor/uploader/'),
    'data-search-users-url': _prefixed('/martor/search-user/'),
})
