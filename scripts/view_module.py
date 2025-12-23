from os import getenv
import sys

# Initialize NetBox API client
token = getenv("NETBOX_TOKEN")
url = getenv("NETBOX_URL")

if not token or not url:
    print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
    sys.exit()

nb = pynetbox.api(
    url=url,
    token=token
)

# Get the device
device = nb.dcim.devices.get(name="switch1")
if not device:
    print("Device not found")
    exit()

# Get interfaces for the device
interfaces = nb.dcim.interfaces.filter(device_id=device.id)

# Print interfaces and their module association
for interface in interfaces:
    module_info = interface.module.display if interface.module else "None"
    print(f"Interface: {interface.name}, Module: {module_info}")
  
