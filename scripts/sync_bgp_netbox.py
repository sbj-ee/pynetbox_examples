import re
from netmiko import ConnectHandler
from pynetbox import api
from datetime import datetime

# Configuration
NETBOX_URL = "http://netbox.example.com"
NETBOX_TOKEN = "your-netbox-api-token"

# Router inventory
IOSXR_ROUTERS = [
    {
        "device_type": "cisco_xr",
        "host": "iosxr1.example.com",
        "username": "admin",
        "password": "password",
        "secret": "secret"
    },
    # Add more IOSXR routers here
]

SROS_ROUTERS = [
    {
        "device_type": "nokia_sros",
        "host": "sros1.example.com",
        "username": "admin",
        "password": "password",
        "secret": "secret"
    },
    # Add more SROS routers here
]

# Initialize Netbox API
netbox = api(url=NETBOX_URL, token=NETBOX_TOKEN)

def parse_iosxr_bgp(output):
    """Parse IOSXR BGP neighbor output"""
    bgp_neighbors = []
    neighbor_pattern = re.compile(r'Neighbor\s+([0-9.]+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+)')
    
    for line in output.splitlines():
        match = neighbor_pattern.search(line)
        if match:
            neighbor = {
                'neighbor_ip': match.group(1),
                'remote_as': match.group(2),
                'state': match.group(3),
                'prefix_received': match.group(4),
                'prefix_sent': match.group(5),
                'uptime': match.group(6),
                'vrf': match.group(7)
            }
            bgp_neighbors.append(neighbor)
    
    return bgp_neighbors

def parse_sros_bgp(output):
    """Parse SROS BGP neighbor output"""
    bgp_neighbors = []
    neighbor_pattern = re.compile(r'(\S+)\s+:\s+([0-9.]+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)')
    
    for line in output.splitlines():
        match = neighbor_pattern.search(line)
        if match:
            neighbor = {
                'neighbor_ip': match.group(2),
                'remote_as': match.group(3),
                'state': match.group(4),
                'prefix_received': match.group(5),
                'prefix_sent': match.group(6),
                'vrf': match.group(7)
            }
            bgp_neighbors.append(neighbor)
    
    return bgp_neighbors

def get_device_id(netbox, hostname):
    """Get Netbox device ID by hostname"""
    device = netbox.dcim.devices.get(name=hostname)
    return device.id if device else None

def sync_to_netbox(device_hostname, bgp_neighbors):
    """Sync BGP neighbors to Netbox"""
    device_id = get_device_id(netbox, device_hostname)
    if not device_id:
        print(f"Device {device_hostname} not found in Netbox")
        return

    for neighbor in bgp_neighbors:
        # Check if BGP session exists
        existing_session = netbox.plugins.bgp_sessions.filter(
            device_id=device_id,
            remote_address=neighbor['neighbor_ip']
        )
        
        session_data = {
            'device': device_id,
            'remote_address': neighbor['neighbor_ip'],
            'remote_asn': neighbor['remote_as'],
            'status': 'active' if neighbor['state'].lower() == 'established' else 'down',
            'vrf': neighbor['vrf'],
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            if existing_session:
                # Update existing session
                session = existing_session[0]
                netbox.plugins.bgp_sessions.update(session.id, session_data)
                print(f"Updated BGP session for {neighbor['neighbor_ip']} on {device_hostname}")
            else:
                # Create new session
                netbox.plugins.bgp_sessions.create(**session_data)
                print(f"Created BGP session for {neighbor['neighbor_ip']} on {device_hostname}")
        except Exception as e:
            print(f"Error syncing {neighbor['neighbor_ip']} for {device_hostname}: {str(e)}")

def main():
    # Process IOSXR routers
    for router in IOSXR_ROUTERS:
        try:
            with ConnectHandler(**router) as conn:
                output = conn.send_command("show bgp neighbors")
                bgp_neighbors = parse_iosxr_bgp(output)
                sync_to_netbox(router['host'], bgp_neighbors)
        except Exception as e:
            print(f"Error connecting to IOSXR {router['host']}: {str(e)}")

    # Process SROS routers
    for router in SROS_ROUTERS:
        try:
            with ConnectHandler(**router) as conn:
                output = conn.send_command("show router bgp neighbor")
                bgp_neighbors = parse_sros_bgp(output)
                sync_to_netbox(router['host'], bgp_neighbors)
        except Exception as e:
            print(f"Error connecting to SROS {router['host']}: {str(e)}")

if __name__ == "__main__":
    main()
