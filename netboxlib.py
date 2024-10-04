import pynetbox
from pprint import pprint


nm_cidr_dict = {
    "255.255.255.255", "/32",
    "255.255.255.254", "/31",
    "255.255.255.252", "/30",
    "255.255.255.248", "/29",
    "255.255.255.240", "/28",
    "255.255.255.224", "/27",
    "255.255.255.192", "/26",
    "255.255.255.128", "/25",
    "255.255.255.0", "/24",
    "255.255.254.0", "/23",
    "255.255.252.0", "/22",
    "255.255.248.0", "/21",
    "255.255.240.0", "/20",
    "255.255.224.0", "/19",
    "255.255.192.0", "/18",
    "255.255.128.0", "/17",
    "255.255.0.0", "/16"
}

def get_pynetbox_version(nb) -> str:
    return str(nb.status()["netbox-version"])


def show_pynetbox_version(nb) -> None:
    print(get_pynetbox_version(nb))


# this will stall for some reason - I suspect the firewall interfering with the data transfer
def show_all_netbox_devices(nb):
    devices = nb.dcim.devices.all()
    for device in devices:
        print(f"{str(device.id):<6} {str(device):<30}  {str(device.primary_ip):<20}  {str(device.device_role)}")


def get_netbox_device_count(nb):
    return nb.dcim.devices.count()


def check_if_cidr_exists(nb, cidr: str) -> bool:
    """Given a CIDR, check to see if that CIDR is in netbox"""
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
    """Given just an IP, look for any CIDR which exists in netbox using that IP"""
    rv = False
    for slash in nm_cidr_dict:
        cidr = f"{ip}{slash}"
        result = nb.ipam.ip_addresses.get(address=cidr)
        if result:
            print(f"IP: {ip}  =>  CIDR: {cidr}  exists in netbox")
            rv = True
    if rv is False:
        print(f"IP: {ip} was not found in netbox")
    return rv


def get_all_ip_prefixes(nb) -> dict:
    return dict(nb.ipam.prefixes.all())


def show_all_ip_prefixes(nb) -> None:
    prefixes = nb.ipam.prefixes.all()
    for pf in prefixes:
        print(pf)


def check_if_device_name_exists(nb, device_name: str) -> bool:
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
    """Using just the IP, map to the device"""
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
                print(f"assigned object.device.name: {result.assigned_object.device.name}")
            if result.assigned_object.device.url:
                print(f"assigned object.device.url: {result.assigned_object.device.url}")
            if result.assigned_object.device.display:
                print(f"assigned object.device.display: {result.assigned_object.device.display}")
            
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
        ndev_site: int = nb.dcim.sites.get(name=site)
        if ndev_site is not None:
            return ndev_site.id
    except pynetbox.RequestError as e:
        print(e.error)


def get_device_type_id(nb, device_type: str):
    """retrieve a specific device type id"""
    try:
        ndev_type: int = nb.dcim.device_types.get(model=device_type)
        if ndev_type is not None:
            return ndev_type.id
    except pynetbox.RequestError as e:
        print(e.error)


def get_device_role_id(nb, device_role: str):
    """retrieve a specific device role id"""
    try:
        ndev_role: int = nb.dcim.device_roles.get(name=device_role)
        if ndev_role is not None:
            return ndev_role.id
    except pynetbox.RequestError as e:
        print(e.error)


def create_netbox_device(nb, device_name: str, site: str, device_type: str, device_role:str) -> str:
    """add a device into Netbox"""
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


def delete_netbox_device(nb, device_name: str):
    """
    delete a netbox device
    Note: the device must be in the status 'decommissioning' to be deleted
    """
    ndev_device= nb.dcim.devices.get(name=device_name)
    if ndev_device is not None:
        ndev_device.delete()
    else:
        print(f"device name {device_name} not found")

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
        print(f"change the status for {cidr}")
        print(dir(response))
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
        for contact in contacts:
            print(f"{contact.name}, {contact.title}, {contact.tags}")
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False
