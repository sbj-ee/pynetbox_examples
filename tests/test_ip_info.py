import pytest
import sys
import os
from io import StringIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from netbox_utils.ip_info import ip_info

def test_ip_info_ipv4(capsys):
    ip_info("192.168.1.1/24")
    captured = capsys.readouterr()
    assert "CIDR    192.168.1.1/24" in captured.out
    assert "IPv4    192.168.1.1" in captured.out
    assert "private IP" in captured.out

def test_ip_info_ipv4_public(capsys):
    ip_info("8.8.8.8/32")
    captured = capsys.readouterr()
    assert "IPv4    8.8.8.8" in captured.out
    # Should NOT say private IP
    assert "private IP" not in captured.out

def test_ip_info_ipv6(capsys):
    ip_info("2001:db8::1/128")
    captured = capsys.readouterr()
    assert "IPv6    2001:db8::1" in captured.out
    assert "number of addresses: 1" in captured.out
