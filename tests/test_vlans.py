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
    return NetboxClient(url="http://mock-netbox", token="mock-token")


# --- Tests ---


def test_get_vlan_group_id(netbox_client):
    mock_group = MagicMock()
    mock_group.id = 10

    # Mock filtering returning a list with one item
    netbox_client.nb.ipam.vlan_groups.filter.return_value = [mock_group]

    group_id = netbox_client.get_vlan_group_id("Test-Group")
    assert group_id == 10


def test_get_vlan_group_id_not_found(netbox_client):
    # Mock filtering returning empty list
    netbox_client.nb.ipam.vlan_groups.filter.return_value = []

    group_id = netbox_client.get_vlan_group_id("NonExistent-Group")
    assert group_id is None


def test_add_vlan_group(netbox_client):
    netbox_client.get_site_id = MagicMock(return_value=5)

    mock_group = {"name": "Test-Group", "id": 10, "slug": "test-group"}
    netbox_client.nb.ipam.vlan_groups.create.return_value = mock_group

    result = netbox_client.add_vlan_group("Test-Group", "test-group", "Test-Site")

    assert result["name"] == "Test-Group"
    netbox_client.nb.ipam.vlan_groups.create.assert_called_with(
        name="Test-Group",
        slug="test-group",
        description="",
        scope_type="dcim.site",
        scope_id=5,
    )


def test_add_vlan(netbox_client):
    netbox_client.get_site_id = MagicMock(return_value=50)
    netbox_client.get_vlan_group_id = MagicMock(return_value=12)

    mock_vlan = {"name": "User-VLAN", "vid": 100, "id": 999}
    netbox_client.nb.ipam.vlans.create.return_value = mock_vlan

    result = netbox_client.add_vlan(100, "User-VLAN", "My-Site", "My-Group")

    assert result["vid"] == 100
    netbox_client.nb.ipam.vlans.create.assert_called_with(
        vid=100, name="User-VLAN", status="active", description="", site=50, group=12
    )


def test_add_vlan_failure(netbox_client):
    netbox_client.nb.ipam.vlans.create.side_effect = Exception("API Error")

    result = netbox_client.add_vlan(100, "User-VLAN")
    assert result is None
