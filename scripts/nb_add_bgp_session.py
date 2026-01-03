import pynetbox
from os import getenv

# establish your netbox connection
NETBOX_URL = getenv("NETBOX_URL")
NETBOX_TOKEN = getenv("NETBOX_TOKEN")

if not NETBOX_URL or not NETBOX_TOKEN:
    raise ValueError("NETBOX_URL and NETBOX_TOKEN must be set in environment variables")

nb = pynetbox.api(url=NETBOX_URL, token=NETBOX_TOKEN)

# assuming you have a connection, the following are the raw steps
rir = nb.ipam.rirs.get(rir="ARIN")

local_as = nb.ipam.asns.get(asn=4181)
remote_as = nb.ipam.asns.get(asn=852)
local_ip = nb.ipam.ip_addresses.get("64.50.224.10/31")
remote_ip = nb.ipam.ip_addresses.get("64.50.224.11/31")
device = nb.dcim.devices.get("CHCGILDTcor51")
session_info = {
    "name": "Test",
    "description": "Test",
    "comments": "Test",
    "local_as": local_as.id,
    "remote_as": remote_as.id,
    "device": device.id,
    "local_address": local_ip.id,
    "remote_address": remote_ip.id,
}
nb.plugins.bgp.session.create(session_info)
