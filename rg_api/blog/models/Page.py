"""
Page model.
"""
from django.conf import settings
from django.db import models


class Page(models.Model):
    """
    Blog Page model.
    """
    objects = models.Manager()

    title = models.CharField(max_length=50)
    body = models.TextField()
    tag = models.CharField(max_length=50, null=False, unique=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)
