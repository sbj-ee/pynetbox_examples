import pynetbox
from loguru import logger
from getpass import getpass
import urllib3
import ipaddress
from ipaddress import ip_address, IPv4Address
from typing import Union, Optional
from pynetbox.core.response import RecordSet
from pprint import pprint
from os import getenv
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
            print(f"Exception: check_if_device_name_exists : {e}")
            return False

    def get_site_id(self, site_name: str) -> int | None:
        """Get the site id for a given site."""
        try:
            site = self.nb.dcim.sites.get(name=site_name)
            return site.id
        except Exception as e:
            print(f"Exception: get_site_id : {e}")
            return None

    def get_device_id(self, device_name: str) -> int | None:
        """Get the device id for a given device"""
        try:
            device = self.nb.dcim.devices.get(name=device_name)
            return device.id
        except Exception as e:
            print(f"Exception: get_device_id : {e}")
            return None

    def get_role_id(self, role_name: str) -> int | None:
        """ Get the role id for a given role"""
        try:
            role = self.nb.dcim.device_roles.get(name=role_name)
            return role.id
        except Exception as e:
            print(f"Exception: get_role_id : {e}")
            return None

    def get_device_type_id(self, device_type_name: str) -> int | None:
        """Get the device_type id for a given device type."""
        try:
            device_type = self.nb.dcim.device_types.get(model=device_type_name)
            return device_type.id
        except Exception as e:
            print(f"Exception: get_device_type_id : {e}")
            return None

    def add_device(self, device_site: str, device_name: str, device_role: str, device_type_name: str) -> dict:
        """Add a device into netbox"""
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
        """Add an interface to a device"""
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
        """Get the interface id for an interface."""
        try:
            interface = self.nb.dcim.interfaces.get(device_id=self.get_device_id(device_name), name=interface_name)
            return interface.id
        except Exception as e:
            print(f"Exception: get_interface_id : {e}")
            return None

    def add_ip_to_interface(self, device_name: str, interface_name: str, ip_addr: str, status: str, description: str) -> bool:
        """Add an IP to an interface."""
        try:
            ip_data = {
                    "address": ip_addr,
                    "interface": self.get_interface_id(device_name, interface_name),
                    "status": status.lower(),
                    "description": description
            }
            new_ip = self.nb.ipam.ip_addresses.create(**ip_data)
            return True
        except Exception as e:
            print(f"Exception: add_ip_to_interface : {e}")
            return False

    def get_ipaddress_id(self, ip_addr: str) -> int | None:
        """Get the ipaddress id for a given IP."""
        try:
            ipaddress = self.nb.ipam.ip_addresses.get(address=ip_addr)
            return ipaddress.id
        except Exception as e:
            print(f"Exception: get_ipaddress_id: {e}")
            return None

    def get_as_id(self, asn: int) -> int | None:
        """Get the AS id for a given ASN."""
        try:
            asn_entry = self.nb.ipam.asns.get(asn=asn)
            return asn_entry.id
        except Exception as e:
            print(f"Exception: get_as_id : {e}")
            return None

    def add_bgp_session(self, site: str, remote_as: int, remote_ip: str, local_as: int, local_ip: str, device: str, bgp_name: str, status: str) -> dict | None:
        """Add a BGP Session."""
        try:
            session_info = {
                    "name": bgp_name,
                    "description": bgp_name,
                    "local_as": self.get_as_id(local_as),
                    "local_address": self.get_ipaddress_id(local_ip),
                    "remote_as": self.get_as_id(remote_as),
                    "remote_address": self.get_ipaddress_id(remote_ip),
                    "device": self.get_device_id(device),
                    "status": status.lower(),
                    "site": self.get_site_id(site),
            }
            bgp_session = self.nb.plugins.bgp.session.create(session_info)
            return bgp_session
        except Exception as e:
            print(f"Exception add_bgp_session: {e}")
            return None

    def get_bgp_sessions_all(self) -> RecordSet | None:
        """Get ll the BGP Sessions."""
        try:
            bgp_sessions = self.nb.plugins.bgp.session.all()
            return bgp_sessions
        except Exception as e:
            print(f"Exception: get_bgp_sessions_all : {e}")
            return None

    def get_bgp_session_by_device_and_address(self, device_name: str, remote_addr: str):
        """Get a BGP Session by device and remote address."""
        try:
            sessions = self.nb.plugins.bgp.session.filter(device=device_name, remote_address=remote_addr)
            return next(iter(sessions), None)
        except Exception as e:
            print(f"Exception: get_bgp_session_by_device : {e}")
            return None

    def print_bgp_session_by_device_and_address(self, device_name: str, remote_addr: str) -> None:
        """Print the BGP Session information."""
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
        """Validate if the input is a proper ipv4 or ipv6 address."""
        try:
            # Validate CIDR notation (IP with subnet mask)
            my_ip_network = ipaddress.ip_network(cidr_string, strict=False)
            # Extract the IP address with the prefix length
            return f"{my_ip_network.network_address}/{my_ip_network.prefixlen}"
        except ValueError as e:
            raise ValueError(f"Invalid CIDR address: {cidr_string} - {str(e)}")

    def add_ip_to_netbox(self, cidr_string: str, description: str, status: str) -> str | None:
        """Add an IP address into Netbox after validation."""
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
                "status": status.lower(),
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

    def get_circuit_id(self, device_name: str, interface_name: str) -> int | None:
        """Get circuit ID from interface link_peers."""
        try:
            interface = self.nb.dcim.interfaces.get(device_id=self.get_device_id(device_name), name=interface_name)
            if interface and interface.link_peers:
                for peer in interface.link_peers:
                    if hasattr(peer, 'circuit'):
                        return peer.circuit.id
            return None
        except Exception as e:
            print(f"Exception: get_circuit_id : {e}")
            return None

    def get_circuit(self, device_name: str, interface_name: str) -> dict | None:
        """Get full circuit details."""
        try:
            circuit_id = self.get_circuit_id(device_name, interface_name)
            if circuit_id:
                circuit = self.nb.circuits.circuits.get(circuit_id)
                return dict(circuit)
            return None
        except Exception as e:
            print(f"Exception: get_circuit : {e}")
            return None


if __name__ == "__main__":
    netbox_url = getenv("NETBOX_URL")
    netbox_token = getenv("NETBOX_TOKEN")
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

    # nb_client.print_bgp_session_by_device_and_address("LSANCARCcor52", "206.72.211.104/23")

    device_name="VERNNYXAhed11"
    interface_name="1/1/1"
    ckt = nb_client.get_circuit(device_name=device_name, interface_name=interface_name)
    print(f"{device_name}    {interface_name}")
    pprint(ckt)
