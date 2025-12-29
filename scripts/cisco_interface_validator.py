import pynetbox
import os

def is_canonical_cisco_name(name: str) -> bool:
    name = name.lower().replace(" ", "")
    canonical_patterns = [
        "gigabitethernet", "fastethernet", "tengigabitethernet",
        "hundredgige", "fortygige", "twentyfivegige", "fivieg",
        "ethernet", "loopback", "tunnel", "vlan", "port-channel",
        "nve", "null", "bdi", "dialer", "virtualport-channel"
    ]
    abbreviations = ["gi", "fa", "te", "tw", "hu", "fo", "et", "po", "vl"]
    for abbr in abbreviations:
        if name.startswith(abbr) and any(c.isdigit() for c in name[len(abbr):]):
            return False
    return any(name.startswith(pat) for pat in canonical_patterns)

# Config from environment variables
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
OFFENDERS_FILE = "offenders.txt"

if not NETBOX_URL or not NETBOX_TOKEN:
    raise ValueError("NETBOX_URL and NETBOX_TOKEN must be set in environment variables")

nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)
devices = nb.dcim.devices.filter(manufacturer="cisco")

offenders = []
for device in devices:
    interfaces = nb.dcim.interfaces.filter(device_id=device.id)
    for iface in interfaces:
        name = iface.name.strip()
        if not is_canonical_cisco_name(name):
            offenders.append((iface.id, name, device.name))

if offenders:
    with open(OFFENDERS_FILE, "w", encoding="utf-8") as f:
        f.write("ID\tInterface Name\tDevice Name\n")
        for iface_id, name, dev_name in offenders:
            f.write(f"{iface_id}\t{name}\t{dev_name}\n")
    print(f"Found {len(offenders)} offending interfaces. Written to {OFFENDERS_FILE}")
else:
    print("No offending interfaces found.")
