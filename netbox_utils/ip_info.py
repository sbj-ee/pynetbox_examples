import ipaddress
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from ipaddress import IPv4Interface
from ipaddress import ip_network


from loguru import logger

def ip_info(cidr: str) -> None:
    """Provide information about the IP address"""

    logger.info(f"CIDR    {cidr}")
    ip = cidr.split("/")[0]
    if ipaddress.ip_address(ip).version == 4:
        logger.info(f"cidr = {cidr}")
        net = ipaddress.ip_network(cidr, strict=False).netmask

        # concatenate the IP and Netmask
        check_this: str = f"{ip}/{net}"

        logger.info(f"IPv4    {ip}")
        logger.info(f"inet_aton: {int(ipaddress.IPv4Address(ip))}")

        if IPv4Address(ip).is_private:
            logger.info("private IP")

        if IPv4Address(ip).is_multicast:
            logger.info("multicast IP")

        ifc: IPv4Interface = IPv4Interface(check_this)
        logger.info(f"ifc.ip = {ifc.ip}")
        logger.info(f"ifc.network = {ifc.network}")
        net: IPv4Network = IPv4Network(ifc.network)
        logger.info(f"broadcast address: {net.broadcast_address}")
        logger.info(f"number of addresses: {str(net.num_addresses)}")
        subnet_host_list: list = list(ip_network(ifc.network).hosts())

        logger.info("usable host IPs:")
        for host in subnet_host_list:
            logger.info(host)

    elif ipaddress.ip_address(ip).version == 6:
        logger.info(f"IPv6    {ip}")
        logger.info(f"inet_aton: {int(ipaddress.IPv6Address(ip))}")
        net6 = ipaddress.ip_network(cidr, strict=False)
        logger.info(f"number of addresses: {str(net6.num_addresses)}")
