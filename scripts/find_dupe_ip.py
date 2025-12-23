import pynetbox
from collections import defaultdict
import urllib3

urllib3.disable_warnings()

# NetBox connection details
from os import getenv
import sys

# NetBox connection details
NETBOX_URL = getenv("NETBOX_URL")
API_TOKEN = getenv("NETBOX_TOKEN")

if not NETBOX_URL or not API_TOKEN:
    print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
    sys.exit()

# Initialize pynetbox client
nb = pynetbox.api(url=NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False


def find_duplicate_ips():
    # Fetch all IP addresses from NetBox
    ip_addresses = nb.ipam.ip_addresses.all()

    # Dictionary to store IP addresses and their occurrences
    ip_counts = defaultdict(list)

    # Iterate through IP addresses and group by address
    for ip in ip_addresses:
        ip_counts[str(ip.address)].append({
            'id': ip.id,
            'address': str(ip.address) if ip.address else 'None',
        })

    # Identify duplicates (IPs with more than one occurrence)
    duplicates = {ip: details for ip, details in ip_counts.items() if len(details) > 1}

    # Print results
    if duplicates:
        print("Duplicate IP addresses found:")
        for ip, instances in duplicates.items():
            print(f"\nIP Address: {ip}")
            for instance in instances:
                print(f"  - ID: {instance['id']}, IP: {instance['address']}")
    else:
        print("No duplicate IP addresses found.")

if __name__ == "__main__":
    find_duplicate_ips()
