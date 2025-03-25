from netboxlib import connect_netbox
import urllib3
from pprint import pprint
from tenacity import retry

urllib3.disable_warnings()


def get_all_netbox_bgp_sessions(nb) -> dict:
    bgp_sessions = nb.plugins.bgp.session.all()
    bgp_sess_dict = dict()
    for session in bgp_sessions:
        print(session.id, session.name)
        bgp_sess_dict[str(session.remote_address).split('/')[0]] = {
            "id": session.id,
            "device": session.device,
            "name": session.name,
            "remote_as": session.remote_as,
            "remote_address": session.remote_address,
            "local_as": session.local_as,
            "local_address": session.local_address,
            "status": session.status
        }
    return bgp_sess_dict

if __name__ == "__main__":
    nb = connect_netbox()
    all_sessions = get_all_netbox_bgp_sessions(nb)
    pprint(all_sessions)
