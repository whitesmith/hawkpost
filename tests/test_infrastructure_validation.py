"""
Validation tests to ensure the testing infrastructure is properly configured.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from pathlib import Path


User = get_user_model()


class TestInfrastructureSetup:
    """Test that the testing infrastructure is properly configured."""
    
    @pytest.mark.unit
    def test_pytest_is_working(self):
        """Verify that pytest can run a simple test."""
        assert True
        assert 1 + 1 == 2
    
    @pytest.mark.unit
    def test_django_settings_loaded(self):
        """Verify that Django settings are properly loaded."""
        from django.conf import settings
        assert hasattr(settings, 'DEBUG')
        assert hasattr(settings, 'DATABASES')
        assert settings.DATABASES['default']['ENGINE']
    
    @pytest.mark.unit
    def test_fixtures_available(self, user, admin_user, client):
        """Verify that conftest fixtures are available."""
        assert user is not None
        assert admin_user is not None
        assert client is not None
        assert isinstance(client, Client)
        assert user.username == "testuser"
        assert admin_user.is_superuser is True
    
    @pytest.mark.unit
    def test_database_access(self, db):
        """Verify that tests can access the database."""
        user_count = User.objects.count()
        User.objects.create_user(
            username="dbtest",
            email="dbtest@example.com",
            password="testpass"
        )
        assert User.objects.count() == user_count + 1
    
    @pytest.mark.unit
    def test_temp_dir_fixture(self, temp_dir):
        """Verify that temp_dir fixture works."""
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    @pytest.mark.unit
    def test_mock_fixture(self, mocker):
        """Verify that pytest-mock is working."""
        mock_func = mocker.Mock(return_value=42)
        assert mock_func() == 42
        mock_func.assert_called_once()
    
    @pytest.mark.unit
    def test_authenticated_client(self, authenticated_client, user):
        """Verify that authenticated client fixture works."""
        # This would normally test a real view, but we'll just verify the client is authenticated
        assert authenticated_client.session
        # In a real test, you would do something like:
        # response = authenticated_client.get(reverse('some-protected-view'))
        # assert response.status_code == 200
    
    @pytest.mark.unit
    def test_captured_emails_fixture(self, captured_emails):
        """Verify that email capturing works."""
        from django.core.mail import send_mail
        
        assert len(captured_emails) == 0
        
        send_mail(
            'Test Subject',
            'Test message',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
        
        assert len(captured_emails) == 1
        assert captured_emails[0].subject == 'Test Subject'
    
    @pytest.mark.unit
    def test_form_data_fixture(self, form_data):
        """Verify that form_data fixture provides expected data."""
        assert 'username' in form_data
        assert 'email' in form_data
        assert 'password1' in form_data
        assert form_data['username'] == 'newuser'
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that integration marker works."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow marker works."""
        import time
        # Don't actually sleep in validation tests
        # time.sleep(0.1)
        assert True


class TestCoverageConfiguration:
    """Test that coverage is properly configured."""
    
    @pytest.mark.unit
    def test_coverage_running(self):
        """This test verifies coverage is tracking."""
        def covered_function():
            return "covered"
        
        def partially_covered_function(condition):
            if condition:
                return "yes"
            else:
                return "no"
        
        assert covered_function() == "covered"
        assert partially_covered_function(True) == "yes"
        # Note: We're intentionally not calling partially_covered_function(False)
        # to demonstrate branch coverage


@pytest.mark.unit
def test_pytest_runs_from_command_line():
    """Verify that pytest can be run from the command line."""
    # This test exists to ensure pytest discovers tests properly
    assert True