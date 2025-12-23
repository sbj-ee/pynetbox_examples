import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from os import getenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils.NetboxClient import NetboxClient

# --- Fixtures ---

@pytest.fixture
def mock_pynetbox_api():
    with patch("pynetbox.api") as mock_api:
        yield mock_api

@pytest.fixture
def netbox_client(mock_pynetbox_api):
    # Mock credentials are fine since we are mocking the pynetbox connection
    return NetboxClient(url="http://mock-netbox", token="mock-token")

# --- Tests ---

def test_instantiation(netbox_client):
    assert netbox_client.url == "http://mock-netbox"
    assert netbox_client.token == "mock-token"
    assert netbox_client.nb is not None

def test_get_pynetbox_version(netbox_client):
    # Setup mock return
    netbox_client.nb.status.return_value = {"netbox-version": "3.5.0"}
    
    version = netbox_client.get_pynetbox_version()
    assert version == "3.5.0"

def test_check_if_cidr_exists_found(netbox_client):
    # Mock finding an IP
    netbox_client.nb.ipam.ip_addresses.get.return_value = MagicMock()
    
    exists = netbox_client.check_if_cidr_exists("192.168.1.1/24")
    assert exists is True

def test_check_if_cidr_exists_not_found(netbox_client):
    # Mock NOT finding an IP
    netbox_client.nb.ipam.ip_addresses.get.return_value = None
    
    exists = netbox_client.check_if_cidr_exists("192.168.1.1/24")
    assert exists is False

def test_get_cidr_from_ip_found(netbox_client):
    # Mock logic: only return true when the specific loop iteration hits /24
    def side_effect(address):
        if address == "192.168.1.1/24":
            return MagicMock()
        return None
        
    netbox_client.nb.ipam.ip_addresses.get.side_effect = side_effect
    
    cidr = netbox_client.get_cidr_from_ip("192.168.1.1")
    assert cidr == "192.168.1.1/24"

def test_get_site_id(netbox_client):
    mock_site = MagicMock()
    mock_site.id = 123
    netbox_client.nb.dcim.sites.get.return_value = mock_site
    
    site_id = netbox_client.get_site_id("Test-Site")
    assert site_id == 123

def test_get_site_id_not_found(netbox_client):
    netbox_client.nb.dcim.sites.get.side_effect = Exception("Not found")
    
    site_id = netbox_client.get_site_id("Invalid-Site")
    assert site_id is None

def test_add_device(netbox_client):
    # Mock dependencies
    netbox_client.get_device_type_id = MagicMock(return_value=1)
    netbox_client.get_role_id = MagicMock(return_value=2)
    netbox_client.get_site_id = MagicMock(return_value=3)
    
    # Mock return value to be a dictionary, which dict() handles natively
    mock_created_device = {"name": "New-Device", "id": 100}
    netbox_client.nb.dcim.devices.create.return_value = mock_created_device
    
    device = netbox_client.add_device("Site", "New-Device", "Role", "Type")
    assert device["name"] == "New-Device"
