from django.db import models
from django.contrib.auth.models import User


class Gallery(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    tag = models.CharField(max_length=50, null=False, unique=True)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'galleries'
