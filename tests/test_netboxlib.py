
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from ipaddress import IPv4Interface

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils import netboxlib

@pytest.fixture
def mock_nb():
    return MagicMock()

def test_get_pynetbox_version(mock_nb):
    mock_nb.status.return_value = {"netbox-version": "3.5"}
    assert netboxlib.get_pynetbox_version(mock_nb) == "3.5"

def test_get_netbox_device_count(mock_nb):
    mock_nb.dcim.devices.count.return_value = 10
    assert netboxlib.get_netbox_device_count(mock_nb) == 10

def test_check_if_cidr_exists(mock_nb):
    mock_nb.ipam.ip_addresses.get.return_value = MagicMock()
    assert netboxlib.check_if_cidr_exists(mock_nb, "1.1.1.1/32") is True
    
    mock_nb.ipam.ip_addresses.get.return_value = None
    assert netboxlib.check_if_cidr_exists(mock_nb, "2.2.2.2/32") is False

def test_check_if_ip_exists(mock_nb):
    # Mocking get to return something only for specific call
    def side_effect(address):
        if address == "1.1.1.1/32":
            return MagicMock()
        return None
    mock_nb.ipam.ip_addresses.get.side_effect = side_effect
    
    assert netboxlib.check_if_ip_exists(mock_nb, "1.1.1.1") is True
    assert netboxlib.check_if_ip_exists(mock_nb, "2.2.2.2") is False

def test_get_cidr_from_ip(mock_nb):
    def side_effect(address):
        if address == "1.1.1.1/32":
            return MagicMock()
        return None
    mock_nb.ipam.ip_addresses.get.side_effect = side_effect
    
    assert netboxlib.get_cidr_from_ip(mock_nb, "1.1.1.1") == "1.1.1.1/32"
    assert netboxlib.get_cidr_from_ip(mock_nb, "2.2.2.2") is None

def test_get_all_ip_prefixes(mock_nb):
    netboxlib.get_all_ip_prefixes(mock_nb)
    mock_nb.ipam.prefixes.all.assert_called_once()

def test_add_ip_prefix(mock_nb):
    # First case: prefix exists
    mock_nb.ipam.prefixes.all.return_value = ["1.1.1.0/24"]
    assert netboxlib.add_ip_prefix(mock_nb, "1.1.1.0/24") is False
    
    # Second case: prefix does not exist
    mock_nb.ipam.prefixes.all.return_value = []
    assert netboxlib.add_ip_prefix(mock_nb, "2.2.2.0/24") is True
    mock_nb.ipam.prefixes.create.assert_called_with("2.2.2.0/24")

def test_check_if_device_name_exists(mock_nb):
    mock_nb.dcim.devices.get.return_value = MagicMock()
    assert netboxlib.check_if_device_name_exists(mock_nb, "Dev1") is True
    
    mock_nb.dcim.devices.get.return_value = None
    assert netboxlib.check_if_device_name_exists(mock_nb, "Dev2") is False

def test_get_site_id(mock_nb):
    mock_site = MagicMock()
    mock_site.id = 1
    mock_nb.dcim.sites.get.return_value = mock_site
    assert netboxlib.get_site_id(mock_nb, "Site1") == 1
    
    mock_nb.dcim.sites.get.return_value = None
    assert netboxlib.get_site_id(mock_nb, "Site2") == -1

def test_create_netbox_device(mock_nb):
    # Mock helpers inside netboxlib or just mock nb calls directly
    # Since get_device_type_id etc use nb calls, we can mock those return values
    
    # Mock type
    mock_type = MagicMock()
    mock_type.id = 10
    mock_nb.dcim.device_types.get.return_value = mock_type
    
    # Mock role
    mock_role = MagicMock()
    mock_role.id = 20
    mock_nb.dcim.device_roles.get.return_value = mock_role
    
    # Mock site
    mock_site = MagicMock()
    mock_site.id = 30
    mock_nb.dcim.sites.get.return_value = mock_site
    
    mock_nb.dcim.devices.create.return_value = "Created-Device"
    
    res = netboxlib.create_netbox_device(mock_nb, "DevName", "Site", "Type", "Role")
    assert res == "Created-Device"

def test_get_ip_status(mock_nb):
    mock_resp = MagicMock()
    mock_resp.status = "active"
    mock_nb.ipam.ip_addresses.get.return_value = mock_resp
    assert netboxlib.get_ip_status(mock_nb, "1.1.1.1/32") == "active"

def test_add_asn(mock_nb):
    mock_nb.ipam.asns.create.return_value = MagicMock()
    assert netboxlib.add_asn(mock_nb, 65000, "Desc") is True

def test_get_bgp_community_desc(mock_nb):
    mock_nb.plugins.bgp.community.get.return_value = {"description": "MyDesc"}
    assert netboxlib.get_bgp_community_desc(mock_nb, "65000:1") == "MyDesc"

def test_add_ipv4_ip(mock_nb):
    # Case: Exists
    mock_nb.ipam.ip_addresses.get.return_value = MagicMock()
    assert netboxlib.add_ipv4_ip(mock_nb, "1.1.1.1/32") == "IP Exists"
    
    # Case: New IP
    mock_nb.ipam.ip_addresses.get.return_value = None
    mock_nb.ipam.ip_addresses.create.return_value = "New-IP-Obj"
    assert netboxlib.add_ipv4_ip(mock_nb, "1.1.1.2/32") == "New-IP-Obj"

