import pytest
import sys
import os
import logging
from loguru import logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from netbox_utils.ip_info import ip_info


class PropagateHandler(logging.Handler):
    def emit(self, record):
        logging.getLogger(record.name).handle(record)


@pytest.fixture(autouse=True)
def caplog_propagate(caplog):
    handler_id = logger.add(PropagateHandler(), format="{message}")
    yield
    logger.remove(handler_id)


def test_ip_info_ipv4(caplog):
    # Ensure info level is captured
    caplog.set_level(logging.INFO)
    ip_info("192.168.1.1/24")

    # Check assertions in caplog.text
    assert "CIDR    192.168.1.1/24" in caplog.text
    assert "IPv4    192.168.1.1" in caplog.text
    assert "private IP" in caplog.text


def test_ip_info_ipv4_public(caplog):
    caplog.set_level(logging.INFO)
    ip_info("8.8.8.8/32")
    assert "IPv4    8.8.8.8" in caplog.text
    # Should NOT say private IP
    assert "private IP" not in caplog.text


def test_ip_info_ipv6(caplog):
    caplog.set_level(logging.INFO)
    ip_info("2001:db8::1/128")
    assert "IPv6    2001:db8::1" in caplog.text
    assert "number of addresses: 1" in caplog.text
