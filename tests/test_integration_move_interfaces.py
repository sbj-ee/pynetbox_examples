import pytest
import pynetbox
import sys
import os
import uuid

# Add scripts dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
# Add root dir to path for netbox_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from move_interfaces import move_interfaces, get_device
from netbox_utils.netboxlib import connect_netbox

# Helper to generate unique names
def uniq(prefix):
    return f"{prefix}-{str(uuid.uuid4())[:8]}"

@pytest.fixture(scope="module")
def nb_connection():
    return connect_netbox()

@pytest.fixture(scope="module")
def setup_netbox_data(nb_connection):
    """
    Creates dependencies: Site, Manufacturer, Device Type, Device Role
    """
    nb = nb_connection
    
    # Create unique names
    site_name = uniq("TestSite")
    mfr_name = uniq("TestMfr")
    dtype_name = uniq("TestType")
    role_name = uniq("TestRole")
    
    # 1. Create Site
    site = nb.dcim.sites.create(name=site_name, slug=site_name.lower())
    
    # 2. Create Manufacturer
    mfr = nb.dcim.manufacturers.create(name=mfr_name, slug=mfr_name.lower())
    
    # 3. Create Device Type
    dtype = nb.dcim.device_types.create(
        manufacturer=mfr.id, 
        model=dtype_name, 
        slug=dtype_name.lower()
    )
    
    # 4. Create Device Role
    role = nb.dcim.device_roles.create(name=role_name, slug=role_name.lower())
    
    data = {
        "site": site,
        "manufacturer": mfr,
        "device_type": dtype,
        "device_role": role
    }
    
    yield data
    
    # Cleanup (reverse order)
    # Note: Devices must be deleted before these can be deleted, handled in test function cleanup
    try:
        nb.dcim.device_roles.delete([role.id])
        nb.dcim.device_types.delete([dtype.id])
        nb.dcim.manufacturers.delete([mfr.id])
        nb.dcim.sites.delete([site.id])
    except Exception as e:
        print(f"Cleanup failed for setup data: {e}")

def test_integration_move_interfaces(nb_connection, setup_netbox_data):
    nb = nb_connection
    data = setup_netbox_data
    
    dev_a_name = uniq("DeviceA")
    dev_b_name = uniq("DeviceB")
    
    # Create 2 Devices
    dev_a = nb.dcim.devices.create(
        name=dev_a_name,
        device_type=data["device_type"].id,
        role=data["device_role"].id,
        site=data["site"].id
    )
    
    dev_b = nb.dcim.devices.create(
        name=dev_b_name,
        device_type=data["device_type"].id,
        role=data["device_role"].id,
        site=data["site"].id
    )
    
    created_devices = [dev_a, dev_b]
    
    try:
        # Create Interfaces on Device A
        # Note: Depending on NetBox version/settings, creation might need generic types
        intf1 = nb.dcim.interfaces.create(device=dev_a.id, name="Eth1", type="virtual")
        intf2 = nb.dcim.interfaces.create(device=dev_a.id, name="Eth2", type="virtual")
        
        # Verify creation
        current_a_intfs = list(nb.dcim.interfaces.filter(device_id=dev_a.id))
        assert len(current_a_intfs) == 2
        
        current_b_intfs = list(nb.dcim.interfaces.filter(device_id=dev_b.id))
        assert len(current_b_intfs) == 0
        
        # --- Perform the Move ---
        print(f"Moving interfaces from {dev_a.name} to {dev_b.name}")
        move_interfaces(nb, dev_a, dev_b)
        
        # --- Verify Results ---
        # 1. Device A should have 0 interfaces
        final_a_intfs = list(nb.dcim.interfaces.filter(device_id=dev_a.id))
        assert len(final_a_intfs) == 0
        
        # 2. Device B should have 2 interfaces
        final_b_intfs = list(nb.dcim.interfaces.filter(device_id=dev_b.id))
        assert len(final_b_intfs) == 2
        assert {i.name for i in final_b_intfs} == {"Eth1", "Eth2"}
        
        print("Integration test successful!")
        
    finally:
        # cleanup devices (interfaces delete cascade usually? no, they are components)
        # interfaces delete with device usually
        for dev in created_devices:
            try:
                d = nb.dcim.devices.get(dev.id)
                if d:
                    d.delete()
            except Exception as e:
                print(f"Failed to delete device {dev.name}: {e}")
