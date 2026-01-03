import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from netbox_utils.validate_cidr import is_valid_cidr


def test_valid_cidrs():
    assert is_valid_cidr("192.168.1.0/24") is True
    assert is_valid_cidr("10.0.0.0/8") is True
    assert is_valid_cidr("172.16.0.0/12") is True
    assert is_valid_cidr("2001:db8::/32") is True  # IPv6


def test_invalid_cidrs():
    assert is_valid_cidr("192.168.1.0") is False  # Missing prefix
    assert is_valid_cidr("256.1.2.3/24") is False  # Invalid octet
    assert is_valid_cidr("192.168.1.0/33") is False  # Invalid prefix length
    assert is_valid_cidr("garbage") is False
    assert is_valid_cidr("") is False
    assert is_valid_cidr("192.168.1.1/-1") is False
