from pprint import pprint
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils.get_clli_from_device import get_clli_from_device, get_netbox_site_name


def test_bgp_session_dict():
    remote_address = "66.66.66.66"
    local_address = "55.55.55.55"

    remote_as = 12345
    local_as = 4181

    device = "ATLNGAMQcor51"
    site = get_netbox_site_name(get_clli_from_device(device))
    bgp_name = "Yadda"

    bgp_sess = {
        'site': site,
        'device': device,
        'local_address': local_address,
        'local_as': local_as,
        'remote_address': remote_address,
        'remote_as': remote_as
    }

    # this is what I'm testing - need a better key
    # just using the remote_address alone was not distinct enough
    bgp_sess_dict_key = f"{remote_address}_{local_address}"

    bgp_sess_dict = {bgp_sess_dict_key: bgp_sess}

    pprint(bgp_sess_dict)

    # I'll pull the info from the router and create the key
    my_router_data_key = f"{remote_address}_{local_address}"
    
    assert bgp_sess_dict[my_router_data_key] == bgp_sess
    assert bgp_sess_dict[my_router_data_key]['site'] == "ATLNGAMQ - Atlanta Digital Reality"