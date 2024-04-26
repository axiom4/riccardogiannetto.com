from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        null=False,
        blank=False,
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]
