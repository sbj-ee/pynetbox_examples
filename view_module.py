import pynetbox

# Initialize NetBox API client
nb = pynetbox.api(
    url="https://netbox.example.com",
    token="your_api_token"
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
  
