from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from .models import UserActivity
from .serializers import UserActivitySerializer

# ...existing code...


class UserActivityViewSet(viewsets.ModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer

# ...existing code...


@csrf_exempt
def csp_report(request):
    return HttpResponse(status=204)
