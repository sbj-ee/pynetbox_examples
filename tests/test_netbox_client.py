import pytest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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


def test_check_if_device_name_exists(netbox_client):
    netbox_client.nb.dcim.devices.get.return_value = MagicMock()
    assert netbox_client.check_if_device_name_exists("Existing-Device") is True

    netbox_client.nb.dcim.devices.get.return_value = None
    assert netbox_client.check_if_device_name_exists("NonExistent") is False


def test_get_device_id(netbox_client):
    mock_device = MagicMock()
    mock_device.id = 55
    netbox_client.nb.dcim.devices.get.return_value = mock_device
    assert netbox_client.get_device_id("Device-A") == 55

    netbox_client.nb.dcim.devices.get.side_effect = Exception("Not found")
    assert netbox_client.get_device_id("Unknown") is None


def test_get_role_id(netbox_client):
    mock_role = MagicMock()
    mock_role.id = 10
    netbox_client.nb.dcim.device_roles.get.return_value = mock_role
    assert netbox_client.get_role_id("Role-A") == 10


def test_get_device_type_id(netbox_client):
    mock_type = MagicMock()
    mock_type.id = 20
    netbox_client.nb.dcim.device_types.get.return_value = mock_type
    assert netbox_client.get_device_type_id("Type-A") == 20


def test_get_interface_id(netbox_client):
    # Mock dependency
    netbox_client.get_device_id = MagicMock(return_value=100)

    mock_intf = MagicMock()
    mock_intf.id = 500
    netbox_client.nb.dcim.interfaces.get.return_value = mock_intf

    assert netbox_client.get_interface_id("Device-A", "Eth1") == 500
    netbox_client.nb.dcim.interfaces.get.assert_called_with(device_id=100, name="Eth1")


def test_add_interface_to_device(netbox_client):
    netbox_client.get_device_id = MagicMock(return_value=100)
    netbox_client.nb.dcim.interfaces.create.return_value = MagicMock()

    assert (
        netbox_client.add_interface_to_device("Eth1", "DevA", "virtual", "Desc") is True
    )
    netbox_client.nb.dcim.interfaces.create.assert_called()


def test_validate_ip_cidr(netbox_client):
    assert netbox_client.validate_ip_cidr("192.168.1.1/24") == "192.168.1.1/24"
    assert netbox_client.validate_ip_cidr("10.10.10.10/32") == "10.10.10.10/32"

    with pytest.raises(ValueError):
        netbox_client.validate_ip_cidr("invalid")


def test_add_ip_to_netbox(netbox_client):
    netbox_client.validate_ip_cidr = MagicMock(return_value="1.1.1.1/32")
    netbox_client.check_if_cidr_exists = MagicMock(return_value=False)

    mock_ip = MagicMock()
    netbox_client.nb.ipam.ip_addresses.create.return_value = mock_ip

    result = netbox_client.add_ip_to_netbox("1.1.1.1/32", "Desc", "Active")
    assert result == mock_ip


def test_add_ip_to_netbox_exists(netbox_client):
    netbox_client.validate_ip_cidr = MagicMock(return_value="1.1.1.1/32")
    netbox_client.check_if_cidr_exists = MagicMock(return_value=True)

    assert netbox_client.add_ip_to_netbox("1.1.1.1/32", "Desc", "Active") is None


def test_get_circuit_id(netbox_client):
    netbox_client.get_device_id = MagicMock(return_value=100)

    mock_peer = MagicMock()
    mock_peer.circuit.id = 999

    mock_intf = MagicMock()
    mock_intf.link_peers = [mock_peer]

    netbox_client.nb.dcim.interfaces.get.return_value = mock_intf

    assert netbox_client.get_circuit_id("Dev", "Intf") == 999


def test_get_ipaddress_id(netbox_client):
    mock_ip = MagicMock()
    mock_ip.id = 88
    netbox_client.nb.ipam.ip_addresses.get.return_value = mock_ip
    assert netbox_client.get_ipaddress_id("1.1.1.1") == 88


def test_get_as_id(netbox_client):
    mock_asn = MagicMock()
    mock_asn.id = 77
    netbox_client.nb.ipam.asns.get.return_value = mock_asn
    assert netbox_client.get_as_id(65000) == 77


def test_add_bgp_session(netbox_client):
    netbox_client.get_as_id = MagicMock(return_value=1)
    netbox_client.get_ipaddress_id = MagicMock(return_value=2)
    netbox_client.get_device_id = MagicMock(return_value=3)
    netbox_client.get_site_id = MagicMock(return_value=4)

    mock_session = {"name": "BGP-Session"}
    netbox_client.nb.plugins.bgp.session.create.return_value = mock_session

    res = netbox_client.add_bgp_session(
        "Site", 65001, "1.1.1.1", 65000, "1.1.1.2", "Dev", "Name", "Active"
    )
    assert res["name"] == "BGP-Session"


def test_get_bgp_sessions_all(netbox_client):
    mock_list = [MagicMock(), MagicMock()]
    netbox_client.nb.plugins.bgp.session.all.return_value = mock_list
    assert len(netbox_client.get_bgp_sessions_all()) == 2


def test_get_bgp_session_by_device_and_address(netbox_client):
    mock_session = MagicMock()
    mock_session.id = 123

    # Mocking a list iterator return
    netbox_client.nb.plugins.bgp.session.filter.return_value = iter([mock_session])

    res = netbox_client.get_bgp_session_by_device_and_address("Dev", "1.1.1.1")
    assert res.id == 123


def test_get_circuit(netbox_client):
    netbox_client.get_circuit_id = MagicMock(return_value=555)
    mock_circuit = {"cid": "Circuit-123"}
    netbox_client.nb.circuits.circuits.get.return_value = mock_circuit

    res = netbox_client.get_circuit("Dev", "Intf")
    assert res["cid"] == "Circuit-123"


def test_add_ip_to_interface(netbox_client):
    netbox_client.get_interface_id = MagicMock(return_value=101)
    netbox_client.nb.ipam.ip_addresses.create.return_value = MagicMock()

    assert (
        netbox_client.add_ip_to_interface("Dev", "Intf", "1.1.1.1/32", "active", "Desc")
        is True
    )
    netbox_client.nb.ipam.ip_addresses.create.assert_called()
