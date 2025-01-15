"""Add a BGP Session into Netbox"""
import argparse
from dotenv import dotenv_values
from loguru import logger
import pynetbox
import sys
import urllib3

urllib3.disable_warnings()
from BgpSession import BgpSession
from pprint import pprint


def check_bgp_session_exists(nb, bgp_session_object: BgpSession) -> bool:
    """check if the BGP Session already exists in Netbox"""
    remote_addr = nb.ipam.ip_addresses.get(address=bgp_session_object.remote_addr)

    if remote_addr:
        print(f"remote_ip is ok: {remote_addr}")
    else:
        print(f"remote_ip {bgp_session_object.remote_addr} was not found")

    sessions = nb.plugins.bgp.session.all()
    exists_flag: bool = False
    for session in sessions:
        print(f"{session.remote_address}")
        print(f"{bgp_session_object.remote_addr}")
        if str(session.remote_address) == str(bgp_session_object.remote_addr):
            exists_flag = True

    return exists_flag

def get_asn_object(nb, bgp_session_object: BgpSession):
    ...


def get_ip_object(nb):
    ...


def main(bgp_session_object: BgpSession):
    config = dotenv_values("netbox.env")
    try:
        token = config['token']
        url = config['url']
    except KeyError as e:
        print(f"key missing from env file: {e}")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False
    session_dict = dict()
    session_dict['name'] = bgp_session_object.name
    session_dict['description'] = bgp_session_object.description
    session_dict['comments'] = bgp_session_object.comments
    local_as = nb.ipam.asns.get(asn=bgp_session_object.local_as)
    session_dict['local_as'] = local_as.id
    remote_as = nb.ipam.asns.get(asn=bgp_session_object.remote_as)
    session_dict['remote_as'] = remote_as.id
    local_addr = nb.ipam.ip_addresses.get(address=bgp_session_object.local_addr)
    session_dict['local_address'] = local_addr.id
    remote_addr = nb.ipam.ip_addresses.get(address=bgp_session_object.remote_addr)
    session_dict['remote_address'] = remote_addr.id
    session_dict['status'] = bgp_session_object.status

    pprint(session_dict)

    session_exists: bool = check_bgp_session_exists(nb, bgp_session_object)
    print(f"session_exists: {session_exists}")

    if session_exists:
        sys.exit()

    try:
        response = nb.plugins.bgp.session.create(session_dict)
        return response.status
    except Exception as e:
        print(f"Exception: {e}")
        return "Unknown"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--name', type=str, required=True, help="BGP Session name")
    parser.add_argument('--description', type=str, required=False,  default="", help="BGP Session description")
    parser.add_argument('--comments', type=str, required=False, default="", help="BGP Session comments")
    parser.add_argument('--local_as', type=int, required=True, help="BGP Session local_as AS number only")
    parser.add_argument('--remote_as', type=int, required=True, help="BGP Session remote_as AS number only")
    parser.add_argument('--local_address', type=str, required=True, help="BGP Session local_address as a CIDR")
    parser.add_argument('--remote_address', type=str, required=True, help="BGP Session remote_address as a CIDR")
    parser.add_argument('-d', '--device', type=str, required=True, help="Device name")
    parser.add_argument('--status', type=str, required=True, help="BGP Session status")
    args = parser.parse_args()

    # create a BGP Session object for passing around
    bgp_session_obj = BgpSession(
        name=args.name,
        description=args.description,
        comments=args.comments,
        local_as=args.local_as,
        remote_as=args.remote_as,
        device=args.device,
        status=str(args.status).lower(),
        local_addr=args.local_address,
        remote_addr=args.remote_address
    )

    main(bgp_session_obj)

