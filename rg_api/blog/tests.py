import tempfile
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from blog.models import Category, Post


@override_settings(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Test Category')


@override_settings(
    MEDIA_ROOT=tempfile.gettempdir(),
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
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

        image_content = b'\x00\x00\x00' # Dummy content
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
        self.assertTrue(post.image.name.endswith('.webp')) # The logic converts to webp


@override_settings(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class BlogAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apitestuser', password='password')
        self.post = Post.objects.create(
            title='API Post',
            body='API Body',
            author=self.user
        )
        self.category = Category.objects.create(name='API Category')
        self.post.categories.add(self.category)

    def test_list_posts(self):
        url = '/blog/posts'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check pagination
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'API Post')

    def test_list_categories(self):
        url = '/blog/categories'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Categories might not be paginated or paginated depending on viewset
        # Checking if 'results' key exists to handle both cases
        if 'results' in response.data:
            data = response.data['results']
        else:
            data = response.data
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'API Category')
