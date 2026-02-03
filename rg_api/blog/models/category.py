"""
Category model.
"""
from django.db import models


class Category(models.Model):
    """
    Blog Category model.
    """
    objects = models.Manager()

    name = models.CharField(
        null=False,
        blank=False,
        max_length=100,
        unique=True
    )

    class Meta:
        """Meta options for Category."""
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)
