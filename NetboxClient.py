import pynetbox
from loguru import logger
from ipaddress import IPv4Network
from ipaddress import IPv4Interface
from ipaddress import IPv6Network
from ipaddress import IPv6Interface


class NetboxClient:
    """A client for using the Netbox API"""

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.nb = None

    def connect(self):
        """Get the connection handle for Netbox."""
        self.nb = pynetbox.api(url=self.url, token=self.token)
        self.nb.http_session.verify = False

    def setup_logging(self) -> None:
        """Configure the logging."""
        logger.remove()
        logger.add("./netbox.log")
        logger.info("Logging configured...")

    def get_pynetbox_version(self) -> str:
        """get the netbox version"""
        return str(self.nb.status()["netbox-version"])


if __name__ == "__main__":
    url = ""
    token = ""
    nb_client = NetboxClient(url, token)
    nb_client.setup_logging()
    nb_client.connect()
    print(nb_client.get_pynetbox_version())
