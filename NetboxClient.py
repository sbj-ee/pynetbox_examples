import pynetbox
from loguru import logger


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

    @staticmethod
    def setup_logging() -> None:
        """Configure the logging."""
        logger.remove()
        logger.add("./netbox.log")
        logger.info("Logging configured...")

    def get_pynetbox_version(self) -> str:
        """get the netbox version"""
        return str(self.nb.status()["netbox-version"])


if __name__ == "__main__":
    netbox_url = ""
    netbox_token = ""
    nb_client = NetboxClient(netbox_url, netbox_token)
    nb_client.setup_logging()
    nb_client.connect()
    print(nb_client.get_pynetbox_version())
