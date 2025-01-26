import sys
import pynetbox
from ipaddress import IPv4Network
from ipaddress import IPv4Interface
from ipaddress import ip_address, IPv4Address
from pprint import pprint
from dotenv import dotenv_values


nm_cidr_dict = {
    "255.255.255.255",
    "/32",
    "255.255.255.254",
    "/31",
    "255.255.255.252",
    "/30",
    "255.255.255.248",
    "/29",
    "255.255.255.240",
    "/28",
    "255.255.255.224",
    "/27",
    "255.255.255.192",
    "/26",
    "255.255.255.128",
    "/25",
    "255.255.255.0",
    "/24",
    "255.255.254.0",
    "/23",
    "255.255.252.0",
    "/22",
    "255.255.248.0",
    "/21",
    "255.255.240.0",
    "/20",
    "255.255.224.0",
    "/19",
    "255.255.192.0",
    "/18",
    "255.255.128.0",
    "/17",
    "255.255.0.0",
    "/16",
    "255.254.0.0",
    "/15",
    "255.252.0.0",
    "/14",
    "255.248.0.0",
    "/13",
    "255.240.0.0",
    "/12",
    "255.224.0.0",
    "/11",
    "255.192.0.0",
    "/10",
    "255.128.0.0",
    "/9",
    "255.0.0.0",
    "/8",
    "254.0.0.0",
    "/7",
    "252.0.0.0",
    "/6",
    "248.0.0.0",
    "/5",
    "240.0.0.0",
    "/4",
    "224.0.0.0",
    "/3",
    "192.0.0.0",
    "/2",
    "128.0.0.0",
    "/1",
    "0.0.0.0",
    "/0",
}


def connect_netbox():
    config = dotenv_values("netbox.env")

    try:
        token = config["token"]
        url = config["url"]
    except KeyError:
        print("key missing from env file")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False
    return nb


def get_pynetbox_version(nb) -> str:
    """get the netbox version"""
    return str(nb.status()["netbox-version"])


def show_pynetbox_version(nb) -> None:
    """display the netbox version"""
    print(get_pynetbox_version(nb))


def show_all_netbox_devices(nb) -> None:
    """show all devices in netbox"""
    devices = nb.dcim.devices.all()
    for device in devices:
        print(
            f"{str(device.id):<6} {str(device):<30}  {str(device.primary_ip):<20}  {str(device.device_role)}"
        )


def get_netbox_device_count(nb):
    """get the count of the number of devices in netbox"""
    return nb.dcim.devices.count()


def check_if_cidr_exists(nb, cidr: str) -> bool:
    """given a CIDR, check to see if that CIDR is in netbox"""
    result = False
    try:
        result = nb.ipam.ip_addresses.get(address=cidr)
    except pynetbox.RequestError as e:
        print(e.error)

    if result:
        return True
    else:
        return False


def check_if_ip_exists(nb, ip: str) -> bool:
    """given just an IP, look for any CIDR which exists in netbox using that IP"""
    rv = False
    max_bitrange = 128
    ip_type = ip_address(ip)
    if isinstance(ip_type, IPv4Address):
        max_bitrange = 32
    for slash in range(max_bitrange, 0, -1):
        cidr = f"{ip}{slash}"
        result = nb.ipam.ip_addresses.get(address=cidr)
        if result:
            print(f"IP: {ip}  =>  CIDR: {cidr}  exists in netbox")
            rv = True
    if rv is False:
        print(f"IP: {ip} was not found in netbox")
    return rv


def get_cidr_from_ip(nb, ip: str) -> str:
    """given an IP, return the CIDR if it exists in netbox"""
    max_bitrange = 128
    ip_type = ip_address(ip)
    if isinstance(ip_type, IPv4Address):
        max_bitrange = 32
    for slash in range(max_bitrange, 0, -1):
        cidr = f"{ip}/{slash}"
        result = nb.ipam.ip_addresses.get(address=cidr)

        if result:
            return cidr


def get_all_ip_prefixes(nb):
    """get all of the ip prefixes"""
    return nb.ipam.prefixes.all()


def show_all_ip_prefixes(nb) -> None:
    """show all of the ip prefixes"""
    prefixes = nb.ipam.prefixes.all()
    for pf in prefixes:
        print(pf)


