"""
Tests for the Gallery API.
"""
import io
import tempfile
from unittest.mock import patch

from PIL import Image
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from gallery.models import Gallery, ImageGallery

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


@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class ImageGalleryAPITest(APITestCase):
    """Test suite for image preview endpoint behavior."""

    def setUp(self):
        """Set up test image and image gallery record."""
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)

        self.media_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)

        self.user = User.objects.create_user(
            username='imgapi', password='password')
        self.gallery = Gallery.objects.create(
            title='Image API Gallery',
            tag='image-api-gallery',
            author=self.user
        )

        image_bytes = io.BytesIO()
        image = Image.new('RGB', (500, 300), color=(255, 0, 0))
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        upload = SimpleUploadedFile(
            'test.jpg',
            image_bytes.getvalue(),
            content_type='image/jpeg'
        )

        self.image = ImageGallery.objects.create(
            title='Fungo 1',
            image=upload,
            gallery=self.gallery,
            author=self.user,
            width=500,
            height=300,
        )

    @override_settings(IMAGE_GENERATOR_MAX_WIDTH=4000)
    @patch('gallery.views.image_gallery_view.ImageOptimizer.compress_and_resize')
    def test_width_3840_returns_image(self, mock_resize):
        """Requesting width 3840 should be allowed and return a webp response."""

        def fake_resize(_image_path, output_path, width):
            with open(output_path, 'wb') as out_file:
                out_file.write(b'RIFFxxxxWEBP')
            return True

        mock_resize.side_effect = fake_resize

        response = self.client.get(f'/portfolio/images/{self.image.slug}/width/3840')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/webp')

    @override_settings(IMAGE_GENERATOR_MAX_WIDTH=4000)
    def test_width_over_configured_limit_returns_404(self):
        """Requesting a width above the configured max should return 404."""
        response = self.client.get(f'/portfolio/images/{self.image.slug}/width/5000')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
