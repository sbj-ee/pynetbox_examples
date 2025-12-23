import os
import pynetbox
import urllib3

urllib3.disable_warnings()

NETBOX_URL = os.getenv('NETBOX_URL')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN')

def get_interface_id(device_name: str, interface_name: str) -> int | None:
    nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)
    nb.http_session.verify = False
    interface = nb.dcim.interfaces.get(device=device_name, name=interface_name)
    return interface.id if interface else None

# Example usage:
if __name__ == "__main__":
    print(get_interface_id("CCW383XAcen13", "Ethernet1/37"))
