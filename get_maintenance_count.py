import os
import pynetbox
import urllib3

urllib3.disable_warnings()

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)
nb.http_session.verify = False

# Fast filtered queries for large environments
devices = list(nb.dcim.devices.filter(cf_Maintenance=True))
circuits = list(nb.circuits.circuits.filter(cf_Maintenance=True))
interfaces = list(nb.dcim.interfaces.filter(cf_Maintenance=True))

print(f"Devices in maintenance: {len(devices)}")
print(f"Circuits in maintenance: {len(circuits)}")
print(f"Interfaces in maintenance: {len(interfaces)}")
