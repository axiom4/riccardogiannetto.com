""" Model definition for Gallery. """
from django.db import models
from django.contrib.auth.models import User


class Gallery(models.Model):
    """
    Represents a collection of media items or images.

    This model stores information about a specific gallery, including its title,
    description, a unique tag for identification, the author who created it,
    and timestamps for creation and last update.

    Attributes:
        title (CharField): The display title of the gallery.
        description (TextField): A detailed description of the gallery's contents.
        tag (CharField): A unique slug or tag used to identify the gallery.
        author (ForeignKey): A reference to the User who created the gallery.
        created_at (DateTimeField): The date and time when the gallery was created.
        updated_at (DateTimeField): The date and time when the gallery was last modified.
    """
    title = models.CharField(max_length=50)
    description = models.TextField()
    tag = models.CharField(max_length=50, null=False, unique=True)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        """
        Meta options for the Gallery model.
        """
        verbose_name_plural = 'galleries'
        ordering = ['-created_at']
