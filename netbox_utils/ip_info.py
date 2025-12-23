import ipaddress
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from ipaddress import IPv4Interface
from ipaddress import ip_network


def ip_info(cidr: str) -> None:
    """Provide information about the IP address"""

    print(f"CIDR    {cidr}")
    ip = cidr.split("/")[0]
    if ipaddress.ip_address(ip).version == 4:
        print(f"cidr = {cidr}")
        net = ipaddress.ip_network(cidr, strict=False).netmask

        # concatenate the IP and Netmask
        check_this: str = f"{ip}/{net}"

        print(f"IPv4    {ip}")
        print(f"inet_aton: {int(ipaddress.IPv4Address(ip))}")

        if IPv4Address(ip).is_private:
            print("private IP")

        if IPv4Address(ip).is_multicast:
            print("multicast IP")

        ifc: IPv4Interface = IPv4Interface(check_this)
        print(f"ifc.ip = {ifc.ip}")
        print(f"ifc.network = {ifc.network}")
        net: IPv4Network = IPv4Network(ifc.network)
        print(f"broadcast address: {net.broadcast_address}")
        print(f"number of addresses: {str(net.num_addresses)}")
        subnet_host_list: list = list(ip_network(ifc.network).hosts())

        print("usable host IPs:")
        for host in subnet_host_list:
            print(host)

    elif ipaddress.ip_address(ip).version == 6:
        print(f"IPv6    {ip}")
        print(f"inet_aton: {int(ipaddress.IPv6Address(ip))}")
        net6 = ipaddress.ip_network(cidr, strict=False)
        print(f"number of addresses: {str(net6.num_addresses)}")


if __name__ == "__main__":
    ip6 = "2001:db8::1/127"
    ip_info(ip6)
    print("----")
    ip4 = "10.10.10.10/31"
    ip_info(ip4)
