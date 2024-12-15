"""
Add an entire subnet for a specified cidr
It will mark the network and broadcast addresses as Reserved
"""

import sys
import argparse
from ipaddress import ip_network
from ipaddress import IPv4Interface, IPv4Network
import urllib3
from dotenv import dotenv_values
from loguru import logger
import pynetbox
from netboxlib import add_ipv4_ip

urllib3.disable_warnings()

def main(cidr: str):
    """main code for adding the subnet"""

    try:
        ifc: IPv4Interface = IPv4Interface(cidr)
        nm: str = cidr.split('/', maxsplit=1)[1]
    except Exception as e:
        logger.info(f"invalid cidr: {cidr}")
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
            ip = str(host).split('/', maxsplit=1)[0]
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
    parser.add_argument('-c', '--cidr', type=str, required=True, help="indicate the cidr")
    args = parser.parse_args()
    logger.info(f"cidr passed: {args.cidr}")

    config = dotenv_values("netbox.env")
    try:
        token = config['token']
        url = config['url']
    except KeyError as e:
        print(f"key missing from env file: {e}")
        sys.exit()

    logger.info(f"netbox url: {url}")

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    main(args.cidr)
