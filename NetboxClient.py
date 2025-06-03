import pynetbox
from loguru import logger
from getpass import getpass
import urllib3
import ipaddress
from ipaddress import ip_address, IPv4Address
from typing import Union, Optional
from pynetbox.core.response import RecordSet

urllib3.disable_warnings()

class NetboxClient:
    """A client for using the Netbox API"""

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.nb = self.connect()

    def connect(self):
        """
        Establishes a connection to the NetBox API and returns the API client instance.

        Initializes the pynetbox API client using the provided URL and authentication token.
        Disables SSL certificate verification for the HTTP session.

        Returns:
            pynetbox.api.Api: An instance of the NetBox API client.
        """
        self.nb = pynetbox.api(url=self.url, token=self.token)
        self.nb.http_session.verify = False
        return self.nb

    @staticmethod
    def setup_logging() -> None:
        """
        Configures the logging system by removing existing handlers and adding a new log file handler.
        Logs an informational message indicating that logging has been configured.
        """
        logger.remove()
        logger.add("./netbox.log")
        logger.info("Logging configured...")

    def get_pynetbox_version(self) -> str:
        """
        Retrieves the current NetBox version from the NetBox API.

        Returns:
            str: The version string of the connected NetBox instance.
        """
        return str(self.nb.status()["netbox-version"])

    def check_if_cidr_exists(self, cidr: str) -> bool:
        """
        Checks if a given CIDR exists in NetBox.

        Args:
            cidr (str): The CIDR address to check (e.g., '192.168.1.0/24').

        Returns:
            bool: True if the CIDR exists in NetBox, False otherwise.

        Raises:
            pynetbox.RequestError: If there is an error communicating with the NetBox API.

        Note:
            Prints the error message if a RequestError is encountered.
        """
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
        """
        Given an IP address, attempts to find and return the most specific CIDR notation
        for that IP address that exists in NetBox.

        Args:
            ip (str): The IP address to search for.

        Returns:
            str: The CIDR notation (e.g., '192.0.2.1/32') if found in NetBox, otherwise None.

        Note:
            The function checks all possible prefix lengths for the given IP version,
            starting from the most specific (e.g., /32 for IPv4, /128 for IPv6) down to /1.
            It returns the first matching CIDR found in NetBox.
        """
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
        """
        Checks if a device with the specified name exists in NetBox.

        Args:
            device_name (str): The name of the device to check.

        Returns:
            bool: True if the device exists, False otherwise.

        Raises:
            Exception: If an unexpected error occurs during the lookup.

        Note:
            Prints the device object if found, and prints exception details if an error occurs.
        """
        try:
            device_name = self.nb.dcim.devices.get(name=device_name)
            print(f"device_name = {device_name}")
            if device_name is not None:
                return True
            else:
                raise "Device not found exception"
        except Exception as e:
            print(f"Exception: check_if_device_name_exists : {e}")
            return False

    def get_site_id(self, site_name: str) -> int | None:
        """
        Retrieves the unique identifier (ID) of a site given its name.

        Args:
            site_name (str): The name of the site to look up.

        Returns:
            int | None: The ID of the site if found, otherwise None.

        Raises:
            Exception: If an error occurs during the lookup, the exception is caught and None is returned.
        """
        try:
            site = self.nb.dcim.sites.get(name=site_name)
            return site.id
        except Exception as e:
            print(f"Exception: get_site_id : {e}")
            return None

    def get_device_id(self, device_name: str) -> int | None:
        """
        Retrieves the unique identifier (ID) of a device from NetBox by its name.

        Args:
            device_name (str): The name of the device to look up.

        Returns:
            int | None: The ID of the device if found, otherwise None.

        Raises:
            Exception: If an error occurs during the API request, the exception is caught and None is returned.
        """
        try:
            device = self.nb.dcim.devices.get(name=device_name)
            return device.id
        except Exception as e:
            print(f"Exception: get_device_id : {e}")
            return None

    def get_role_id(self, role_name: str) -> int | None:
        """
        Retrieve the ID of a device role by its name.

        Args:
            role_name (str): The name of the device role to look up.

        Returns:
            int | None: The ID of the device role if found, otherwise None.

        Raises:
            Exception: If an error occurs during the lookup, the exception is caught and None is returned.
        """
        try:
            role = self.nb.dcim.device_roles.get(name=role_name)
            return role.id
        except Exception as e:
            print(f"Exception: get_role_id : {e}")
            return None

    def get_device_type_id(self, device_type_name: str) -> int | None:
        """
        Retrieve the ID of a device type given its name.

        Args:
            device_type_name (str): The name of the device type to look up.

        Returns:
            int | None: The ID of the device type if found, otherwise None.

        Raises:
            Exception: If there is an error during the lookup, the exception is caught and None is returned.
        """
        try:
            device_type = self.nb.dcim.device_types.get(model=device_type_name)
            return device_type.id
        except Exception as e:
            print(f"Exception: get_device_type_id : {e}")
            return None

    def add_device(self, device_site: str, device_name: str, device_role: str, device_type_name: str) -> dict:
        """
        Adds a new device to NetBox.

        Args:
            device_site (str): The name or slug of the site where the device will be added.
            device_name (str): The name of the device to be created.
            device_role (str): The role assigned to the device.
            device_type_name (str): The name of the device type.

        Returns:
            dict: A dictionary representation of the newly created device.

        Raises:
            Exception: If the device could not be added due to a request error.
        """
        try:
            device_data = {
                    "name": device_name,
                    "device_type": self.get_device_type_id(device_type_name),
                    "role": self.get_role_id(device_role),
                    "site": self.get_site_id(device_site),
            }
            device = self.nb.dcim.devices.create(device_data)
            return dict(device)
        except pynetbox.core.query.RequestError as e:
            raise Exception(f"Failed to add device: {str(device_name)} : {e}")

    def add_interface_to_device(self, interface_name: str, device_name: str, interface_type: str, interface_desc: str) -> bool:
        """
        Adds a new interface to a specified device in NetBox.

        Args:
            interface_name (str): The name of the interface to add.
            device_name (str): The name of the device to which the interface will be added.
            interface_type (str): The type of the interface (e.g., '1000base-t', 'virtual', etc.).
            interface_desc (str): A description for the interface.

        Returns:
            bool: True if the interface was successfully added, False otherwise.

        Raises:
            Exception: Prints the exception message if an error occurs during interface creation.
        """
        try:
            interface_data = {
                    "device": self.get_device_id(device_name),
                    "name": interface_name,
                    "type": interface_type,
                    "enabled": True,
                    "description":interface_desc
            }
            new_interface = self.nb.dcim.interfaces.create(**interface_data)
            return True
        except Exception as e:
            print(f"Exception : add_interface_to_device : {e}")
            return False

    def get_interface_id(self, device_name: str, interface_name: str) -> int | None:
        """
        Retrieve the unique identifier (ID) of a specific interface on a given device.

        Args:
            device_name (str): The name of the device containing the interface.
            interface_name (str): The name of the interface whose ID is to be retrieved.

        Returns:
            int | None: The ID of the interface if found, otherwise None.

        Raises:
            Exception: If there is an error retrieving the interface, the exception is caught and None is returned.
        """
        try:
            interface = self.nb.dcim.interfaces.get(device_id=self.get_device_id(device_name), name=interface_name)
            return interface.id
        except Exception as e:
            print(f"Exception: get_interface_id : {e}")
            return None

    def add_ip_to_interface(self, device_name: str, interface_name: str, ip_addr: str, status: str, description: str) -> bool:
        """
        Adds an IP address to a specified interface on a device.

        Args:
            device_name (str): The name of the device to which the interface belongs.
            interface_name (str): The name of the interface to assign the IP address.
            ip_addr (str): The IP address to assign (in CIDR notation).
            status (str): The status to assign to the IP address (e.g., 'active', 'reserved').
            description (str): A description for the IP address.

        Returns:
            bool: True if the IP address was successfully added, False otherwise.
        """
        try:
            ip_data = {
                    "address": ip_addr,
                    "interface": self.get_interface_id(device_name, interface_name),
                    "status": status,
                    "description": description
            }
            new_ip = self.nb.ipam.ip_addresses.create(**ip_data)
            return True
        except Exception as e:
            print(f"Exception: add_ip_to_interface : {e}")
            return False

    def get_ipaddress_id(self, ip_addr: str) -> int | None:
        """
        Retrieve the unique identifier (ID) of an IP address from NetBox.

        Args:
            ip_addr (str): The IP address to look up.

        Returns:
            int | None: The ID of the IP address if found, otherwise None.

        Raises:
            Exception: If there is an error during the lookup, the exception is caught and None is returned.
        """
        try:
            ipaddress = self.nb.ipam.ip_addresses.get(address=ip_addr)
            return ipaddress.id
        except Exception as e:
            print(f"Exception: get_ipaddress_id: {e}")
            return None

    def get_as_id(self, asn: int) -> int | None:
        """
        Retrieve the unique identifier (ID) for an Autonomous System (AS) given its ASN.

        Args:
            asn (int): The Autonomous System Number to look up.

        Returns:
            int | None: The ID of the AS if found, otherwise None.

        Raises:
            Exception: If an error occurs during the lookup, the exception is caught and None is returned.
        """
        try:
            asn_entry = self.nb.ipam.asns.get(asn=asn)
            return asn_entry.id
        except Exception as e:
            print(f"Exception: get_as_id : {e}")
            return None

    def add_bgp_session(self, site: str, remote_as: int, remote_ip: str, local_as: int, local_ip: str, device: str, bgp_name: str, status: str) -> dict | None:
        """
        Add a BGP Session to NetBox.

        Args:
            site (str): The name or identifier of the site where the BGP session will be created.
            remote_as (int): The remote Autonomous System (AS) number.
            remote_ip (str): The remote peer's IP address.
            local_as (int): The local Autonomous System (AS) number.
            local_ip (str): The local peer's IP address.
            device (str): The name or identifier of the device associated with the BGP session.
            bgp_name (str): The name to assign to the BGP session.
            status (str): The operational status of the BGP session.

        Returns:
            dict | None: The created BGP session object as a dictionary if successful, otherwise None.

        Raises:
            Exception: Prints the exception message if an error occurs during session creation.
        """
        try:
            session_info = {
                    "name": bgp_name,
                    "description": bgp_name,
                    "local_as": self.get_as_id(local_as),
                    "local_address": self.get_ipaddress_id(local_ip),
                    "remote_as": self.get_as_id(remote_as),
                    "remote_address": self.get_ipaddress_id(remote_ip),
                    "device": self.get_device_id(device),
                    "status": status,
                    "site": self.get_site_id(site),
            }
            bgp_session = self.nb.plugins.bgp.session.create(session_info)
            return bgp_session
        except Exception as e:
            print(f"Exception add_bgp_session: {e}")
            return None

    def get_bgp_sessions_all(self) -> RecordSet | None:
        """
        Retrieve all BGP sessions from the NetBox API.

        Returns:
            RecordSet | None: A set of BGP session records if successful, otherwise None.

        Raises:
            Exception: If an error occurs while fetching BGP sessions, the exception is caught and logged.
        """
        try:
            bgp_sessions = self.nb.plugins.bgp.session.all()
            return bgp_sessions
        except Exception as e:
            print(f"Exception: get_bgp_sessions_all : {e}")
            return None

    def get_bgp_session_by_device_and_address(self, device_name: str, remote_addr: str):
        """
        Retrieve a BGP session for a given device and remote address.

        Args:
            device_name (str): The name of the device to search for.
            remote_addr (str): The remote address of the BGP session.

        Returns:
            object or None: The first matching BGP session object if found, otherwise None.

        Raises:
            Exception: If an error occurs during the API call, prints the exception and returns None.
        """
        try:
            sessions = self.nb.plugins.bgp.session.filter(device=device_name, remote_address=remote_addr)
            return next(iter(sessions), None)
        except Exception as e:
            print(f"Exception: get_bgp_session_by_device : {e}")
            return None

    def print_bgp_session_by_device_and_address(self, device_name: str, remote_addr: str) -> None:
        """
        Prints the BGP session information for a given device and remote address.

        Args:
            device_name (str): The name of the device to search for the BGP session.
            remote_addr (str): The remote address of the BGP peer.

        Returns:
            None

        Behavior:
            - Retrieves the BGP session matching the specified device and remote address.
            - If a session is found, prints a formatted table row with session details including ID, device, peer, remote AS, remote address, and status.
            - If no session is found, prints a message indicating that no session was found for the given device and remote address.
        """
        session = self.get_bgp_session_by_device_and_address(device_name, remote_addr)
        if session:
            device_name = str(session.device) if session.device else "N/A"
            peer_name = str(session.name) if session.name else "N/A"
            status = str(session.status) if session.status else "Unknown"
            peer_as = str(session.remote_as) if session.remote_as else "Unknown"
            remote_ip = str(session.remote_address) if session.remote_address else "Unknown"
            print(f"{'ID':>5} {'Device':<20} {'Peer':<30} {'Remote AS':<36} {'Remote Address':<45} {'Status':<15}")
            print("-" * 150)
            print(f"{session.id:>5} {device_name:<20.15} {peer_name:<30.20} {peer_as:<36.30} {remote_ip:<45.36} {status:<15}")
        else:
            print(f"No BGP session found for device {device_name} with remote address {remote_addr}")

    def validate_ip_cidr(self, cidr_string: str) -> str:
        """
        Validates whether the provided string is a valid IPv4 or IPv6 address in CIDR notation.

        Args:
            cidr_string (str): The IP address in CIDR notation (e.g., '192.168.1.0/24' or '2001:db8::/32').

        Returns:
            str: The normalized CIDR string in the format 'network_address/prefixlen'.

        Raises:
            ValueError: If the input string is not a valid CIDR address.
        """
        try:
            # Validate CIDR notation (IP with subnet mask)
            my_ip_network = ipaddress.ip_network(cidr_string, strict=False)
            # Extract the IP address with the prefix length
            return f"{my_ip_network.network_address}/{my_ip_network.prefixlen}"
        except ValueError as e:
            raise ValueError(f"Invalid CIDR address: {cidr_string} - {str(e)}")

    def add_ip_to_netbox(self, cidr_string: str, description: str, status: str) -> str | None:
        """
        Adds an IP address to NetBox after validating the CIDR notation and checking for duplicates.

        Args:
            cidr_string (str): The IP address in CIDR notation to add to NetBox.
            description (str): A description for the IP address.
            status (str): The status to assign to the IP address in NetBox.

        Returns:
            str | None: The newly created IP address object if successful, or None if the IP already exists or an error occurs.

        Raises:
            ValueError: If the provided CIDR string is invalid.
            Exception: For any other errors encountered during the process.
        """
        try:
            # Validate CIDR address
            validated_cidr = self.validate_ip_cidr(cidr_string)

            # Check if the IP/CIDR already exists in Netbox
            if self.check_if_cidr_exists(cidr_string):
                print(f"CIDR {cidr_string} already exists in Netbox")
                return None

            # Prepare IP data for NetBox
            ip_data = {
                "address": validated_cidr,
                "status": status,
                "description": description
            }

            # Add IP to NetBox
            ipam = nb.ipam.ip_addresses
            new_ip = ipam.create(**ip_data)

            print(f"Successfully added {validated_cidr} to NetBox")
            return new_ip
        except ValueError as e:
            print(f"Validation error: {str(e)}")
            return None
        except Exception as e:
            print(f"Error adding IP to NetBox: {str(e)}")
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
    # my_device = "FTBGWIIEagg03"
    # print(f"device {my_device} in netbox is {nb_client.check_if_device_name_exists(my_device)}")

    # my_site_name = "STGRUTFK"
    # print(f"site {my_site_name} id is {nb_client.get_site_id(my_site_name)}")

    # my_role = "Switch"
    # print(f"Switch role id is {nb_client.get_role_id(my_role)}")

    # my_device_type = "93180YC-EX"
    # print(f"Device type {my_device_type} id is {nb_client.get_device_type_id(my_device_type)}")

    # print(nb_client.add_device("STPTWI001", "STPTWI001cen02", "Router", "ASR-920-24SZ-IM"))
    # print(nb_client.add_interface_to_device("Lo555", "STPTWI001cen02", "virtual", "ISP Management and Source Interface"))
    # print(nb_client.add_ip_to_interface("STPTWI001cen02", "Lo555", "64.50.230.117/32", "active", "ISP Management and Source Interface"))

    # print(nb_client.add_bgp_session("ABDLWIXA", 4150, "66.66.66.0/30", 4181, "66.66.66.1/30", "MDSNWIGJdst53", "Testing BGP Add", "active"))
    # my_bgp_sessions = nb_client.get_bgp_sessions_all()
    # for session in my_bgp_sessions:
    #     print(f"BGP Session ID: {str(session.id):>6}   Device: {str(session.device):<18}   Remote IP: {str(session.remote_address):>30}  Name: {str(session.name)}")

    nb_client.print_bgp_session_by_device_and_address("LSANCARCcor52", "206.72.211.104/23")
