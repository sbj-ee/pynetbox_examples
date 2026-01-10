"""Integration tests for NetBox connectivity using real credentials.

These tests require a live NetBox instance and valid credentials.
Set NETBOX_URL and NETBOX_TOKEN environment variables before running.

Run with: pytest tests/test_integration_netbox.py -v
"""
import sys
import os
import pytest
import pynetbox
import urllib3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from credentials import get_netbox_credentials, MissingCredentialsError

urllib3.disable_warnings()


# Skip all tests if credentials are not available
def credentials_available():
    """Check if NetBox credentials are available."""
    try:
        get_netbox_credentials()
        return True
    except MissingCredentialsError:
        return False


pytestmark = pytest.mark.skipif(
    not credentials_available(),
    reason="NetBox credentials not available (NETBOX_URL, NETBOX_TOKEN)"
)


@pytest.fixture
def netbox_api():
    """Create a NetBox API connection using credentials from environment."""
    url, token = get_netbox_credentials()
    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False
    return nb


class TestNetboxConnectivity:
    """Test NetBox API connectivity and basic operations."""

    def test_get_netbox_credentials_returns_valid_credentials(self):
        """Test that get_netbox_credentials returns the expected format."""
        url, token = get_netbox_credentials()
        assert url is not None
        assert token is not None
        assert url.startswith(("http://", "https://"))
        assert len(token) > 0

    def test_netbox_api_connection(self, netbox_api):
        """Test that we can connect to NetBox API."""
        status = netbox_api.status()
        assert "netbox-version" in status
        assert "python-version" in status

    def test_netbox_version(self, netbox_api):
        """Test that NetBox version is retrievable."""
        status = netbox_api.status()
        version = status["netbox-version"]
        assert version is not None
        # Version should be in format X.Y.Z
        parts = version.split(".")
        assert len(parts) >= 2

    def test_list_sites(self, netbox_api):
        """Test listing sites from NetBox."""
        sites = list(netbox_api.dcim.sites.all())
        # Just verify we can list sites, don't assume any exist
        assert isinstance(sites, list)

    def test_list_devices(self, netbox_api):
        """Test listing devices from NetBox."""
        devices = list(netbox_api.dcim.devices.all())
        assert isinstance(devices, list)

    def test_list_ip_addresses(self, netbox_api):
        """Test listing IP addresses from NetBox."""
        ips = list(netbox_api.ipam.ip_addresses.all())
        assert isinstance(ips, list)

    def test_list_prefixes(self, netbox_api):
        """Test listing prefixes from NetBox."""
        prefixes = list(netbox_api.ipam.prefixes.all())
        assert isinstance(prefixes, list)

    def test_list_vlans(self, netbox_api):
        """Test listing VLANs from NetBox."""
        vlans = list(netbox_api.ipam.vlans.all())
        assert isinstance(vlans, list)

    def test_list_device_types(self, netbox_api):
        """Test listing device types from NetBox."""
        device_types = list(netbox_api.dcim.device_types.all())
        assert isinstance(device_types, list)

    def test_list_manufacturers(self, netbox_api):
        """Test listing manufacturers from NetBox."""
        manufacturers = list(netbox_api.dcim.manufacturers.all())
        assert isinstance(manufacturers, list)


class TestNetboxDataIntegrity:
    """Test data integrity in NetBox responses."""

    def test_site_has_required_fields(self, netbox_api):
        """Test that sites have required fields."""
        sites = list(netbox_api.dcim.sites.all())
        if sites:
            site = sites[0]
            assert hasattr(site, "id")
            assert hasattr(site, "name")
            assert hasattr(site, "slug")

    def test_device_has_required_fields(self, netbox_api):
        """Test that devices have required fields."""
        devices = list(netbox_api.dcim.devices.all())
        if devices:
            device = devices[0]
            assert hasattr(device, "id")
            assert hasattr(device, "name")
            assert hasattr(device, "device_type")

    def test_ip_address_has_required_fields(self, netbox_api):
        """Test that IP addresses have required fields."""
        ips = list(netbox_api.ipam.ip_addresses.all())
        if ips:
            ip = ips[0]
            assert hasattr(ip, "id")
            assert hasattr(ip, "address")
            assert hasattr(ip, "status")
