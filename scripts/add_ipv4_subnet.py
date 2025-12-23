"""
Add an entire subnet for a specified cidr
It will mark the network and broadcast addresses as Reserved
"""

import sys
import argparse
from ipaddress import ip_network
from ipaddress import IPv4Interface, IPv4Network
import urllib3
from os import getenv
from loguru import logger
import pynetbox
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils.netboxlib import add_ipv4_ip

urllib3.disable_warnings()


def main(cidr: str):
    """main code for adding the subnet"""

    try:
        ifc: IPv4Interface = IPv4Interface(cidr)
        nm: str = cidr.split("/", maxsplit=1)[1]
    except Exception as e:
        logger.info(f"invalid cidr: {cidr} {e}")
        sys.exit()

    if int(nm) <= 22:
        proceed: str = input(f"A large subnet - Are you sure? Y or N: ")
        if proceed.lower() != "y":
            logger.info("Exiting - proceed check was {proceed}")
            sys.exit()

    net: IPv4Network = IPv4Network(ifc.network)

    # add the subnet and broadcast
    logger.info(f"adding network address: {str(ifc.network)}")
    rv = add_ipv4_ip(nb, str(ifc.network))
    logger.info(f"result: {rv}")
    bcast_addr: str = f"{net.broadcast_address}/{nm}"
    logger.info(f"adding broadcast address: {bcast_addr}")
    rv = add_ipv4_ip(nb, bcast_addr)
    logger.info(f"result: {rv}")

    # add all the host ip addresses
    try:
        subnet_host_list: list = list(ip_network(ifc.network).hosts())
        logger.info("adding all hosts")
        for host in subnet_host_list:
            ip = str(host).split("/", maxsplit=1)[0]
            ip_addr: str = f"{ip}/{nm}"
            logger.info(f"adding host: {ip_addr}")
            rv = add_ipv4_ip(nb, ip_addr)
            logger.info(f"result: {rv}")
    except Exception as e:
        logger.debug(f"Exception {e}")

    logger.info("Completed")


if __name__ == "__main__":
    logger.remove()
    logger.add("./netbox.log")
    logger.info("Executing add_ipv4_subnet.py")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--cidr", type=str, required=True, help="indicate the cidr"
    )
    args = parser.parse_args()
    logger.info(f"cidr passed: {args.cidr}")

    token = getenv("NETBOX_TOKEN")
    url = getenv("NETBOX_URL")

    if not token or not url:
        print("NETBOX_TOKEN or NETBOX_URL missing from environment variables")
        sys.exit()

    logger.info(f"netbox url: {url}")

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    main(args.cidr)
