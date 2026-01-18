"""Unit tests for credentials.py module."""
import sys
import os
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from credentials import (
    get_credentials,
    get_netbox_credentials,
    MissingCredentialsError,
    InvalidURLError,
)


class TestGetCredentials:
    """Test cases for get_credentials function."""

    @patch.dict(os.environ, {"ROUTER_USERNAME": "testuser", "ROUTER_PASSWORD": "testpass"})  # pragma: allowlist secret
    def test_get_credentials_success(self):
        """Test successful credential retrieval."""
        username, password = get_credentials()
        assert username == "testuser"
        assert password == "testpass"  # pragma: allowlist secret

    @patch.dict(os.environ, {"ROUTER_USERNAME": "  testuser  ", "ROUTER_PASSWORD": "  testpass  "}, clear=True)  # pragma: allowlist secret
    def test_get_credentials_strips_whitespace(self):
        """Test that credentials are stripped of whitespace."""
        username, password = get_credentials()
        assert username == "testuser"
        assert password == "testpass"  # pragma: allowlist secret

    @patch.dict(os.environ, {}, clear=True)
    def test_get_credentials_missing_username(self):
        """Test MissingCredentialsError when username is missing."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_credentials()
        assert "ROUTER_USERNAME" in str(exc_info.value)
        assert "ROUTER_PASSWORD" in str(exc_info.value)
        assert "ROUTER_USERNAME" in exc_info.value.env_vars

    @patch.dict(os.environ, {"ROUTER_USERNAME": "testuser"}, clear=True)
    def test_get_credentials_missing_password(self):
        """Test MissingCredentialsError when password is missing."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_credentials()
        assert "ROUTER_PASSWORD" in str(exc_info.value)
        assert "ROUTER_PASSWORD" in exc_info.value.env_vars

    @patch.dict(os.environ, {"ROUTER_USERNAME": "", "ROUTER_PASSWORD": "testpass"}, clear=True)  # pragma: allowlist secret
    def test_get_credentials_empty_username(self):
        """Test MissingCredentialsError when username is empty string."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_credentials()
        assert "ROUTER_USERNAME" in str(exc_info.value)

    @patch.dict(os.environ, {"ROUTER_USERNAME": "testuser", "ROUTER_PASSWORD": ""}, clear=True)  # pragma: allowlist secret
    def test_get_credentials_empty_password(self):
        """Test MissingCredentialsError when password is empty string."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_credentials()
        assert "ROUTER_PASSWORD" in str(exc_info.value)

    @patch.dict(os.environ, {"ROUTER_USERNAME": "   ", "ROUTER_PASSWORD": "testpass"}, clear=True)  # pragma: allowlist secret
    def test_get_credentials_whitespace_only_username(self):
        """Test MissingCredentialsError when username is only whitespace."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_credentials()
        assert "ROUTER_USERNAME" in str(exc_info.value)


class TestGetNetboxCredentials:
    """Test cases for get_netbox_credentials function."""

    @patch.dict(os.environ, {"NETBOX_URL": "https://netbox.example.com", "NETBOX_TOKEN": "test-token"})
    def test_get_netbox_credentials_success(self):
        """Test successful NetBox credential retrieval."""
        url, token = get_netbox_credentials()
        assert url == "https://netbox.example.com"
        assert token == "test-token"

    @patch.dict(os.environ, {"NETBOX_URL": "http://localhost:8000", "NETBOX_TOKEN": "dev-token"})
    def test_get_netbox_credentials_http_url(self):
        """Test NetBox credential retrieval with HTTP URL."""
        url, token = get_netbox_credentials()
        assert url == "http://localhost:8000"
        assert token == "dev-token"

    @patch.dict(os.environ, {"NETBOX_URL": "  https://netbox.example.com  ", "NETBOX_TOKEN": "  test-token  "})
    def test_get_netbox_credentials_strips_whitespace(self):
        """Test that NetBox credentials are stripped of whitespace."""
        url, token = get_netbox_credentials()
        assert url == "https://netbox.example.com"
        assert token == "test-token"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_netbox_credentials_missing_url(self):
        """Test MissingCredentialsError when NETBOX_URL is missing."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_netbox_credentials()
        assert "NETBOX_URL" in str(exc_info.value)
        assert "NETBOX_TOKEN" in str(exc_info.value)
        assert "NETBOX_URL" in exc_info.value.env_vars

    @patch.dict(os.environ, {"NETBOX_URL": "https://netbox.example.com"}, clear=True)
    def test_get_netbox_credentials_missing_token(self):
        """Test MissingCredentialsError when NETBOX_TOKEN is missing."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_netbox_credentials()
        assert "NETBOX_TOKEN" in str(exc_info.value)
        assert "NETBOX_TOKEN" in exc_info.value.env_vars

    @patch.dict(os.environ, {"NETBOX_URL": "", "NETBOX_TOKEN": "test-token"}, clear=True)
    def test_get_netbox_credentials_empty_url(self):
        """Test MissingCredentialsError when NETBOX_URL is empty string."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_netbox_credentials()
        assert "NETBOX_URL" in str(exc_info.value)

    @patch.dict(os.environ, {"NETBOX_URL": "https://netbox.example.com", "NETBOX_TOKEN": ""}, clear=True)
    def test_get_netbox_credentials_empty_token(self):
        """Test MissingCredentialsError when NETBOX_TOKEN is empty string."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_netbox_credentials()
        assert "NETBOX_TOKEN" in str(exc_info.value)

    @patch.dict(os.environ, {"NETBOX_URL": "invalid-url", "NETBOX_TOKEN": "test-token"})
    def test_get_netbox_credentials_invalid_url_format(self):
        """Test InvalidURLError when URL format is invalid."""
        with pytest.raises(InvalidURLError) as exc_info:
            get_netbox_credentials()
        assert "Invalid URL format" in str(exc_info.value)

    @patch.dict(os.environ, {"NETBOX_URL": "ftp://netbox.example.com", "NETBOX_TOKEN": "test-token"})
    def test_get_netbox_credentials_unsupported_scheme(self):
        """Test InvalidURLError when URL uses unsupported scheme."""
        with pytest.raises(InvalidURLError) as exc_info:
            get_netbox_credentials()
        assert "http or https scheme" in str(exc_info.value)

    @patch.dict(os.environ, {"NETBOX_URL": "https://", "NETBOX_TOKEN": "test-token"})
    def test_get_netbox_credentials_missing_netloc(self):
        """Test InvalidURLError when URL is missing netloc."""
        with pytest.raises(InvalidURLError) as exc_info:
            get_netbox_credentials()
        assert "Invalid URL format" in str(exc_info.value)

    @patch.dict(os.environ, {"NETBOX_URL": "://netbox.example.com", "NETBOX_TOKEN": "test-token"})
    def test_get_netbox_credentials_missing_scheme(self):
        """Test InvalidURLError when URL is missing scheme."""
        with pytest.raises(InvalidURLError) as exc_info:
            get_netbox_credentials()
        assert "Invalid URL format" in str(exc_info.value)

    @patch.dict(os.environ, {"NETBOX_URL": "   ", "NETBOX_TOKEN": "test-token"})
    def test_get_netbox_credentials_whitespace_only_url(self):
        """Test MissingCredentialsError when URL is only whitespace."""
        with pytest.raises(MissingCredentialsError) as exc_info:
            get_netbox_credentials()
        assert "NETBOX_URL" in str(exc_info.value)


class TestExceptionClasses:
    """Test exception classes."""

    def test_missing_credentials_error_with_env_vars(self):
        """Test MissingCredentialsError with env_vars list."""
        error = MissingCredentialsError("Test error", ["VAR1", "VAR2"])
        assert str(error) == "Test error"
        assert error.env_vars == ["VAR1", "VAR2"]

    def test_missing_credentials_error_without_env_vars(self):
        """Test MissingCredentialsError without env_vars list."""
        error = MissingCredentialsError("Test error")
        assert str(error) == "Test error"
        assert error.env_vars == []
