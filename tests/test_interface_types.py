
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils import netbox_interface_types

def test_interface_types_dict():
    # Verify the dictionary exists and has content
    assert isinstance(netbox_interface_types.interface_types, dict)
    assert len(netbox_interface_types.interface_types) > 0
    
    # Verify some key entries
    assert netbox_interface_types.interface_types["Virtual"] == "virtual"
    assert netbox_interface_types.interface_types["1000BASE-T"] == "1000base-t"
    
def test_interface_types_values():
    # Ensure all values are strings (slugs)
    for value in netbox_interface_types.interface_types.values():
        assert isinstance(value, str)
