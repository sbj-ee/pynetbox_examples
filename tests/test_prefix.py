"""Tests for NetBox prefix operations.

Note: NetBox may redirect HTTP to HTTPS, which converts POST to GET.
Ensure NETBOX_URL uses https:// for write operations to work.
"""
import sys
import os
import pytest
import urllib3
import uuid

urllib3.disable_warnings()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from netbox_utils.netboxlib import (
    connect_netbox,
    add_ip_prefix,
    get_all_ip_prefixes,
    show_all_ip_prefixes,
    delete_ip_prefix,
)


def get_unique_prefix():
    """Generate a unique prefix for testing."""
    # Use a random second octet to avoid conflicts
    octet = uuid.uuid4().int % 200 + 50  # 50-249
    return f"192.{octet}.99.0/24"


def test_add_ip_prefix():
    """Test adding an IP prefix to NetBox."""
    nb = connect_netbox()
    prefix_str = get_unique_prefix()

    try:
        # Ensure clean state
        delete_ip_prefix(nb, prefix_str)

        # Add prefix
        prefix_dict = {"prefix": prefix_str}
        result = add_ip_prefix(nb, prefix=prefix_dict)
        assert result is True, f"Failed to add prefix {prefix_str}"

        # Verify it was created
        created = nb.ipam.prefixes.get(prefix=prefix_str)
        assert created is not None, f"Prefix {prefix_str} was not created"

    finally:
        # Cleanup
        delete_ip_prefix(nb, prefix_str)


def test_delete_ip_prefix():
    """Test deleting an IP prefix from NetBox."""
    nb = connect_netbox()
    prefix_str = get_unique_prefix()

    try:
        # Ensure it exists first
        prefix_dict = {"prefix": prefix_str}
        add_ip_prefix(nb, prefix=prefix_dict)

        # Verify it exists
        existing = nb.ipam.prefixes.get(prefix=prefix_str)
        assert existing is not None, f"Prefix {prefix_str} was not created for delete test"

        # Delete it
        rv = delete_ip_prefix(nb, prefix_str)
        assert rv is True, f"delete_ip_prefix returned False for {prefix_str}"

        # Verify deletion
        deleted = nb.ipam.prefixes.get(prefix=prefix_str)
        assert deleted is None, f"Prefix {prefix_str} was not deleted"

    finally:
        # Ensure cleanup even if test fails
        try:
            delete_ip_prefix(nb, prefix_str)
        except Exception:
            pass


def test_get_all_ip_prefixes():
    """Test retrieving all IP prefixes from NetBox."""
    nb = connect_netbox()
    prefixes = get_all_ip_prefixes(nb)

    # Should return an iterable (could be empty)
    assert prefixes is not None
    # Convert to list to verify it's iterable
    prefix_list = list(prefixes)
    assert isinstance(prefix_list, list)

    for prefix in prefix_list:
        print(prefix)


def test_show_all_ip_prefixes():
    """Test displaying all IP prefixes from NetBox."""
    nb = connect_netbox()
    # This just prints, so we verify it doesn't raise an exception
    show_all_ip_prefixes(nb)


if __name__ == "__main__":
    test_get_all_ip_prefixes()
    test_show_all_ip_prefixes()
    test_add_ip_prefix()
    test_show_all_ip_prefixes()
    print("deleting a prefix")
    test_delete_ip_prefix()
    test_show_all_ip_prefixes()
