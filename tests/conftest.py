"""
Shared pytest fixtures for the Hawkpost test suite.
"""
import os
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.utils import timezone as django_timezone


User = get_user_model()


@pytest.fixture
def temp_dir():
    """Create a temporary directory that is cleaned up after the test."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_settings(settings):
    """Fixture to easily modify Django settings for tests."""
    return settings


@pytest.fixture
def client():
    """Django test client instance."""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Django test client with an authenticated user."""
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Django test client with an authenticated admin user."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def user(db):
    """Create a regular test user."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )


@pytest.fixture
def admin_user(db):
    """Create an admin test user."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User"
    )


@pytest.fixture
def another_user(db):
    """Create another regular test user for multi-user tests."""
    return User.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password="anotherpass123",
        first_name="Another",
        last_name="User"
    )


@pytest.fixture
def sample_file():
    """Create a sample uploaded file for testing file uploads."""
    content = b"This is a test file content"
    return SimpleUploadedFile(
        "test_file.txt",
        content,
        content_type="text/plain"
    )


@pytest.fixture
def sample_image():
    """Create a sample image file for testing image uploads."""
    # Create a minimal valid PNG image
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return SimpleUploadedFile(
        "test_image.png",
        png_data,
        content_type="image/png"
    )


@pytest.fixture
def mock_datetime(mocker):
    """Mock datetime to return a fixed time."""
    fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mock = mocker.patch("django.utils.timezone.now")
    mock.return_value = fixed_time
    return fixed_time


@pytest.fixture
def api_client(client):
    """Client configured for API requests with JSON content type."""
    class APIClient(Client):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        def _add_headers(self, **kwargs):
            kwargs.setdefault('content_type', 'application/json')
            kwargs.setdefault('HTTP_ACCEPT', 'application/json')
            return kwargs
            
        def get(self, *args, **kwargs):
            return super().get(*args, **self._add_headers(**kwargs))
            
        def post(self, *args, **kwargs):
            return super().post(*args, **self._add_headers(**kwargs))
            
        def put(self, *args, **kwargs):
            return super().put(*args, **self._add_headers(**kwargs))
            
        def patch(self, *args, **kwargs):
            return super().patch(*args, **self._add_headers(**kwargs))
            
        def delete(self, *args, **kwargs):
            return super().delete(*args, **self._add_headers(**kwargs))
    
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """API client with an authenticated user."""
    api_client.force_login(user)
    return api_client


@pytest.fixture
def mock_celery_task(mocker):
    """Mock Celery task execution to run synchronously."""
    def _mock_task(task_path):
        return mocker.patch(task_path, side_effect=lambda *args, **kwargs: None)
    return _mock_task


@pytest.fixture
def captured_emails(settings):
    """Capture emails sent during tests."""
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    from django.core import mail
    mail.outbox = []
    return mail.outbox


@pytest.fixture
def mock_external_api(mocker):
    """Mock external API calls."""
    def _mock_api(url, response_data=None, status_code=200):
        mock_response = mocker.Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = response_data or {}
        mock_response.text = str(response_data or {})
        
        mock_get = mocker.patch("requests.get", return_value=mock_response)
        mock_post = mocker.patch("requests.post", return_value=mock_response)
        
        return {
            "get": mock_get,
            "post": mock_post,
            "response": mock_response
        }
    return _mock_api


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.
    This can be overridden by using pytest.mark.django_db(transaction=True)
    for tests that need transactions.
    """
    pass


@pytest.fixture
def test_data_factory():
    """Factory for creating various test data."""
    class TestDataFactory:
        @staticmethod
        def create_users(count=3):
            """Create multiple test users."""
            users = []
            for i in range(count):
                user = User.objects.create_user(
                    username=f"user{i}",
                    email=f"user{i}@example.com",
                    password=f"pass{i}123"
                )
                users.append(user)
            return users
        
        @staticmethod
        def create_datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0):
            """Create a timezone-aware datetime."""
            return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    
    return TestDataFactory


@pytest.fixture
def form_data():
    """Common form data for testing Django forms."""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password1": "ComplexPass123!",
        "password2": "ComplexPass123!",
        "first_name": "New",
        "last_name": "User",
    }


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis client for testing Celery/caching."""
    mock_redis_client = mocker.Mock()
    mock_redis_client.get.return_value = None
    mock_redis_client.set.return_value = True
    mock_redis_client.delete.return_value = True
    mock_redis_client.exists.return_value = False
    
    mocker.patch("redis.Redis", return_value=mock_redis_client)
    return mock_redis_client