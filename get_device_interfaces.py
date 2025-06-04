import pynetbox
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# NetBox connection details
NETBOX_URL = os.getenv("NETBOX_URL", "http://localhost:8000")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN", "YOUR_TOKEN_HERE")
DEVICE_NAME = "your-device-name"  # Replace with your device name

def get_device_interfaces():
    try:
        # Initialize pynetbox API connection
        nb = pynetbox.api(
            url=NETBOX_URL,
            token=NETBOX_TOKEN
        )
        
        # Get the device by name
        device = nb.dcim.devices.get(name=DEVICE_NAME)
        
        if not device:
            print(f"Device '{DEVICE_NAME}' not found in NetBox")
            return
        
        # Get all interfaces for the device
        interfaces = nb.dcim.interfaces.filter(device_id=device.id)
        
        # Print interface details
        print(f"\nInterfaces for device '{DEVICE_NAME}':")
        print("-" * 50)
        
        for interface in interfaces:
            print(f"Interface: {interface.name}")
            print(f"  Type: {interface.type.value}")
            print(f"  Enabled: {interface.enabled}")
            print(f"  MAC Address: {interface.mac_address or 'N/A'}")
            print(f"  MTU: {interface.mtu or 'N/A'}")
            print(f"  Description: {interface.description or 'N/A'}")
            print("-" * 50)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    get_device_interfaces()
