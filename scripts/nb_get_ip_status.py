from os import getenv
import pynetbox
import sys
import urllib3

urllib3.disable_warnings()


def nb_get_ip_status(cidr: str) -> str:
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")
    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    try:
        response = nb.ipam.ip_addresses.get(address=cidr)
        return response.status
    except Exception as e:
        print(f"Exception: {e}")
        return "Unknown"


if __name__ == "__main__":
    cidr = "66.66.66.1/29"
    desc = "This is a test"
    status = nb_get_ip_status(cidr)
    print(status)
