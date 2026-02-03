import tempfile
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from blog.models import Category, Post


@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Test Category')


@override_settings(
    MEDIA_ROOT=tempfile.gettempdir(),
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='authortest', password='password')
        self.category = Category.objects.create(name='Tech')

    @patch('utils.image_optimizer.ImageOptimizer.compress_and_resize')
    def test_post_creation(self, mock_optimize):
        # Mock optimizer to return the same file buffer or similar
        mock_optimize.side_effect = lambda img, width: img

        image_content = b'\x00\x00\x00'  # Dummy content
        uploaded = SimpleUploadedFile(
            'test.jpg', image_content, content_type='image/jpeg')

        post = Post.objects.create(
            title='My Post',
            body='Content body',
            author=self.user,
            image=uploaded
        )
        post.categories.add(self.category)

        self.assertEqual(post.title, 'My Post')
        self.assertEqual(post.categories.count(), 1)
        # The logic converts to webp
        self.assertTrue(post.image.name.endswith('.webp'))