def add_ip_prefix(nb, prefix) -> bool:
    """add a netbox prefix"""
    # ensure the prefix doesn't exist
    prefixes = get_all_ip_prefixes(nb)
    if prefix in prefixes:
        return False
    else:
        nb.ipam.prefixes.create(prefix)
        return True


def delete_ip_prefix(nb, prefix) -> bool:
    """delete a netbox prefix"""
    try:
        prefix_to_delete = nb.ipam.prefixes.get(prefix=prefix)
        if prefix_to_delete is not None:
            prefix_to_delete.delete()
            return True
        raise "not found"
    except Exception as e:
        print(e)
        return False


def check_if_device_name_exists(nb, device_name: str) -> bool:
    """check if a device name exists in netbox"""
    try:
        device_name = nb.dcim.devices.get(name=device_name)
        print(f"device_name = {device_name}")
        if device_name is not None:
            return True
        else:
            raise "Device not found exception"
    except:
        return False


def get_ip_device_info(nb, ip) -> bool:
    """using just the IP, map to the device"""
    try:
        result = nb.ipam.ip_addresses.get(address=ip)
        if result:
            print(f"result.id: {result.id}")
        if result.url:
            print(f"result.url: {result.url}")
        if result.display:
            print(f"result.display: {result.display}")
        if result.family.value:
            print(f"result.family.value: {result.family.value}")
        if result.family.label:
            print(f"result.family.label: {result.family.label}")
        if result.description:
            print(f"result.description: {result.description}")
        if result.created:
            print(f"result.created: {result.created}")
        if result.last_updated:
            print(f"result.last_updated: {result.last_updated}")
        if result.dns_name:
            print(f"result.dns_name: {result.dns_name}")
        if result.tags:
            print(f"result.tags: {result.tags}")
        if result.assigned_object:
            if result.assigned_object.url:
                print(f"assigned object.url: {result.assigned_object.url}")
            if result.assigned_object.id:
                print(f"assigned object.id: {result.assigned_object.id}")
            if result.assigned_object.display:
                print(f"assigned object.display: {result.assigned_object.display}")
            if result.assigned_object.device.id:
                print(f"assigned object.device.id: {result.assigned_object.device.id}")
            if result.assigned_object.device.name:
                print(
                    f"assigned object.device.name: {result.assigned_object.device.name}"
                )
            if result.assigned_object.device.url:
                print(
                    f"assigned object.device.url: {result.assigned_object.device.url}"
                )
            if result.assigned_object.device.display:
                print(
                    f"assigned object.device.display: {result.assigned_object.device.display}"
                )

            # get the device using result.object.device.id
            device = nb.dcim.devices.get(result.assigned_object.device.id)
            pprint(dict(device), indent=4)
    except pynetbox.RequestError as e:
        print(e.error)
        return False

    return True


def get_site_id(nb, site: str) -> int:
    """retrieve a specific site id"""
    try:
        ndev_site = nb.dcim.sites.get(name=site)
        if ndev_site is not None:
            return int(ndev_site.id)
    except pynetbox.RequestError as e:
        print(e.error)
        return -1


def get_device_type_id(nb, device_type: str) -> int:
    """retrieve a specific device type id"""
    try:
        ndev_type = nb.dcim.device_types.get(model=device_type)
        if ndev_type is not None:
            return int(ndev_type.id)
    except pynetbox.RequestError as e:
        print(e.error)
        return -1


def get_device_role_id(nb, device_role: str) -> int:
    """retrieve a specific device role id"""
    try:
        ndev_role = nb.dcim.device_roles.get(name=device_role)
        if ndev_role is not None:
            return int(ndev_role.id)
    except pynetbox.RequestError as e:
        print(e.error)
        return -1


def create_netbox_device(
    nb, device_name: str, site: str, device_type: str, device_role: str
) -> str:
    """add a device into netbox"""
    try:
        result = nb.dcim.devices.create(
            name=device_name,
            device_type=get_device_type_id(nb, device_type),
            role=get_device_role_id(nb, device_role),
            site=get_site_id(nb, site),
        )
        return result
    except pynetbox.RequestError as e:
        print(e.error)
        return str(e.error)


def delete_netbox_device(nb, device_name: str) -> bool:
    """
    delete a netbox device
    note: the device must be in the status 'decommissioning' to be deleted
    *this is an optional setting
    """
    ndev_device = nb.dcim.devices.get(name=device_name)
    if ndev_device is not None:
        ndev_device.delete()
        return True
    else:
        print(f"device name {device_name} not found")
        return False


