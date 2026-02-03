"""
Tests for UserSession model.
"""
from django.test import TestCase
from ..models import UserSession


class UserSessionModelTest(TestCase):
    """
    Test suite for UserSession model.
    """

    def setUp(self):
        """Set up test environment."""
        self.session = UserSession.objects.create(
            session_key="test_session_key_123",
            ip_address="127.0.0.1",
            user_agent="TestAgent/1.0"
        )

    def test_session_creation(self):
        """Test that a UserSession instance is correctly created."""
        self.assertEqual(self.session.session_key, "test_session_key_123")
        self.assertEqual(self.session.ip_address, "127.0.0.1")
        self.assertEqual(self.session.page_count, 1)

    def test_session_str(self):
        """Test the string representation of UserSession."""
        expected_str = (
            f"{self.session.ip_address} ({self.session.session_key}) "
            f"- Pages: {self.session.page_count}"
        )
        self.assertEqual(str(self.session), expected_str)

    def test_session_duration(self):
        """Test that duration property returns a timedelta."""
        self.assertIsNotNone(self.session.duration)
