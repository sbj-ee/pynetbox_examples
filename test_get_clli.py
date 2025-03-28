from get_clli_from_device import get_clli_from_device, get_netbox_site_name

def test_get_clli_from_device():
    clli = get_clli_from_device("atlngamqcor51.network.tds.net")
    assert(clli == "ATLNGAMQ")

def test_get_netbox_site_name():
    site_name = get_netbox_site_name(get_clli_from_device("atlngamqcor51.network.tds.net"))
    assert(site_name == "ATLNGAMQ - Atlanta Digital Reality")
    