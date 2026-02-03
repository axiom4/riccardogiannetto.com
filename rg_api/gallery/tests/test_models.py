"""
Tests for Gallery models.
"""
import os
import tempfile
from unittest.mock import patch
from PIL import Image

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from gallery.models import Gallery, ImageGallery

User = get_user_model()


@override_settings(
    MEDIA_ROOT=tempfile.gettempdir(),
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class GalleryModelTest(TestCase):
    """Test suite for the Gallery model."""

    def setUp(self):
        """Set up test environment."""
        self.user = User.objects.create_user(
            username='testuser', password='password')
        self.gallery = Gallery.objects.create(
            title='Test Gallery',
            description='Test Description',
            tag='test-gallery',
            author=self.user
        )

    def tearDown(self):
        """Clean up test environment."""
        # Cleanup code if needed

    def test_gallery_creation(self):
        """Test that a Gallery object is created correctly."""
        self.assertEqual(self.gallery.title, 'Test Gallery')
        self.assertEqual(str(self.gallery), 'Test Gallery')


@override_settings(
    MEDIA_ROOT=tempfile.gettempdir(),
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class ImageGalleryModelTest(TestCase):
    """Test suite for the ImageGallery model."""

    def setUp(self):
        """Set up test environment."""
        self.user = User.objects.create_user(
            username='testuser', password='password')
        self.gallery = Gallery.objects.create(
            title='Test Gallery',
            tag='test-gallery',
            author=self.user
        )

    def create_dummy_image(self):
        """Create a temp dummy image file and return its path."""
        image = Image.new('RGB', (100, 100), color='red')
        # pylint: disable=consider-using-with
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image.save(tmp_file, format='JPEG')
        tmp_file.close()
        return tmp_file.name

    @patch('gallery.models.image_gallery.get_gps_data')
    @patch('PIL.Image.open')
    def test_image_save_metadata(self, mock_image_open, mock_get_gps):
        """Test that metadata is extracted and saved with the image."""
        # Setup mocks
        mock_get_gps.return_value = (
            41.9028, 12.4964, 50.0)  # Rome coordinates

        # Create a dummy image file
        img_path = self.create_dummy_image()

        with open(img_path, 'rb') as f:
            content = f.read()

        uploaded_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=content,
            content_type='image/jpeg'
        )

        # Mock PIL Image object for width/height and getexif
        mock_img_instance = mock_image_open.return_value.__enter__.return_value
        mock_img_instance.size = (800, 600)
        mock_img_instance.getexif.return_value = {
            # Standard EXIF tags (keys are integers)
            # Make (mapped to nothing in our code currently)
            271: 'TestCamera',
            272: 'TestModel',       # Model -> camera_model
            306: '2023:01:01 12:00:00',  # DateTime
            33434: 0.01,            # ExposureTime -> shutter_speed
            37386: 50.0,            # FocalLength
        }

        # Create ImageGallery instance
        image_gallery = ImageGallery(
            title='Test Image',
            gallery=self.gallery,
            author=self.user,
            image=uploaded_file
        )
        image_gallery.save()

        # refresh
        image_gallery.refresh_from_db()

        # Assertions
        self.assertEqual(image_gallery.width, 800)

        # Cleanup
        if os.path.exists(img_path):
            os.remove(img_path)

        self.assertEqual(image_gallery.height, 600)
        self.assertEqual(image_gallery.camera_model, 'TestModel')
        self.assertEqual(image_gallery.latitude, 41.9028)
        self.assertEqual(image_gallery.longitude, 12.4964)
        self.assertEqual(image_gallery.shutter_speed, 0.01)
