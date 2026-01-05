"""
Script to get interfaces for a device from NetBox.
"""

import pynetbox
import os
from loguru import logger

# NetBox connection details (from environment variables)
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
DEVICE_NAME = "your-device-name"  # Replace with your device name

if not NETBOX_URL or not NETBOX_TOKEN:
    raise ValueError("NETBOX_URL and NETBOX_TOKEN must be set in environment variables")


def get_device_interfaces():
    """Get all interfaces for a device and log their details."""
    try:
        # Initialize pynetbox API connection
        nb = pynetbox.api(url=NETBOX_URL, token=NETBOX_TOKEN)

        # Get the device by name
        device = nb.dcim.devices.get(name=DEVICE_NAME)

        if not device:
            logger.error(f"Device '{DEVICE_NAME}' not found in NetBox")
            return

        # Get all interfaces for the device
        interfaces = nb.dcim.interfaces.filter(device_id=device.id)

        # Print interface details
        logger.info(f"\nInterfaces for device '{DEVICE_NAME}':")
        logger.info("-" * 50)

        for interface in interfaces:
            logger.info(f"Interface: {interface.name}")
            logger.info(f"  Type: {interface.type.value}")
            logger.info(f"  Enabled: {interface.enabled}")
            logger.info(f"  MAC Address: {interface.mac_address or 'N/A'}")
            logger.info(f"  MTU: {interface.mtu or 'N/A'}")
            logger.info(f"  Description: {interface.description or 'N/A'}")
            logger.info("-" * 50)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    get_device_interfaces()
