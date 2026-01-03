import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from netbox_utils.BgpSession import BgpSession


def test_bgp_session_instantiation():
    session = BgpSession(
        name="Test-BGP",
        description="Test Description",
        site="Test-Site",
        local_addr="192.168.1.1/30",
        local_as=65001,
        remote_addr="192.168.1.2/30",
        remote_as=65002,
        device="Test-Device",
        comments="No comments",
        status="active",
    )

    assert session.name == "Test-BGP"
    assert session.local_as == 65001
    assert session.remote_addr == "192.168.1.2/30"
    assert session.status == "active"
