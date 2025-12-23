"""
Script to demonstrate managing VLANs and VLAN Groups in NetBox.
"""
import sys
import os
import argparse
from os import getenv
from loguru import logger

# Add sys path to find netbox_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils.NetboxClient import NetboxClient

def main():
    parser = argparse.ArgumentParser(description="Manage NetBox VLANs")
    parser.add_argument("--create-group", action="store_true", help="Create a new VLAN Group")
    parser.add_argument("--create-vlan", action="store_true", help="Create a new VLAN")
    parser.add_argument("--name", type=str, required=True, help="Name of the VLAN or Group")
    parser.add_argument("--vid", type=int, help="VLAN ID (Required for --create-vlan)")
    parser.add_argument("--site", type=str, help="Site Name")
    parser.add_argument("--group", type=str, help="VLAN Group Name (for VLAN creation)")
    parser.add_argument("--desc", type=str, default="", help="Description")
    
    args = parser.parse_args()

    netbox_url = getenv("NETBOX_URL")
    netbox_token = getenv("NETBOX_TOKEN")

    if not netbox_url or not netbox_token:
        logger.error("Please set NETBOX_URL and NETBOX_TOKEN environment variables.")
        sys.exit(1)

    client = NetboxClient(netbox_url, netbox_token)

    if args.create_group:
        slug = args.name.lower().replace(" ", "-")
        logger.info(f"Creating VLAN Group '{args.name}'...")
        result = client.add_vlan_group(args.name, slug, args.site, args.desc)
        if result:
            logger.info("Successfully created VLAN Group:")
            logger.info(result)
        else:
            logger.error("Failed to create VLAN Group.")

    if args.create_vlan:
        if not args.vid:
            logger.error("Error: --vid is required when creating a VLAN.")
            sys.exit(1)
        
        logger.info(f"Creating VLAN '{args.name}' (ID: {args.vid})...")
        result = client.add_vlan(args.vid, args.name, args.site, args.group, args.desc)
        if result:
            logger.info("Successfully created VLAN:")
            logger.info(result)
        else:
            logger.error("Failed to create VLAN.")

if __name__ == "__main__":
    main()
