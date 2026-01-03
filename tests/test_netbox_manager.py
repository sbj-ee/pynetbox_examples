import pytest
import sys
import os
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from netbox_utils.netbox_manager import NetboxManager


@pytest.fixture
def mock_pynetbox_api():
    with patch("pynetbox.api") as mock_api:
        yield mock_api


@pytest.fixture
def manager(mock_pynetbox_api):
    return NetboxManager(url="http://mock", token="token")


def test_init(mock_pynetbox_api):
    mgr = NetboxManager("http://url", "token", ssl_verify=False)
    mock_pynetbox_api.assert_called_with("http://url", token="token")
    assert mgr.nb.http_session.verify is False


def test_add_site(manager):
    mock_site = {"name": "Site1", "id": 10}
    manager.nb.dcim.sites.create.return_value = mock_site

    res = manager.add_site("Site1", "site1")
    assert res["name"] == "Site1"
    manager.nb.dcim.sites.create.assert_called()


def test_add_device(manager):
    mock_dev = {"name": "Dev1", "id": 20}
    manager.nb.dcim.devices.create.return_value = mock_dev

    res = manager.add_device("Dev1", 1, 2, 3)
    assert res["name"] == "Dev1"
    manager.nb.dcim.devices.create.assert_called()


def test_add_interface(manager):
    mock_intf = {"name": "Eth0", "id": 30}
    manager.nb.dcim.interfaces.create.return_value = mock_intf

    res = manager.add_interface(20, "Eth0")
    assert res["name"] == "Eth0"


def test_add_ip_address(manager):
    mock_ip = {"address": "1.1.1.1/24", "id": 40}
    manager.nb.ipam.ip_addresses.create.return_value = mock_ip

    res = manager.add_ip_address("1.1.1.1/24", 30)
    assert res["address"] == "1.1.1.1/24"
