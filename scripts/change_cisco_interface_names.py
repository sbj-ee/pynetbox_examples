import pynetbox
from os import getenv
import sys

# NetBox connection details
NETBOX_URL = getenv("NETBOX_URL")
NETBOX_TOKEN = getenv("NETBOX_TOKEN")

if not NETBOX_URL or not NETBOX_TOKEN:
    print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
    sys.exit()

# Interface name mapping
NAME_MAPPING = {
    "Fa": "FastEthernet",
    "Gi": "GigabitEthernet",
    "Eth": "Ethernet",
    "FH": "FourHundredGigE",
    "Fo": "FortyGigE",
    "Hu": "HundredGigE",
    "BE": "Bundle-Ether",
    "BV": "BVI",
    "Lo": "Loopback",
    "Vl": "Vlan",
    "Po": "port-channel",
    "Te": "TenGigE",
    "Nu": "Null",
    "Mg": "MgmtEth"
}

def connect_to_netbox():
    """Establish connection to NetBox API"""
    return pynetbox.api(url=NETBOX_URL, token=NETBOX_TOKEN)

def get_manufacturer_id(nb, manufacturer_name):
    """Get manufacturer ID from NetBox given the manufacturer name"""
    try:
        manufacturer = nb.dcim.manufacturers.get(name=manufacturer_name)
        if manufacturer:
            return manufacturer.id
        else:
            print(f"Manufacturer '{manufacturer_name}' not found in NetBox")
            return None
    except Exception as e:
        print(f"Error retrieving manufacturer ID for '{manufacturer_name}': {str(e)}")
        return None
    
def is_long_name_already_used(name):
    """Check if the interface name already uses the long format"""
    long_names = set(NAME_MAPPING.values())
    return any(name.startswith(long_name) for long_name in long_names)

def update_interface_name(interface):
    """Update interface name from short to long format for Cisco devices"""
    # Skip if already using long name
    if is_long_name_already_used(interface.name):
        return False
    
    original_name = interface.name
    new_name = original_name
    
    # Check each short name and replace with long name
    for short_name, long_name in NAME_MAPPING.items():
        if original_name.startswith(short_name):
            new_name = long_name + original_name[len(short_name):]
            break
    
    if new_name != original_name:
        try:
            interface.name = new_name
            # interface.save()
            print(f"Updated interface id={interface.id} {original_name} to {new_name}")
            return True
        except Exception as e:
            print(f"Error updating interface id={interface.id} {original_name}: {str(e)}")
            return False
    return False

def main():
    """Main function to process interfaces on Cisco devices"""
    try:
        # Connect to NetBox
        nb = connect_to_netbox()
        nb.http_session.verify = False
        
        # Get all devices from Cisco Systems
        cisco_devices = nb.dcim.devices.filter(manufacturer_id=get_manufacturer_id(nb, "Cisco Systems"))
        
        # Counter for updated interfaces
        updated_count = 0
        total_count = 0
        
        # Process interfaces for each Cisco device
        for device in cisco_devices:
            interfaces = nb.dcim.interfaces.filter(device_id=device.id)
            for interface in interfaces:
                total_count += 1
                if update_interface_name(interface):
                    updated_count += 1
                
        print(f"\nProcessing complete. Updated {updated_count} out of {total_count} interfaces on Cisco Systems devices.")
        
    except Exception as e:
        print(f"Error connecting to NetBox or processing interfaces: {str(e)}")

if __name__ == "__main__":
    main()
