"""Credential helper for loading device credentials from environment variables."""
import os
import sys


def get_credentials(service: str, environment: str = "prod") -> tuple[str, str]:
    """Get username/password from environment variables.

    Args:
        service: Service prefix (CISCO, NOKIA, VELOCIX, etc.)
        environment: Environment name (prod, lab)

    Returns:
        Tuple of (username, password)

    Environment variables format:
        {SERVICE}_{ENV}_USERNAME, {SERVICE}_{ENV}_PASSWORD
        Example: CISCO_PROD_USERNAME, CISCO_PROD_PASSWORD
    """
    env = environment.upper()
    svc = service.upper()
    username = os.getenv(f"{svc}_{env}_USERNAME")
    password = os.getenv(f"{svc}_{env}_PASSWORD")

    if not username or not password:
        print(f"Error: {svc}_{env}_USERNAME and {svc}_{env}_PASSWORD must be set")
        sys.exit(1)

    return username, password


def get_netbox_credentials() -> tuple[str, str]:
    """Get NetBox URL and token from environment variables."""
    url = os.getenv("NETBOX_URL")
    token = os.getenv("NETBOX_TOKEN")

    if not url or not token:
        print("Error: NETBOX_URL and NETBOX_TOKEN must be set")
        sys.exit(1)

    return url, token
