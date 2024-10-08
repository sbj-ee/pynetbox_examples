from dotenv import dotenv_values
import pynetbox
import sys
from pprint import pprint
from time import sleep
import urllib3
urllib3.disable_warnings()


def test_add_contact() -> None:
    config = dotenv_values(".env.netbox.sbj.dev")

    try:
        token = config['token']
        url = config['url']
    except KeyError:
        print("key missing from env file")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    contact_name: str = "Bob Dole"

    rv = nb.tenancy.contacts.create(name=contact_name)

    if rv:
        assert True
    else:
        assert False


def test_delete_contact():
    config = dotenv_values(".env.netbox.sbj.dev")

    try:
        token = config['token']
        url = config['url']
    except KeyError:
        print("key missing from env file")
        sys.exit()

    nb = pynetbox.api(url=url, token=token)
    nb.http_session.verify = False

    contact_name: str = "Bob Dole"

    contact_ref = nb.tenancy.contacts.get(name=contact_name)
    print(f"contact_ref = {contact_ref}   type={type(contact_ref)}")
    # print(dir(contact_ref))
    print(f"contact id = {contact_ref.id}")
    print(f"contact name = {contact_ref.name}")

    rv = nb.tenancy.contacts.delete([contact_ref])
    
    if rv:
        assert True
    else:
        assert False


if __name__ == "__main__":
    test_add_contact()
    sleep(10)
    test_delete_contact()
