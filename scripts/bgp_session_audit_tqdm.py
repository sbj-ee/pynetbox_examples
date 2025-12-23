import pynetbox
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException
import re
from datetime import datetime
import logging
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
from getpass import getpass
import urllib3

urllib3.disable_warnings()



# Configure logging
logging.basicConfig(filename='bgp_audit.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# NetBox configuration
from os import getenv
import sys

# NetBox configuration
NETBOX_URL = getenv("NETBOX_URL")
NETBOX_TOKEN = getenv("NETBOX_TOKEN")

if not NETBOX_URL or not NETBOX_TOKEN:
    print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
    sys.exit()
router_user = input("Router username: ")
router_password = getpass("Router password: ")

# Router credentials (replace with your own or use a secure method like environment variables)
ROUTER_CREDENTIALS = {
    'username': router_user,
    'password': router_password,
    'device_type': 'cisco_ios'  # Adjust based on your router type (e.g., 'cisco_ios', 'juniper', etc.)
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException,)),
    before_sleep=lambda retry_state: logging.info(
        f"Retrying NetBox connection (attempt {retry_state.attempt_number})..."
    )
)
def initialize_netbox():
    """Initialize pynetbox API connection with retry."""
    try:
        nb = pynetbox.api(url=NETBOX_URL, token=NETBOX_TOKEN)
        nb.http_session.verify = False  # Disable SSL verification if needed
        return nb
    except Exception as e:
        logging.error(f"Failed to connect to NetBox: {e}")
        raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException,)),
    before_sleep=lambda retry_state: logging.info(
        f"Retrying BGP sessions retrieval (attempt {retry_state.attempt_number})..."
    )
)
def get_bgp_sessions(nb):
    """Retrieve all BGP sessions from NetBox using the BGP plugin with retry."""
    try:
        bgp_sessions = nb.plugins.bgp.session.all()
        return list(bgp_sessions)
    except Exception as e:
        logging.error(f"Failed to retrieve BGP sessions from NetBox: {e}")
        raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((NetMikoTimeoutException, NetMikoAuthenticationException)),
    before_sleep=lambda retry_state: logging.info(
        f"Retrying connection to router {retry_state.args[0]} (attempt {retry_state.attempt_number})..."
    )
)
def get_router_bgp_status(device_ip, bgp_neighbor_ip):
    """Connect to the router and check the BGP session status for a specific neighbor with retry."""
    try:
        connection = ConnectHandler(
            device_type=ROUTER_CREDENTIALS['device_type'],
            ip=device_ip,
            username=ROUTER_CREDENTIALS['username'],
            password=ROUTER_CREDENTIALS['password']
        )
        
        # Execute command to get BGP neighbor status (Cisco IOS example)
        output = connection.send_command("show ip bgp neighbors")
        connection.disconnect()
        
        # Parse the output to find the neighbor status
        neighbor_status = parse_bgp_status(output, bgp_neighbor_ip)
        return neighbor_status
    
    except (NetMikoTimeoutException, NetMikoAuthenticationException) as e:
        logging.error(f"Failed to connect to router {device_ip}: {e}")
        raise
    except Exception as e:
        logging.error(f"Error checking BGP status on {device_ip}: {e}")
        return None

def parse_bgp_status(output, neighbor_ip):
    """Parse BGP neighbor status from router output (Cisco IOS example)."""
    # Example regex to find BGP neighbor state
    pattern = rf"BGP neighbor is {neighbor_ip}.*?BGP state = (\w+)"
    match = re.search(pattern, output, re.DOTALL)
    
    if match:
        state = match.group(1)
        return state == "Established"
    return False

def generate_report(discrepancies):
    """Generate a report of discrepancies in BGP sessions."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"BGP Session Audit Report - {timestamp}\n"
    report += "=" * 50 + "\n\n"
    
    if not discrepancies:
        report += "No discrepancies found. All BGP sessions match NetBox records.\n"
    else:
        report += "Discrepancies found:\n\n"
        for discrepancy in discrepancies:
            report += f"Device: {discrepancy['device']}\n"
            report += f"Neighbor IP: {discrepancy['neighbor_ip']}\n"
            report += f"NetBox Status: {discrepancy['netbox_status']}\n"
            report += f"Router Status: {discrepancy['router_status']}\n"
            report += "-" * 50 + "\n"
    
    return report

def main():
    """Main function to audit BGP sessions."""
    discrepancies = []
    
    # Initialize NetBox connection
    nb = initialize_netbox()
    
    # Get all BGP sessions from NetBox
    bgp_sessions = get_bgp_sessions(nb)
    logging.info(f"Retrieved {len(bgp_sessions)} BGP sessions from NetBox.")
    
    # Check each BGP session with a progress bar
    for session in tqdm(bgp_sessions, desc="Checking BGP Sessions", unit="session"):
        try:
            device = session.device.name if session.device else None
            neighbor_ip = session.remote_address.address.split('/')[0] if session.remote_address else None
            local_ip = session.local_address.address.split('/')[0] if session.local_address else None
            
            if not device or not neighbor_ip:
                logging.warning(f"Skipping session {session.id}: Missing device or neighbor IP.")
                continue
            
            # Assume NetBox indicates the session should be active (Established)
            netbox_status = "Established"
            
            # Get device IP from NetBox (primary IP)
            device_obj = nb.dcim.devices.get(name=device)
            if not device_obj or not device_obj.primary_ip4:
                logging.warning(f"Device {device} not found or no primary IP in NetBox.")
                continue
            
            device_ip = device_obj.primary_ip4.address.split('/')[0]
            
            # Check BGP status on the router
            router_status = get_router_bgp_status(device_ip, neighbor_ip)
            
            # Compare NetBox and router status
            if router_status is None:
                discrepancies.append({
                    'device': device,
                    'neighbor_ip': neighbor_ip,
                    'netbox_status': netbox_status,
                    'router_status': "Connection Error"
                })
            elif not router_status:
                discrepancies.append({
                    'device': device,
                    'neighbor_ip': neighbor_ip,
                    'netbox_status': netbox_status,
                    'router_status': "Not Established"
                })
            else:
                logging.info(f"BGP session on {device} for neighbor {neighbor_ip} is Established.")
        
        except Exception as e:
            logging.error(f"Error processing session {session.id}: {e}")
            continue
    
    # Generate and print report
    report = generate_report(discrepancies)
    print(report)
    
    # Save report to file
    with open('bgp_audit_report.txt', 'w') as f:
        f.write(report)
    logging.info("Report generated and saved to bgp_audit_report.txt")

if __name__ == "__main__":
    main()
