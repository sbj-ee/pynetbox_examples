from dataclasses import dataclass
from .get_clli_from_device import get_clli_from_device, get_netbox_site_name


@dataclass
class BgpSession:
    name: str
    description: str
    site: str
    local_addr: str
    local_as: int
    remote_addr: str
    remote_as: int
    device: str
    comments: str
    status: str
    id: int = None


if __name__ == "__main__":
    bgp_sess = BgpSession(
        name="Test",
        description="Test",
        site="",
        local_addr="10.10.10.10/31",
        local_as=4181,
        remote_addr="10.10.10.11/31",
        remote_as=11111,
        status="active",
        device="CHCGILDTcor51.network.tds.net",
        comments="",
    )

    bgp_sess.site = get_netbox_site_name(get_clli_from_device(bgp_sess.device))
    print(bgp_sess)
