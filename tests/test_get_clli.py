import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils.get_clli_from_device import get_clli_from_device, get_netbox_site_name

def test_get_clli_from_device_variations():
    # 13 chars
    assert get_clli_from_device("ATLNGAMQcor51.network.tds.net") == "ATLNGAMQ"
    # 11 chars
    assert get_clli_from_device("CNTCNHdst51") == "CNTCNH"
    # 16 chars (CCW specific)
    assert get_clli_from_device("MDSNWIVU01Ndst53.network.teldta.com") == "MDSNWIVU01N"
    # Unknown length
    # Note: Function prints error but returns empty string or whatever clli was initialized to?
    # Actually looking at code: clli = "" initially.
    assert get_clli_from_device("short") == ""

def test_get_netbox_site_name_lookup():
    assert get_netbox_site_name("ATLNGAMQ") == "ATLNGAMQ - Atlanta Digital Reality"
    
def test_get_netbox_site_name_key_error():
    with pytest.raises(KeyError):
        get_netbox_site_name("UNKNOWN")
    