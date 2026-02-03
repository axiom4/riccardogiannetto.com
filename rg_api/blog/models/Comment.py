"""
Comment model.
"""
from django.db import models
from .post import Post


class Comment(models.Model):
    """
    Blog Comment model.
    """
    objects = models.Manager()

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False)
    mail = models.EmailField(blank=False, null=False)
    ip = models.GenericIPAddressField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return str(self.text)
