from dotenv import dotenv_values
import pynetbox
import sys
import urllib3
urllib3.disable_warnings()


def nb_get_ip_status(cidr: str) -> str:
    config = dotenv_values("netbox.env")
    try:
        token = config['token']
        url = config['url']
    except KeyError as e:
        print(f"key missing from env file: {e}")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    try:
        response = nb.ipam.ip_addresses.get(address=cidr)
        return response.status
    except Exception as e:
        print(f"Exception: {e}")
        return "Unknown"


if __name__ == "__main__":
    cidr = "66.66.66.1/29"
    desc = "This is a test"
    status = nb_get_ip_status(cidr)
    print(status)
