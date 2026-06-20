from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from martor.views import (
    markdown_imgur_uploader,
    markdown_search_user,
    markdownfy_view,
)


@csrf_exempt
@staff_member_required
@require_POST
def admin_markdownify_view(request):
    return markdownfy_view(request)

urlpatterns = [
    path('markdownify/', admin_markdownify_view, name='martor_markdownfy'),
    path('uploader/', staff_member_required(markdown_imgur_uploader), name='imgur_uploader'),
    path('search-user/', staff_member_required(markdown_search_user), name='search_user_json'),
]
