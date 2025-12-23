from os import getenv
import pynetbox
import sys
import urllib3

urllib3.disable_warnings()


def nb_change_ip_desc(cidr: str, description: str) -> bool:
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")
    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    try:
        response = nb.ipam.ip_addresses.get(address=cidr)
        print(f"change the description for {cidr}")
        response.description = description
        response.save()
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False


if __name__ == "__main__":
    cidr = "66.66.66.1/29"
    desc = "This is a test"
    nb_change_ip_desc(cidr, desc)
    nb_change_ip_desc("66.66.66.2/29", "This is another test")
