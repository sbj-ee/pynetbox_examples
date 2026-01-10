"""Tests for NetBox contact operations.

Note: NetBox may redirect HTTP to HTTPS, which converts POST to GET.
Ensure NETBOX_URL uses https:// for write operations to work.
"""
from os import getenv
import pynetbox
import sys
import pytest
import urllib3
import uuid

urllib3.disable_warnings()


def get_netbox_connection():
    """Get NetBox API connection."""
    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")

    if not token or not url:
        pytest.skip("NETBOX_TOKEN or NETBOX_URL missing from environment variables")

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False
    return nb


def test_add_contact() -> None:
    """Test creating a contact in NetBox."""
    nb = get_netbox_connection()

    # Use unique name to avoid conflicts
    contact_name = f"Test_Contact_{uuid.uuid4().hex[:8]}"

    try:
        # Create contact
        nb.tenancy.contacts.create(name=contact_name)

        # Verify by fetching it back (handles HTTP redirect issue)
        created = nb.tenancy.contacts.get(name=contact_name)
        assert created is not None, f"Contact '{contact_name}' was not created"
        assert created.name == contact_name

    finally:
        # Cleanup - always try to delete
        contact = nb.tenancy.contacts.get(name=contact_name)
        if contact:
            contact.delete()


def test_modify_contact():
    """Test modifying a contact in NetBox."""
    nb = get_netbox_connection()

    contact_name = f"Test_Contact_{uuid.uuid4().hex[:8]}"
    new_title = "Test Title Modified"

    try:
        # Setup - create contact
        nb.tenancy.contacts.create(name=contact_name)

        # Fetch the created contact
        contact = nb.tenancy.contacts.get(name=contact_name)
        assert contact is not None, f"Contact '{contact_name}' was not created"

        # Modify the contact
        contact.title = new_title
        contact.save()

        # Verify modification
        updated = nb.tenancy.contacts.get(name=contact_name)
        assert updated.title == new_title

    finally:
        # Cleanup
        contact = nb.tenancy.contacts.get(name=contact_name)
        if contact:
            contact.delete()


def test_delete_contact():
    """Test deleting a contact from NetBox."""
    nb = get_netbox_connection()

    contact_name = f"Test_Contact_{uuid.uuid4().hex[:8]}"

    # Setup - create contact
    nb.tenancy.contacts.create(name=contact_name)

    # Verify it exists
    contact = nb.tenancy.contacts.get(name=contact_name)
    assert contact is not None, f"Contact '{contact_name}' was not created"

    # Delete the contact
    result = contact.delete()
    assert result is True

    # Verify deletion
    deleted = nb.tenancy.contacts.get(name=contact_name)
    assert deleted is None, f"Contact '{contact_name}' was not deleted"


if __name__ == "__main__":
    test_add_contact()
    test_modify_contact()
    test_delete_contact()
