from dotenv import dotenv_values
import pynetbox
import sys
from time import sleep
from netboxlib import add_ipv6_ip
import urllib3

urllib3.disable_warnings()


def test_add_ip() -> None:
    config = dotenv_values("netbox.env")
    try:
        token = config["token"]
        url = config["url"]
    except KeyError as e:
        print(f"key missing from env file: {e}")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False
    subnet = "/29"
    for i in range(8):
        cidr = f"66.66.66.{i}{subnet}"
        ip_add_dict = dict(address=cidr, description="testing yadda")
        new_ip = nb.ipam.ip_addresses.create(ip_add_dict)
        print(f"new_ip = {new_ip}")

    sleep(5)

    cidr = f"66.66.66.0{subnet}"
    response = nb.ipam.ip_addresses.get(address=cidr)
    print(f"change the status for {cidr}")
    response.description = "more yadda"  # ok - I can change the description like this
    response.save()


def test_add_ipv6_ip():
    config = dotenv_values("netbox.env")
    try:
        token = config["token"]
        url = config["url"]
    except KeyError as e:
        print(f"key missing from env file: {e}")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False
    ipv6_ip = "1234:1234:1234::/127"
    rv = add_ipv6_ip(nb, ipv6_ip)
    print(rv)


if __name__ == "__main__":
    test_add_ipv6_ip()
