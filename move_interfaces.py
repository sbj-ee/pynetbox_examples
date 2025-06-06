import pynetbox
import getpass

# NetBox connection details
NETBOX_URL = "http://your-netbox-url"  # Replace with your NetBox URL
API_TOKEN = "your-api-token"  # Replace with your NetBox API token

# Initialize pynetbox API
nb = pynetbox.api(url=NETBOX_URL, token=API_TOKEN)

def get_device(device_name):
    """Retrieve a device by name."""
    device = nb.dcim.devices.get(name=device_name)
    if not device:
        print(f"Device '{device_name}' not found.")
        exit(1)
    return device

def move_interfaces(source_device, dest_device):
    """Move all interfaces from source device to destination device."""
    # Get all interfaces for the source device
    interfaces = nb.dcim.interfaces.filter(device_id=source_device.id)
    
    if not interfaces:
        print(f"No interfaces found for device '{source_device.name}'.")
        return
    
    print(f"Found {len(list(interfaces))} interfaces to move from '{source_device.name}' to '{dest_device.name}'.")
    
    # Iterate through interfaces and update their device assignment
    for interface in interfaces:
        try:
            interface.device = dest_device
            interface.save()
            print(f"Successfully moved interface '{interface.name}' to '{dest_device.name}'.")
        except Exception as e:
            print(f"Failed to move interface '{interface.name}': {str(e)}")

def main():
    # Prompt for device names
    source_device_name = input("Enter the source device name: ").strip()
    dest_device_name = input("Enter the destination device name: ").strip()
    
    # Validate device names
    if not source_device_name or not dest_device_name:
        print("Device names cannot be empty.")
        exit(1)
    
    if source_device_name == dest_device_name:
        print("Source and destination devices cannot be the same.")
        exit(1)
    
    # Get device objects
    source_device = get_device(source_device_name)
    dest_device = get_device(dest_device_name)
    
    # Confirm action
    print(f"\nThis will move all interfaces from '{source_device.name}' to '{dest_device.name}'.")
    confirm = input("Proceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Operation cancelled.")
        exit(0)
    
    # Perform the interface move
    move_interfaces(source_device, dest_device)
    print("\nInterface move operation completed.")

if __name__ == "__main__":
    main()
  
