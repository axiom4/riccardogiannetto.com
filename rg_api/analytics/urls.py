"""
Docstring for rg_api.analytics.urls
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserActivityViewSet, csp_report

router = DefaultRouter()
router.register(r"user-activity", UserActivityViewSet,
                basename="user-activity")

urlpatterns = [
    path("csp-report/", csp_report, name="csp-report"),
    path("", include(router.urls)),
]
