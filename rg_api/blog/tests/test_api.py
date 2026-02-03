from django.test import override_settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from blog.models import Category, Post


@override_settings(
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
