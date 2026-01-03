import warnings
import argparse
import sys
from dotenv import dotenv_values
from netmiko import ConnectHandler
import pynetbox
import re
from typing import Dict, List
import logging


# NetBox connection details
from os import getenv

# NetBox connection details
NETBOX_URL = getenv("NETBOX_URL")
NETBOX_TOKEN = getenv("NETBOX_TOKEN")

if not NETBOX_URL or not NETBOX_TOKEN:
    print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
    # We allow script to continue if just variables are defined, but let's see where they are used.
    # They are passed to main.

ROUTER_NAME = input("Enter router name: ")


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_short_interface_name(full_name: str) -> str:
    """Convert full interface name to short form (e.g., GigabitEthernet0/0/0/0 to Ge0/0/0/0)."""
    interface_map = {
        "GigabitEthernet": "Ge",
        "HundredGigE": "Hu",
        "FortyGigE": "Fo",
        "FourHundredGigE": "FH",
        "TenGigE": "Te",
        "Bundle-Ether": "BE",
        "Bundle-POS": "BP",
        "Serial": "Se",
        "Loopback": "Lo",
        "Null": "Nu",
        "Port-channel": "Po",
        "Vlan": "Vl",
        "Management": "Mg",
    }

    for long_name, short_name in interface_map.items():
        if full_name.startswith(long_name):
            return full_name.replace(long_name, short_name, 1)
    return full_name  # Return original if no match


def get_router_interfaces(
    device_ip: str, username: str, password: str, device_type: str = "cisco_ios"
) -> List[Dict]:
    """Connect to IOS-XR router and retrieve interfaces with descriptions."""
    try:
        device = {
            "device_type": device_type,
            "host": device_ip,
            "username": username,
            "password": password,
        }
        logger.info(f"Connecting to device {device_ip}")
        with ConnectHandler(**device) as net_connect:
            # Run 'show interfaces description' command
            output = net_connect.send_command("show interfaces description")
            interfaces = []

            # Parse output
            lines = output.splitlines()
            for line in lines[1:]:  # Skip header
                if line.strip():
                    # Example line: "GigabitEthernet0/0/0/0 up up Management Interface"
                    match = re.match(
                        r"^(\S+)\s+(up|down|admin-down)\s+(up|down|admin-down)\s*(.*)?$",
                        line,
                    )
                    if match:
                        intf_name, admin_status, oper_status, description = (
                            match.groups()
                        )
                        description = description.strip() if description else ""
                        short_name = get_short_interface_name(intf_name)
                        interfaces.append(
                            {"name": short_name, "description": description}
                        )
            logger.info(f"Retrieved {len(interfaces)} interfaces from {device_ip}")
            return interfaces
    except Exception as e:
        logger.error(f"Failed to retrieve interfaces from {device_ip}: {str(e)}")
        raise


def sync_netbox_interfaces(
    netbox_url: str, netbox_token: str, device_name: str, interfaces: List[Dict]
) -> None:
    """Synchronize router interfaces with NetBox."""
    try:
        # Connect to NetBox
        nb = pynetbox.api(url=netbox_url, token=netbox_token)
        nb.http_session.verify = (
            False  # Disable SSL verification if needed (not recommended for production)
        )

        # Get the device from NetBox
        device = nb.dcim.devices.get(name=device_name)
        if not device:
            logger.error(f"Device {device_name} not found in NetBox")
            raise ValueError(f"Device {device_name} not found in NetBox")

        logger.info(f"Processing interfaces for device {device_name} in NetBox")

        # Get existing interfaces in NetBox
        existing_interfaces = {
            intf.name: intf for intf in nb.dcim.interfaces.filter(device_id=device.id)
        }

        # Process each interface from the router
        for intf in interfaces:
            short_name = intf["name"]
            description = intf["description"]

            if short_name in existing_interfaces:
                # Update existing interface
                nb_interface = existing_interfaces[short_name]
                if nb_interface.description != description:
                    nb_interface.description = description
                    nb_interface.save()
                    logger.info(
                        f"Updated interface {short_name} description to '{description}'"
                    )
            else:
                # Create new interface
                nb.dcim.interfaces.create(
                    device=device.id,
                    name=short_name,
                    type="other",  # Adjust type as needed (e.g., '1000base-t' for GigabitEthernet)
                    description=description,
                )
                logger.info(
                    f"Created interface {short_name} with description '{description}'"
                )

        # Optionally, remove interfaces in NetBox that don't exist on the router
        router_interface_names = {intf["name"] for intf in interfaces}
        for nb_intf_name, nb_intf in existing_interfaces.items():
            if nb_intf_name not in router_interface_names:
                nb_intf.delete()
                logger.info(
                    f"Deleted interface {nb_intf_name} from NetBox as it does not exist on the router"
                )

        logger.info(f"Synchronization completed for device {device_name}")
    except Exception as e:
        logger.error(f"Failed to sync interfaces to NetBox for {device_name}: {str(e)}")
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--env",
        type=str,
        required=False,
        default="prod",
        help="specify the environment (prod, lab)",
    )
    parser.add_argument(
        "-r", "--router", type=str, required=False, help="indicate the router"
    )
    args = parser.parse_args()

    if args.env == "prod" or args.env == "production":
        env_file = "/home/usrsbj/.sbj_creds/ipno.env"
        environment = "production"
    elif args.env == "lab":
        env_file = "/home/usrsbj/.sbj_creds/ipno.lab.env"
        environment = "lab"
    else:
        print(f"unknown environment: {str(args.env)}")
        sys.exit()

    config = dotenv_values(env_file)
    warnings.filterwarnings("ignore")

    # Configuration
    router_ip = args.router  # Replace with your router IP
    username = config["username"]  # Replace with your username
    password = config["password"]  # Replace with your password
    netbox_url = NETBOX_URL  # Replace with your NetBox URL
    netbox_token = NETBOX_TOKEN  # Replace with your NetBox API token
    device_name = ROUTER_NAME  # Replace with your device name in NetBox

    try:
        # Get interfaces from router
        interfaces = get_router_interfaces(router_ip, username, password)

        print(interfaces)

        # Sync interfaces to NetBox
        sync_netbox_interfaces(netbox_url, netbox_token, device_name, interfaces)

    except Exception as e:
        logger.error(f"Script execution failed: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
