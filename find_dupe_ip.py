import pynetbox
from collections import defaultdict

# NetBox connection details
NETBOX_URL = "http://your-netbox-instance.com"  # Replace with your NetBox URL
API_TOKEN = "your-api-token"  # Replace with your NetBox API token

# Initialize pynetbox client
nb = pynetbox.api(url=NETBOX_URL, token=API_TOKEN)

def find_duplicate_ips():
    # Fetch all IP addresses from NetBox
    ip_addresses = nb.ipam.ip_addresses.all()
    
    # Dictionary to store IP addresses and their occurrences
    ip_counts = defaultdict(list)
    
    # Iterate through IP addresses and group by address
    for ip in ip_addresses:
        ip_counts[str(ip.address)].append({
            'id': ip.id,
            'interface': str(ip.interface) if ip.interface else 'None',
            'device': str(ip.interface.device) if ip.interface and ip.interface.device else 'None'
        })
    
    # Identify duplicates (IPs with more than one occurrence)
    duplicates = {ip: details for ip, details in ip_counts.items() if len(details) > 1}
    
    # Print results
    if duplicates:
        print("Duplicate IP addresses found:")
        for ip, instances in duplicates.items():
            print(f"\nIP Address: {ip}")
            for instance in instances:
                print(f"  - ID: {instance['id']}, Device: {instance['device']}, Interface: {instance['interface']}")
    else:
        print("No duplicate IP addresses found.")
        
if __name__ == "__main__":
    find_duplicate_ips()
