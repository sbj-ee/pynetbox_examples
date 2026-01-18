"""Credential helper for loading device credentials from environment variables."""
import os
from urllib.parse import urlparse
from loguru import logger


class MissingCredentialsError(Exception):
    """Raised when required credentials are missing from environment variables."""

    def __init__(self, message: str, env_vars: list[str] | None = None):
        """Initialize the exception with a message and optional list of missing env vars.

        Args:
            message: Error message describing what credentials are missing
            env_vars: Optional list of environment variable names that are missing
        """
        super().__init__(message)
        self.env_vars = env_vars or []


class InvalidURLError(Exception):
    """Raised when a URL has an invalid format."""

    pass


def get_credentials() -> tuple[str, str]:
    """Get username/password from environment variables.

    Returns:
        Tuple of (username, password)

    Raises:
        MissingCredentialsError: If required environment variables are not set or empty

    Environment variables:
        ROUTER_USERNAME, ROUTER_PASSWORD
    """
    username_var = "ROUTER_USERNAME"
    password_var = "ROUTER_PASSWORD"  # pragma: allowlist secret

    username = os.getenv(username_var)
    password = os.getenv(password_var)

    # Check for missing or empty credentials
    missing_vars = []
    if not username or not username.strip():
        missing_vars.append(username_var)
    if not password or not password.strip():
        missing_vars.append(password_var)

    if missing_vars:
        error_msg = (
            f"Missing or empty router credentials. "
            f"Please set the following environment variables: {', '.join(missing_vars)}"
        )
        logger.error(error_msg)
        raise MissingCredentialsError(error_msg, missing_vars)

    logger.debug("Successfully retrieved router credentials")
    return username.strip(), password.strip()


def get_netbox_credentials() -> tuple[str, str]:
    """Get NetBox URL and token from environment variables.

    Returns:
        Tuple of (url, token)

    Raises:
        MissingCredentialsError: If NETBOX_URL or NETBOX_TOKEN are not set or empty
        InvalidURLError: If NETBOX_URL has an invalid format
    """
    url = os.getenv("NETBOX_URL")
    token = os.getenv("NETBOX_TOKEN")

    # Check for missing or empty credentials
    missing_vars = []
    if not url or not url.strip():
        missing_vars.append("NETBOX_URL")
    if not token or not token.strip():
        missing_vars.append("NETBOX_TOKEN")

    if missing_vars:
        error_msg = (
            f"Missing or empty NetBox credentials. "
            f"Please set the following environment variables: {', '.join(missing_vars)}"
        )
        logger.error(error_msg)
        raise MissingCredentialsError(error_msg, missing_vars)

    url = url.strip()
    token = token.strip()

    # Validate URL format
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise InvalidURLError(
                f"Invalid URL format for NETBOX_URL: '{url}'. "
                f"Expected format: https://netbox.example.com"
            )
        if parsed.scheme not in ("http", "https"):
            raise InvalidURLError(
                f"NETBOX_URL must use http or https scheme. Got: '{parsed.scheme}'"
            )
    except Exception as e:
        if isinstance(e, InvalidURLError):
            raise
        logger.error(f"Failed to parse NETBOX_URL: {e}")
        raise InvalidURLError(f"Invalid URL format for NETBOX_URL: '{url}'") from e

    logger.debug("Successfully retrieved NetBox credentials")
    return url, token
