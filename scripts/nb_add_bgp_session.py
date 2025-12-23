import pynetbox

# establish your netbox connection
#

# assuming you have a connection, the following are the raw steps
rir = nb.ipam.rirs.get("rir="ARIN")

local_as = nb.ipam.asns.get(asn=4181)
remote_as = nb.ipam.asns.get(asn=852)
local_ip = nb.ipam.ip_addresses.get("64.50.224.10/31")
remote_ip = nb.ipam.ip_addresses.get("64.50.224.11/31")
device = nb.dcim.devices.get("CHCGILDTcor51")
session_info = {"name": "Test", "description": "Test", "comments": "Test", "local_as": local_as.id, "remote_as": remote_as.id, "device": device.id, "local_address": local_ip.id, "remote_address": remote_ip.id,}
nb.plugins.bgp.session.create(session_info)
