"""
Script to retrieve all BGP sessions from NetBox.
"""
import sys
import os
from loguru import logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils.netboxlib import connect_netbox
import urllib3
from netbox_utils.BgpSession import BgpSession

urllib3.disable_warnings()


def get_all_netbox_bgp_sessions(nb) -> dict:
    """Get all the BGP Sessions from Netbox and stuff them into a dict of BgpSession objects"""
    bgp_sessions = nb.plugins.bgp.session.all()
    bgp_sess_dict = dict()
    for session in bgp_sessions:
        # logger.debug(f"{session.id}, {session.name}, {session.remote_address}, {session.local_address}")
        
        # Handle cases where attributes might be None or objects
        remote_ip = str(session.remote_address) if session.remote_address else "0.0.0.0/0"
        local_ip = str(session.local_address) if session.local_address else "0.0.0.0/0"
        
        bgp_key: str = f"{remote_ip.split('/')[0]}_{local_ip.split('/')[0]}"
        
        bgp_obj = BgpSession(
            id=session.id,
            device=str(session.device) if session.device else "",
            name=session.name,
            remote_as=session.remote_as.asn if session.remote_as else 0,
            remote_addr=remote_ip,
            local_as=session.local_as.asn if session.local_as else 0,
            local_addr=local_ip,
            status=str(session.status),
            description=session.description if hasattr(session, 'description') else "",
            site=str(session.site) if hasattr(session, 'site') and session.site else "",
            comments=session.comments if hasattr(session, 'comments') else ""
        )
        
        bgp_sess_dict[bgp_key] = bgp_obj
        
    return bgp_sess_dict

if __name__ == "__main__":
    nb = connect_netbox()
    all_sessions = get_all_netbox_bgp_sessions(nb)
    logger.info(f"len is {len(all_sessions)}")

    # logger.info(f"test case {all_sessions['69.11.245.66']}")
