import pynetbox
from typing import Dict, Optional

class NetboxManager:
    """A class to manage NetBox operations using pynetbox."""
    
    def __init__(self, url: str, token: str, ssl_verify: bool = True):
        """
        Initialize NetboxManager with NetBox API connection.
        
        Args:
            url (str): NetBox API URL (e.g., http://netbox.local/api).
            token (str): NetBox API token.
            ssl_verify (bool): Whether to verify SSL certificates (default: True).
        """
        try:
            self.nb = pynetbox.api(url, token=token)
            self.nb.http_session.verify = ssl_verify
        except Exception as e:
            raise Exception(f"Failed to connect to NetBox: {str(e)}")

    def add_site(self, name: str, slug: str, status: str = "active", **kwargs) -> Dict:
        """
        Add a site to NetBox.
        
        Args:
            name (str): Name of the site.
            slug (str): URL-friendly slug for the site.
            status (str): Status of the site (default: 'active').
            **kwargs: Additional site attributes (e.g., description, region).
        
        Returns:
            Dict: Created site data.
        
        Raises:
            Exception: If site creation fails.
        """
        try:
            site_data = {
                "name": name,
                "slug": slug,
                "status": status,
                **kwargs
            }
            site = self.nb.dcim.sites.create(site_data)
            return dict(site)
        except pynetbox.core.query.RequestError as e:
            raise Exception(f"Failed to add site: {str(e)}")

    def add_device(self, name: str, device_type: int, role: int, site: int, **kwargs) -> Dict:
        """
        Add a device to NetBox.
        
        Args:
            name (str): Name of the device.
            device_type (int): ID of the device type.
            role (int): ID of the device role.
            site (int): ID of the site.
            **kwargs: Additional device attributes (e.g., serial, status).
        
        Returns:
            Dict: Created device data.
        
        Raises:
            Exception: If device creation fails.
        """
        try:
            device_data = {
                "name": name,
                "device_type": device_type,
                "role": role,
                "site": site,
                **kwargs
            }
            device = self.nb.dcim.devices.create(device_data)
            return dict(device)
        except pynetbox.core.query.RequestError as e:
            raise Exception(f"Failed to add device: {str(e)}")

    def add_interface(self, device: int, name: str, type: str = "virtual", **kwargs) -> Dict:
        """
        Add an interface to a device in NetBox.
        
        Args:
            device (int): ID of the device.
            name (str): Name of the interface.
            type (str): Type of interface (default: 'virtual').
            **kwargs: Additional interface attributes (e.g., description, mac_address).
        
        Returns:
            Dict: Created interface data.
        
        Raises:
            Exception: If interface creation fails.
        """
        try:
            interface_data = {
                "device": device,
                "name": name,
                "type": type,
                **kwargs
            }
            interface = self.nb.dcim.interfaces.create(interface_data)
            return dict(interface)
        except pynetbox.core.query.RequestError as e:
            raise Exception(f"Failed to add interface: {str(e)}")

    def add_ip_address(self, address: str, interface: int, **kwargs) -> Dict:
        """
        Add an IP address to an interface in NetBox.
        
        Args:
            address (str): IP address with CIDR (e.g., '192.168.1.10/24').
            interface (int): ID of the interface.
            **kwargs: Additional IP address attributes (e.g., status, description).
        
        Returns:
            Dict: Created IP address data.
        
        Raises:
            Exception: If IP address creation fails.
        """
        try:
            ip_data = {
                "address": address,
                "interface": interface,
                **kwargs
            }
            ip_address = self.nb.ipam.ip_addresses.create(ip_data)
            return dict(ip_address)
        except pynetbox.core.query.RequestError as e:
            raise Exception(f"Failed to add IP address: {str(e)}")

# Example usage (commented out):
"""
if __name__ == "__main__":
    # Initialize NetboxManager
    netbox = NetboxManager(url="http://netbox.local/api", token="your-api-token-here", ssl_verify=False)
    
    # Add a site
    site = netbox.add_site(name="Main Site", slug="main-site", description="Primary data center")
    print("Created site:", site)
    
    # Add a device
    device = netbox.add_device(
        name="Router1",
        device_type=1,  # Replace with actual device type ID
        role=1,         # Replace with actual role ID
        site=site["id"],
        status="active"
    )
    print("Created device:", device)
    
    # Add an interface
    interface = netbox.add_interface(
        device=device["id"],
        name="eth0",
        type="1000base-t",
        description="Primary Ethernet interface"
    )
    print("Created interface:", interface)
    
    # Add an IP address
    ip = netbox.add_ip_address(
        address="192.168.1.10/24",
        interface=interface["id"],
        status="active",
        description="Primary IP for eth0"
    )
    print("Created IP address:", ip)
"""
