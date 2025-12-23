import pynetbox
import ipaddress
from os import getenv
import sys

# NetBox connection details
NETBOX_URL = getenv("NETBOX_URL")
API_TOKEN = getenv("NETBOX_TOKEN")

if not NETBOX_URL or not API_TOKEN:
    print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
    sys.exit()

# Initialize pynetbox API client
nb = pynetbox.api(url=NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

def get_bgp_session():
    """Retrieve a BGP session by ID."""
    try:
        session_id = input("Enter the BGP session ID to edit: ")
        session = nb.plugins.bgp.session.get(id=session_id)
        if not session:
            print(f"No BGP session found with ID {session_id}")
            return None
        return session
    except Exception as e:
        print(f"Error retrieving BGP session: {e}")
        return None

def display_session_details(session):
    """Display current BGP session details."""
    print("\nCurrent BGP Session Details:")
    print(f"ID: {session.id}")
    print(f"Device: {session.device.name if session.device else 'None'} (ID: {session.device.id if session.device else 'None'})")
    print(f"Local Address: {session.local_address.address if session.local_address else 'None'} (ID: {session.local_address.id if session.local_address else 'None'})")
    print(f"Remote Address: {session.remote_address.address if session.remote_address else 'None'} (ID: {session.remote_address.id if session.remote_address else 'None'})")
    print(f"Peer Group: {session.peer_group.name if session.peer_group else 'None'}")
    print(f"Status: {session.status.label if session.status else 'None'}")
    print(f"Site: {session.site.name if session.site else 'None'} (ID: {session.site.id if session.site else 'None'})")

def get_ip_address_id(prompt):
    """Prompt for an IP address and return its ID."""
    ip_input = input(f"{prompt} (enter IP address or leave blank to keep unchanged): ").strip()
    if not ip_input:
        return None
    try:
        # Validate IP address format
        ipaddress.ip_address(ip_input)
        # Find IP address in NetBox
        ip_obj = nb.ipam.ip_addresses.get(address=ip_input)
        if not ip_obj:
            print(f"IP address {ip_input} not found in NetBox.")
            return None
        return ip_obj.id
    except ValueError:
        print(f"Invalid IP address format: {ip_input}")
        return None
    except Exception as e:
        print(f"Error finding IP address: {e}")
        return None

def get_device_id():
    """Prompt for a device name and return its ID."""
    device_name = input("Enter new device name (or leave blank to keep unchanged): ").strip()
    if not device_name:
        return None
    try:
        device = nb.dcim.devices.get(name=device_name)
        if not device:
            print(f"Device {device_name} not found in NetBox.")
            return None
        return device.id
    except Exception as e:
        print(f"Error finding device: {e}")
        return None

def get_site_id():
    """Prompt for a site name and return its ID."""
    site_name = input("Enter new site name (or leave blank to keep unchanged): ").strip()
    if not site_name:
        return None
    try:
        site = nb.dcim.sites.get(name=site_name)
        if not site:
            print(f"Site {site_name} not found in NetBox.")
            return None
        return site.id
    except Exception as e:
        print(f"Error finding site: {e}")
        return None

def update_bgp_session(session):
    """Prompt for changes and update the BGP session."""
    try:
        print("\nLeave fields blank to keep them unchanged.")
        local_address_id = get_ip_address_id("Enter new local IP address")
        remote_address_id = get_ip_address_id("Enter new remote IP address")
        device_id = get_device_id()
        site_id = get_site_id()

        # Prepare update payload
        update_data = {}
        if local_address_id:
            update_data['local_address'] = local_address_id
        if remote_address_id:
            update_data['remote_address'] = remote_address_id
        if device_id:
            update_data['device'] = device_id
        if site_id:
            update_data['site'] = site_id

        if update_data:
            # Update the session
            nb.plugins.bgpsessions.sessions.update([{
                'id': session.id,
                **update_data
            }])
            print("BGP session updated successfully!")
        else:
            print("No changes provided. BGP session unchanged.")

        # Fetch and display updated session details
        updated_session = nb.plugins.bgpsessions.sessions.get(session.id)
        print("\nUpdated BGP Session Details:")
        display_session_details(updated_session)
    except Exception as e:
        print(f"Error updating BGP session: {e}")

def main():
    print("NetBox BGP Session Editor")
    session = get_bgp_session()
    if session:
        display_session_details(session)
        confirm = input("\nDo you want to edit this session? (yes/no): ").lower().strip()
        if confirm == 'yes':
            update_bgp_session(session)
        else:
            print("No changes made.")

if __name__ == "__main__":
    main()
