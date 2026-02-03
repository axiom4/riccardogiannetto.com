"""
Category admin.
"""
from django.contrib import admin


class CategoryAdmin(admin.ModelAdmin):
    """
    Category admin.
    """
    fields = ['name']
