from os import getenv
import pynetbox
import sys
from time import sleep
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
            nb.ipam.ip_addresses.create(ip_add_dict)
        except pynetbox.RequestError as e:
            if "Duplicate IP address" in str(e):
                print(f"IP {cidr} already exists")
            else:
                raise e

    sleep(5)

    cidr = f"66.66.66.0{subnet}"
    response = nb.ipam.ip_addresses.get(address=cidr)
    print(f"change the status for {cidr}")
    response.description = "more yadda"  # ok - I can change the description like this
    response.save()


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


if __name__ == "__main__":
    test_add_ipv6_ip()