def get_ip_status(nb, cidr: str) -> str:
    """
    get the status for a netbox ip_address using the cidr
    """
    try:
        response = nb.ipam.ip_addresses.get(address=cidr)
        return response.status
    except Exception as e:
        print(f"Exception: {e}")
        return "Unknown"


def change_ip_status(nb, cidr: str, status: str) -> bool:
    """change the status for a netbox ip_address"""
    try:
        response = nb.ipam.ip_addresses.get(address=cidr)
        response.status = status.lower()
        response.save()
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False


def change_ip_desc(nb, cidr: str, description: str) -> bool:
    """change a netbox ip_address description"""
    try:
        response = nb.ipam.ip_addresses.get(address=cidr)
        response.description = description
        response.save()
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False


def get_contacts_all(nb):
    """get all contacts"""
    try:
        contacts = nb.tenancy.contacts.all()
        return contacts
    except Exception as e:
        print(f"Exception: {e}")
        return False


def add_contact(nb, contact_name: str) -> bool:
    """add a netbox contact"""
    try:
        nb.tenancy.contacts.create(name=contact_name)
        return True
    except Exception as e:
        print(f"exception: {e}")
        return False


def modify_contact() -> bool:
    """modify a netbox contact"""
    ...
    # need to deal with case of more than one record


def delete_contact(nb, contact_name: str) -> bool:
    """delete a netbox contact"""
    ...
    # need to deal with case of more than one record


def show_all_contacts(nb) -> bool:
    """show all netbox contacts"""
    try:
        contacts = get_contacts_all(nb)
        for contact in contacts:
            print(f"{contact.name}, {contact.title}, {contact.tags}")
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False


def check_asn_exists(nb, asn: int) -> bool:
    """check if an ASN exists in netbox"""
    rv = nb.ipam.asns.get(asn=asn)
    if rv:
        return True
    else:
        return False


def add_asn(nb, asn: int, desc: str) -> bool:
    """Add an ASN for RIR=1 ARIN"""
    rv = nb.ipam.asns.create(asn=asn, rir=1, description=desc)
    if rv:
        return True
    else:
        return False


def delete_asn(nb, asn) -> bool:
    """Delete an ASN"""
    asn_ref = nb.ipam.asns.get(asn=asn)
    rv = nb.ipam.asns.delete([asn_ref])

    if rv:
        return True
    else:
        return False


def get_bgp_community_desc(nb, community: str) -> str:
    """Get the description for a specific BGP Community from Netbox"""
    try:
        rv = nb.plugins.bgp.community.get(value=community)
        return rv["description"]
    except Exception as e:
        print(f"Exception getting {community} from Netbox")
        return ""


def get_all_bgp_communities(nb) -> dict:
    """Get all the BGP Communities from Netbox and return them as a dict"""
    bgp_community_dict = dict()
    try:
        communities = nb.plugins.bgp.community.all()
        for community in communities:
            bgp_community_dict[community] = community.description
        return bgp_community_dict
    except Exception as e:
        print(f"Exception getting communities from Netbox: {e}")


def add_bgp_community(nb, community: str, description: str) -> None:
    """Add a BGP Community"""
    try:
        nb.plugins.bgp.community.create(value=community, description=description)
    except Exception as e:
        print(f"Exception adding BGP Community: {e}")


def add_ipv4_ip(nb, cidr: str) -> str:
    """add an ipv4 IP into netbox"""
    # check to see if it already exists in netbox
    result = nb.ipam.ip_addresses.get(address=cidr)
    if result:
        return "IP Exists"
    else:
        set_reserved_status: bool = False
        description: str = ""
        ip_addr = cidr.split("/")[0]
        ifc: IPv4Interface = IPv4Interface(cidr)
        net: IPv4Network = IPv4Network(ifc.network)

        if str(net.broadcast_address) == str(ip_addr):
            description = "Broadcast"
            set_reserved_status = True
        elif str(ifc.network) == str(cidr):
            description = "Subnet"
            set_reserved_status = True

        ip_add_dict = dict(
            address=cidr,
            description=description,
        )
        new_ip = nb.ipam.ip_addresses.create(ip_add_dict)
        if set_reserved_status:
            change_ip_status(nb, cidr, "Reserved")
        return new_ip
