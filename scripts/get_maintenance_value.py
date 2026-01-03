import os
import pynetbox
import urllib3

urllib3.disable_warnings()

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)
nb.http_session.verify = False


def get_maintenance(obj):
    return obj.custom_fields.get("Maintenance", False) if obj.custom_fields else False


# Examples:
devices = nb.dcim.devices.all()
for dev in devices:
    print(f"Device {dev.name}: Maintenance = {get_maintenance(dev)}")

circuits = nb.circuits.circuits.all()
for circuit in circuits:
    print(f"Circuit {circuit.cid}: Maintenance = {get_maintenance(circuit)}")

interfaces = nb.dcim.interfaces.all()
for iface in interfaces:
    print(
        f"Interface {iface.device.name}/{iface.name}: Maintenance = {get_maintenance(iface)}"
    )
