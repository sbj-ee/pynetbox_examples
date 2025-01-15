from dataclasses import dataclass


@dataclass
class BgpSession:
    name: str
    description: str
    local_addr: str
    local_as: int
    remote_addr: str
    remote_as: int
    device: str
    comments: str
    status: str


if __name__ == "__main__":
    bgp_sess = BgpSession(
        name="Test",
        description="Test",
        local_addr="10.10.10.10/31",
        local_as=4181,
        remote_addr="10.10.10.11/31",
        remote_as=11111,
        status="active",
        device="CHCGILDTcor51",
        comments=""
    )

    print(bgp_sess)
