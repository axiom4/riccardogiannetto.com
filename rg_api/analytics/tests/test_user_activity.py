"""
Tests for UserActivity model and API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import UserActivity

User = get_user_model()


class UserActivityModelTest(TestCase):
    """
    Test suite for UserActivity model.
    """

    def setUp(self):
        """Set up test environment."""
        self.user = User.objects.create_user(
            username='testuser', password='password')
        self.activity = UserActivity.objects.create(
            user=self.user,
            action="PAGE_VIEW",
            path="/home",
            method="GET",
            ip_address="127.0.0.1"
        )

    def test_activity_creation(self):
        """Test that UserActivity is correctly created."""
        self.assertEqual(self.activity.action, "PAGE_VIEW")
        self.assertEqual(self.activity.user, self.user)
        self.assertEqual(self.activity.path, "/home")

    def test_activity_str(self):
        """Test the string representation of UserActivity."""
        self.assertIn("testuser", str(self.activity))
        self.assertIn("PAGE_VIEW", str(self.activity))


class UserActivityAPITest(APITestCase):
    """
    Test suite for UserActivity API.
    """

    def setUp(self):
        """Set up test environment."""
        self.list_url = reverse('useractivity-list')
        self.user = User.objects.create_user(
            username='apiuser', password='password')

    def test_create_activity_anonymous(self):
        """Test creating an activity as an anonymous user."""
        data = {
            "action": "CLICK",
            "path": "/gallery",
            "method": "POST",
            "payload": {"button": "submit"}
        }
        client = APIClient(enforce_csrf_checks=False)
        response = client.post(
            self.list_url,
            data,
            format='json',
            REMOTE_ADDR="192.168.1.50",
            HTTP_USER_AGENT="AnonymousAgent/1.0"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserActivity.objects.count(), 1)

        activity = UserActivity.objects.first()
        self.assertEqual(activity.ip_address, "192.168.1.50")
        self.assertEqual(activity.user_agent, "AnonymousAgent/1.0")
        self.assertIsNone(activity.user)

    def test_create_activity_authenticated(self):
        """Test creating an activity as an authenticated user."""
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "LOGIN",
            "path": "/login",
            "method": "POST"
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        activity = UserActivity.objects.latest('timestamp')
        self.assertEqual(activity.user, self.user)

    def test_x_forwarded_for_ip(self):
        """Test that X-Forwarded-For header is used for IP if present."""
        data = {
            "action": "PROXY_VISIT",
            "path": "/",
            "method": "GET"
        }
        response = self.client.post(
            self.list_url,
            data,
            format='json',
            HTTP_X_FORWARDED_FOR="10.0.0.1, 192.168.1.1"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        activity = UserActivity.objects.latest('timestamp')
        self.assertEqual(activity.ip_address, "10.0.0.1")
