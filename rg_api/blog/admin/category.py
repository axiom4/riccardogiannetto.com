from django.contrib import admin
from ..models import Category


class CategoryAdmin(admin.ModelAdmin):
    fields = ['name']
