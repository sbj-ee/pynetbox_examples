# pynetbox_examples
Helpful examples for Netbox

I beat my head against the wall today attempting to change the `Status` for IP addresses. It wasn't clear that the status needed to be lower case. I have examples here which show how one can change different attributes for the Netbox ipam items. If it saves anybody time and frustration, then putting information here will have been my contribution to world happiness.

I'll try to add more examples as I proceed figuring out the different APIs and their nuances.

`netboxlib.py` is the primary code that I'm working on for generic usage.  All the other python files are either testing or being used to determine the pynetbox/netbox usage for something.

`ip_info.py` is where I'm trying out the `ipaddress` module and I'll be making use of it for some of the netboxlib in the near future.

# NetboxClient class
I'm pulling all my netboxlib.py functions into a `NetboxClient` class.
