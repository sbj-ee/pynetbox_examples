
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

def test_delete_netbox_device(mock_nb):
    # Found
    mock_dev = MagicMock()
    mock_nb.dcim.devices.get.return_value = mock_dev
    assert netboxlib.delete_netbox_device(mock_nb, "Dev1") is True
    mock_dev.delete.assert_called_once()
    
    # Not found
    mock_nb.dcim.devices.get.return_value = None
    assert netboxlib.delete_netbox_device(mock_nb, "Dev2") is False

def test_change_ip_status(mock_nb):
    mock_ip = MagicMock()
    mock_nb.ipam.ip_addresses.get.return_value = mock_ip
    assert netboxlib.change_ip_status(mock_nb, "1.1.1.1/32", "active") is True
    assert mock_ip.status == "active"
    mock_ip.save.assert_called()

def test_change_ip_desc(mock_nb):
    mock_ip = MagicMock()
    mock_nb.ipam.ip_addresses.get.return_value = mock_ip
    assert netboxlib.change_ip_desc(mock_nb, "1.1.1.1/32", "Desc") is True
    assert mock_ip.description == "Desc"
    mock_ip.save.assert_called()

def test_check_asn_exists(mock_nb):
    mock_nb.ipam.asns.get.return_value = MagicMock()
    assert netboxlib.check_asn_exists(mock_nb, 65000) is True
    
    mock_nb.ipam.asns.get.return_value = None
    assert netboxlib.check_asn_exists(mock_nb, 65999) is False

def test_delete_asn(mock_nb):
    mock_asn = MagicMock()
    mock_nb.ipam.asns.get.return_value = mock_asn
    mock_nb.ipam.asns.delete.return_value = True
    assert netboxlib.delete_asn(mock_nb, 65000) is True
    
    mock_nb.ipam.asns.get.return_value = None
    assert netboxlib.delete_asn(mock_nb, 65999) is False

def test_add_contact(mock_nb):
    mock_nb.tenancy.contacts.create.return_value = True
    assert netboxlib.add_contact(mock_nb, "Contact1") is True

def test_get_all_bgp_communities(mock_nb):
    c1 = MagicMock()
    c1.description = "Desc1"
    # Need to make sure c1 works as a dict key or mock logic appropriately
    # The code does: bgp_community_dict[community] = community.description
    # So community object must be hashable. MagicMock is hashable.
    mock_nb.plugins.bgp.community.all.return_value = [c1]
    
    res = netboxlib.get_all_bgp_communities(mock_nb)
    assert len(res) == 1
    assert res[c1] == "Desc1"

def test_add_bgp_community(mock_nb):
    netboxlib.add_bgp_community(mock_nb, "65000:100", "Desc")
    mock_nb.plugins.bgp.community.create.assert_called_with(value="65000:100", description="Desc")

def test_add_ipv6_ip(mock_nb):
    # Exists
    mock_nb.ipam.ip_addresses.get.return_value = MagicMock()
    assert netboxlib.add_ipv6_ip(mock_nb, "2001:db8::1/64") == "IP Exists"
    
    # New
    mock_nb.ipam.ip_addresses.get.return_value = None
    mock_nb.ipam.ip_addresses.create.return_value = "New-IPv6"
    assert netboxlib.add_ipv6_ip(mock_nb, "2001:db8::2/64") == "New-IPv6"

def test_get_ip_device_info(mock_nb):
    # Setup a complex mock object to hit the print statements
    mock_res = MagicMock()
    mock_res.id = 1
    mock_res.url = "http://url"
    mock_res.display = "Display"
    mock_res.family.value = 4
    mock_res.family.label = "IPv4"
    mock_res.description = "Desc"
    mock_res.created = "2023-01-01"
    mock_res.last_updated = "2023-01-02"
    mock_res.dns_name = "dns"
    mock_res.tags = ["tag"]
    
    mock_assigned = MagicMock()
    mock_assigned.url = "http://assigned"
    mock_assigned.id = 2
    mock_assigned.display = "AssignedDisplay"
    
    mock_device = MagicMock()
    mock_device.id = 3
    mock_device.name = "DeviceName"
    mock_device.url = "http://device"
    mock_device.display = "DeviceDisplay"
    
    # Link them
    mock_assigned.device = mock_device
    mock_res.assigned_object = mock_assigned
    
    mock_nb.ipam.ip_addresses.get.return_value = mock_res
    mock_nb.dcim.devices.get.return_value = {"name": "DeviceName"}
    
    # Run function
    assert netboxlib.get_ip_device_info(mock_nb, "1.1.1.1") is True
