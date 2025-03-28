from pprint import pprint


remote_address = "66.66.66.66"
local_address = "55.55.55.55"

remote_as = 12345
local_as = 4181

site = "ATLNGAMQ"
device = "ATLNGAMQcor51"
bgp_name = "Yadda"

bgp_sess = {
    'site': site,
    'device': device,
    'local_address': local_address,
    'local_as': local_as,
    'remote_address': remote_address,
    'remote_as': remote_as
}


# this is what I'm testing - need a better key
# just using the remote_address alone was not distinct enough
bgp_sess_dict_key = f"{remote_address}_{local_address}"

bgp_sess_dict = {bgp_sess_dict_key: bgp_sess}

pprint(bgp_sess_dict)

# I'll pull the info from the router and create the key
my_router_data_key = f"{remote_address}_{local_address}"
print(bgp_sess_dict[my_router_data_key])