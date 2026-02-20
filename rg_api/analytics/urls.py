"""
URL Configuration for Analytics app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserActivityViewSet, csp_report

router = DefaultRouter()
router.register(r'activities', UserActivityViewSet)

urlpatterns = [
    path('csp-report/', csp_report, name='csp-report'),
    path('', include(router.urls)),
]
