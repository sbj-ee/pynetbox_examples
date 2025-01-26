from dotenv import dotenv_values
import pynetbox
import sys
from pprint import pprint
from time import sleep
import urllib3

urllib3.disable_warnings()
from netboxlib import connect_netbox, add_ip_prefix, get_all_ip_prefixes
from netboxlib import show_all_ip_prefixes, delete_ip_prefix
from pprint import pprint


def test_add_ip_prefix():
    nb = connect_netbox()
    prefix_dict = {"prefix": "192.168.7.0/24"}
    add_ip_prefix(nb, prefix=prefix_dict)
    assert True


def test_delete_ip_prefix():
    # FIX - this is not deleting
    nb = connect_netbox()
    prefix = "192.168.7.0/24"
    rv = delete_ip_prefix(nb, prefix)
    if rv:
        assert True
    else:
        assert False


def test_get_all_ip_prefixes():
    nb = connect_netbox()
    prefixes = get_all_ip_prefixes(nb)
    for prefix in prefixes:
        print(prefix)


def test_show_all_ip_prefixes():
    nb = connect_netbox()
    show_all_ip_prefixes(nb)


if __name__ == "__main__":
    test_get_all_ip_prefixes()
    test_show_all_ip_prefixes()
    test_add_ip_prefix()
    test_show_all_ip_prefixes()
    print("deleting a prefix")
    test_delete_ip_prefix()
    test_show_all_ip_prefixes()
