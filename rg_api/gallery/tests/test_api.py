"""
Tests for the Gallery API.
"""
from django.test import override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from gallery.models import Gallery

User = get_user_model()


@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class GalleryAPITest(APITestCase):
    """Test suite for the Gallery API endpoints."""

    def setUp(self):
        """Set up test environment."""
        self.user = User.objects.create_user(
            username='testapi', password='password')
        self.gallery = Gallery.objects.create(
            title='API Gallery',
            tag='api-gallery',
            author=self.user
        )

    def test_list_galleries(self):
        """Test listing galleries."""
        url = '/portfolio/galleries'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle Pagination
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'API Gallery')

    def test_retrieve_gallery(self):
        """Test retrieving a single gallery."""
        response = self.client.get(f'/portfolio/galleries/{self.gallery.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Gallery')
