import pynetbox
import sys
from os import getenv

# NetBox connection details
NETBOX_URL = getenv("NETBOX_URL")
API_TOKEN = getenv("NETBOX_TOKEN")

def get_netbox_api():
    if not NETBOX_URL or not API_TOKEN:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit(1)
    return pynetbox.api(url=NETBOX_URL, token=API_TOKEN)

def get_device(nb, device_name):
    """Retrieve a device by name."""
    device = nb.dcim.devices.get(name=device_name)
    if not device:
        print(f"Device '{device_name}' not found.")
        # sys.exit(1)  # Raised exception is better for testing than exit
        raise ValueError(f"Device '{device_name}' not found.")
    return device

def move_interfaces(nb, source_device, dest_device):
    """Move all interfaces from source device to destination device."""
    # Get all interfaces for the source device
    interfaces = nb.dcim.interfaces.filter(device_id=source_device.id)
    
    # Needs to be a list to check length
    interfaces_list = list(interfaces)

    if not interfaces_list:
        print(f"No interfaces found for device '{source_device.name}'.")
        return
    
    print(f"Found {len(interfaces_list)} interfaces to move from '{source_device.name}' to '{dest_device.name}'.")
    
    # Iterate through interfaces and update their device assignment
    for interface in interfaces_list:
        try:
            # NetBox does not allow moving components (interfaces) between devices directly.
            # We must create a new interface on the destination, move IPs, and delete the old one.
            
            print(f"Moving interface '{interface.name}'...")
            
            # 1. Create new interface on destination device
            new_intf = nb.dcim.interfaces.create(
                device=dest_device.id,
                name=interface.name,
                type=interface.type.value,
                description=interface.description,
                enabled=interface.enabled,
                mtu=interface.mtu,
                mac_address=interface.mac_address,
                mgmt_only=getattr(interface, "mgmt_only", False)
            )
            
            # 2. Re-assign IP addresses
            ips = nb.ipam.ip_addresses.filter(interface_id=interface.id)
            for ip in ips:
                ip.assigned_object_type = "dcim.interface"
                ip.assigned_object_id = new_intf.id
                ip.save()
                
            # 3. Delete old interface
            interface.delete()
            
            print(f"Successfully moved interface '{interface.name}' to '{dest_device.name}'.")
        except Exception as e:
            print(f"Failed to move interface '{interface.name}': {str(e)}")

def main():
    nb = get_netbox_api()
    # Prompt for device names
    source_device_name = input("Enter the source device name: ").strip()
    dest_device_name = input("Enter the destination device name: ").strip()
    
    # Validate device names
    if not source_device_name or not dest_device_name:
        print("Device names cannot be empty.")
        sys.exit(1)
    
    if source_device_name == dest_device_name:
        print("Source and destination devices cannot be the same.")
        sys.exit(1)
    
    try:
        # Get device objects
        source_device = get_device(nb, source_device_name)
        dest_device = get_device(nb, dest_device_name)
        
        # Confirm action
        print(f"\nThis will move all interfaces from '{source_device.name}' to '{dest_device.name}'.")
        confirm = input("Proceed? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Operation cancelled.")
            sys.exit(0)
        
        # Perform the interface move
        move_interfaces(nb, source_device, dest_device)
        print("\nInterface move operation completed.")
    except ValueError as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
  
