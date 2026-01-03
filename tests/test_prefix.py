import sys
import urllib3

urllib3.disable_warnings()
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from netbox_utils.netboxlib import connect_netbox, add_ip_prefix, get_all_ip_prefixes
from netbox_utils.netboxlib import show_all_ip_prefixes, delete_ip_prefix


def test_add_ip_prefix():
    nb = connect_netbox()
    prefix_str = "192.168.7.0/24"
    # Ensure clean state
    try:
        delete_ip_prefix(nb, prefix_str)
    except:
        pass

    prefix_dict = {"prefix": prefix_str}
    result = add_ip_prefix(nb, prefix=prefix_dict)
    assert result is True

    # Cleanup
    delete_ip_prefix(nb, prefix_str)


def test_delete_ip_prefix():
    # FIX - this is not deleting
    nb = connect_netbox()
    prefix = "192.168.7.0/24"

    # Ensure it exists first so we can test deleting it
    prefix_dict = {"prefix": prefix}
    add_ip_prefix(nb, prefix=prefix_dict)

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
