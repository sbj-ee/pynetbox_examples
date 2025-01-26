from dotenv import dotenv_values
import pynetbox
import sys
import urllib3

urllib3.disable_warnings()


def nb_change_ip_status(cidr: str, status: str) -> bool:
    config = dotenv_values("netbox.env")
    try:
        token = config["token"]
        url = config["url"]
    except KeyError as e:
        print(f"key missing from env file: {e}")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    try:
        response = nb.ipam.ip_addresses.get(address=cidr)
        print(f"change the status for {cidr}")
        print(dir(response))
        # print(f"id = {response.id}")
        # print(f"url = {response.url}")
        response.status = status.lower()
        response.save()
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False


if __name__ == "__main__":
    cidr = "66.66.66.1/29"
    status = "Reserved"
    nb_change_ip_status(cidr, status)
