from os import getenv
import pynetbox
import sys
from time import sleep
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from netbox_utils.netboxlib import add_ipv6_ip
import urllib3

urllib3.disable_warnings()


def test_add_ip() -> None:
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")
    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False
    subnet = "/29"
    for i in range(8):
        cidr = f"66.66.66.{i}{subnet}"
        ip_add_dict = dict(address=cidr, description="testing yadda")
        try:
            new_ip = nb.ipam.ip_addresses.create(ip_add_dict)
            print(f"Created IP {cidr}")

            # Immediately delete after verification to ensure test isolation
            # In a real scenario, you might want separate test/teardown phases
            new_ip.delete()
        except pynetbox.RequestError as e:
            if "Duplicate IP address" in str(e):
                print(f"IP {cidr} already exists, attempting cleanup")
                existing_ip = nb.ipam.ip_addresses.get(address=cidr)
                if existing_ip:
                    existing_ip.delete()
            else:
                raise e

    sleep(5)

    cidr = f"66.66.66.0{subnet}"

    # Re-create for modification test
    try:
        nb.ipam.ip_addresses.create(dict(address=cidr, description="temp"))
    except pynetbox.RequestError:
        pass  # Assume exists if failed

    response = nb.ipam.ip_addresses.get(address=cidr)
    if response:
        print(f"change the status for {cidr}")
        response.description = "more yadda"
        response.save()

        # Cleanup again
        response.delete()
    else:
        print(f"Failed to retrieve IP {cidr} for modification test")


def test_add_ipv6_ip():
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")
    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False
    ipv6_ip = "1234:1234:1234::/127"
    rv = add_ipv6_ip(nb, ipv6_ip)
    print(rv)

    # Cleanup
    if rv != "Failed" and rv != "IP Exists":
        # It's an IP object
        rv.delete()
    elif rv == "IP Exists":
        existing_ip = nb.ipam.ip_addresses.get(address=ipv6_ip)
        if existing_ip:
            existing_ip.delete()


if __name__ == "__main__":
    test_add_ipv6_ip()
