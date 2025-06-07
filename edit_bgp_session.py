import pynetbox
import ipaddress
from getpass import getpass

# NetBox connection details
NETBOX_URL = "http://your-netbox-url.com"  # Replace with your NetBox URL
API_TOKEN = getpass("Enter your NetBox API token: ")

# Initialize pynetbox API client
nb = pynetbox.api(url=NETBOX_URL, token=API_TOKEN)

def get_bgp_session():
    """Retrieve a BGP session by ID."""
    try:
        session_id = input("Enter the BGP session ID to edit: ")
        session = nb.plugins.bgpsessions.sessions.get(session_id)
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

def is_valid_cidr(cidr: str) -> bool:
    """
    Validate if a given string is a valid CIDR notation.
    
    Args:
        cidr: String in CIDR format (e.g., '192.168.1.0/24')
        
    Returns:
        bool: True if valid CIDR, False otherwise
    """
    try:
        # Attempt to create an IP network object
        ipaddress.ip_network(cidr, strict=True)
        return True
    except ValueError:
        return False
        
def get_ip_cidr_id(prompt):
    """Prompt for an IP CIDR address and return its ID."""
    cidr_input = input(f"{prompt} (enter IP address or leave blank to keep unchanged): ").strip()
    if not cidr_input:
        return None
    try:
        # Validate IP CIDR address format
        if is_valid_cidr(cidr_input):
            # Find IP address in NetBox
            ip_obj = nb.ipam.ip_addresses.get(address=ip_input)
            if not ip_obj:
                print(f"CIDR address {cidr_input} not found in NetBox.")
                return None
            return ip_obj.id
    except ValueError:
        print(f"Invalid IP address format: {cidr_input}")
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

def update_bgp_session(session):
    """Prompt for changes and update the BGP session."""
    try:
        print("\nLeave fields blank to keep them unchanged.")
        local_address_id = get_ip_cidr_id("Enter new local IP CIDR address")
        remote_address_id = get_ip_cidr_id("Enter new remote IP CIDR address")
        device_id = get_device_id()

        # Prepare update payload
        update_data = {}
        if local_address_id:
            update_data['local_address'] = local_address_id
        if remote_address_id:
            update_data['remote_address'] = remote_address_id
        if device_id:
            update_data['device'] = device_id

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
