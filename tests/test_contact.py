from os import getenv
import pynetbox
import sys
from pprint import pprint
from time import sleep
import urllib3

urllib3.disable_warnings()


def test_add_contact() -> None:
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")

    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    contact_name: str = "Bob Dole"

    rv = nb.tenancy.contacts.create(name=contact_name)

    if rv:
        assert True
    else:
        assert False


def test_modify_contact():
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")

    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    contact_name: str = "Bob Dole"

    contact_ref = nb.tenancy.contacts.get(name=contact_name)
    contact_ref.title = "Miner yabba dabba do"
    contact_ref.save()


def test_delete_contact():
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")

    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    contact_name: str = "Bob Dole"

    contact_ref = nb.tenancy.contacts.get(name=contact_name)
    rv = nb.tenancy.contacts.delete([contact_ref])

    if rv:
        assert True
    else:
        assert False


if __name__ == "__main__":
    test_add_contact()
    sleep(10)
    test_modify_contact()
    sleep(10)
    test_delete_contact()
