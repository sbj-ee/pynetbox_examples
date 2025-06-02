import pynetbox
from loguru import logger
from getpass import getpass
import urllib3
from ipaddress import ip_address, IPv4Address
from typing import Union, Optional

urllib3.disable_warnings()


class NetboxClient:
    """A client for using the Netbox API"""

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.nb = self.connect()


    def connect(self):
        """Get the connection handle for Netbox."""
        self.nb = pynetbox.api(url=self.url, token=self.token)
        self.nb.http_session.verify = False
        return self.nb

    @staticmethod
    def setup_logging() -> None:
        """Configure the logging."""
        logger.remove()
        logger.add("./netbox.log")
        logger.info("Logging configured...")

    def get_pynetbox_version(self) -> str:
        """get the netbox version"""
        return str(self.nb.status()["netbox-version"])

    def check_if_cidr_exists(self, cidr: str) -> bool:
        """given a CIDR, check to see if that CIDR is in netbox"""
        result = False
        try:
            result = self.nb.ipam.ip_addresses.get(address=cidr)
        except pynetbox.RequestError as e:
            print(e.error)

        if result:
            return True
        else:
            return False

    def get_cidr_from_ip(self, ip: str) -> str:
        """"given an IP, return the CIDR if it exists in netbox"""
        max_bitrange: int = 128
        ip_type = ip_address(ip)
        if isinstance(ip_type, IPv4Address):
            max_bitrange: int = 32

        for slash in range(max_bitrange, 0, -1):
            cidr = f"{ip}/{slash}"
            result = self.nb.ipam.ip_addresses.get(address=cidr)

            if result:
                return cidr

    def check_if_device_name_exists(self, device_name: str) -> bool:
        """check if a device name exists in netbox"""
        try:
            device_name = self.nb.dcim.devices.get(name=device_name)
            print(f"device_name = {device_name}")
            if device_name is not None:
                return True
            else:
                raise "Device not found exception"
        except Exception as e:
            print(e)
            return False

    def get_site_id(self, site_name: str) -> int | None:
        """Get the site id for a given site."""
        try:
            site = self.nb.dcim.sites.get(name=site_name)
            return site.id
        except Exception as e:
            print(e)
            return None

    def get_device_id(self, device_name: str) -> int | None:
        """Get the device id for a given device"""
        try:
            device = nb.dcim.devices.get(name=device_name)
            return device.id
        except Exception as e:
            print(e)
            return None

    def get_role_id(self, role_name: str) -> int | None:
        """ Get the role id for a given role"""
        try:
            role = self.nb.dcim.device_roles.get(name=role_name)
            return role.id
        except Exception as e:
            print(e)
            return None

    def get_device_type_id(self, device_type_name: str) -> int | None:
        """Get the device_type id for a given device type."""
        try:
            device_type = self.nb.dcim.device_types.get(model=device_type_name)
            return device_type.id
        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    netbox_url = input("Netbox URL: ")
    netbox_token = getpass("Token: ")
    nb_client = NetboxClient(netbox_url, netbox_token)
    nb_client.setup_logging()
    print(nb_client.get_pynetbox_version())
    # ip_addr = "216.170.130.221"
    # print(f"check if IP exists in netbox: {nb_client.check_if_cidr_exists(ip_addr)}")
    # print(nb_client.get_cidr_from_ip(ip_addr))
    my_device = "FTBGWIIEagg03"
    print(f"device {my_device} in netbox is {nb_client.check_if_device_name_exists(my_device)}")

    my_site_name = "STGRUTFK"
    print(f"site {my_site_name} id is {nb_client.get_site_id(my_site_name)}")

    my_role = "Switch"
    print(f"Switch role id is {nb_client.get_role_id(my_role)}")

    my_device_type = "93180YC-EX"
    print(f"Device type {my_device_type} id is {nb_client.get_device_type_id(my_device_type)}")

