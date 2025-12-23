import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from move_interfaces import move_interfaces, get_device

def test_move_interfaces():
    # Mock NetBox object
    nb = MagicMock()
    
    # Create dummy devices
    source_device = MagicMock()
    source_device.id = 1
    source_device.name = "Source-Switch"
    
    dest_device = MagicMock()
    dest_device.id = 2
    dest_device.name = "Dest-Switch"
    
    # Create dummy interfaces for source device
    intf1 = MagicMock()
    intf1.name = "Ethernet1"
    intf1.device = source_device
    
    intf2 = MagicMock()
    intf2.name = "Ethernet2"
    intf2.device = source_device
    
    # Mock filtering IP addresses (return empty list for simplicity)
    nb.ipam.ip_addresses.filter.return_value = []
    
    # Mock creating new interface
    new_intf = MagicMock()
    new_intf.id = 99
    nb.dcim.interfaces.create.return_value = new_intf

    # Mock filtering interfaces (return dummy interfaces)
    nb.dcim.interfaces.filter.return_value = [intf1, intf2]
    
    # Run the move function
    move_interfaces(nb, source_device, dest_device)
    
    # Assertions
    # 1. Filter was called for source device ID
    nb.dcim.interfaces.filter.assert_called_with(device_id=1)
    
    # 2. Verify new interfaces created on dest device
    assert nb.dcim.interfaces.create.call_count == 2
    # Check calls arguments if needed, e.g.:
    # nb.dcim.interfaces.create.assert_any_call(device=dest_device.id, name="Ethernet1", ...)
    
    # 3. Old interfaces deleted
    intf1.delete.assert_called_once()
    intf2.delete.assert_called_once()

def test_get_device_success():
    nb = MagicMock()
    mock_device = MagicMock()
    mock_device.name = "MyDevice"
    
    nb.dcim.devices.get.return_value = mock_device
    
    device = get_device(nb, "MyDevice")
    assert device == mock_device
    nb.dcim.devices.get.assert_called_with(name="MyDevice")

def test_get_device_fail():
    nb = MagicMock()
    nb.dcim.devices.get.return_value = None
    
    with pytest.raises(ValueError, match="Device 'Unknown' not found"):
        get_device(nb, "Unknown")
