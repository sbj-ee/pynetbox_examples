from os import getenv
import pynetbox
import sys
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
        # Cleanup
        rv.delete()

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

    # Setup - ensure contact exists
    contact = nb.tenancy.contacts.create(name=contact_name)
    if not contact:
        # Try getting it if creating fails (might already exist)
        contact = nb.tenancy.contacts.get(name=contact_name)

    contact.title = "Miner yabba dabba do"
    contact.save()

    # Cleanup
    if contact:
        contact.delete()


def test_delete_contact():
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")

    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    contact_name: str = "Bob Dole"

    # Setup - ensure contact exists
    try:
        nb.tenancy.contacts.create(name=contact_name)
    except:
        pass  # If it exists that is fine too

    contact_ref = nb.tenancy.contacts.get(name=contact_name)
    # The list wrapper [contact_ref] logic seems odd for simple delete, usually contact_ref.delete()
    # But adhering to original logic structure for now, just ensuring it exists.
    if contact_ref:
        rv = contact_ref.delete()
    else:
        rv = False

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
