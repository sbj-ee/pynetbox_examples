"""
Using Netbox, you often need to use the CIDR for the ip_address. Here's a way to validate the CIDR.
"""

import ipaddress

def is_valid_cidr(cidr: str) -> bool:
    """
    Validate if a given string is a valid CIDR notation.
    
    Args:
        cidr: String in CIDR format (e.g., '192.168.1.0/24')
        
    Returns:
        bool: True if valid CIDR, False otherwise
    """
    try:
        # Attempt to create an IP network object
        ipaddress.ip_network(cidr, strict=True)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
  print(f"{is_valid_cidr('10.16.252.20/24')}")
  print(f"{is_valid_cidr('10.16.252.20')}")
  print(f"{is_valid_cidr('2001:db8::/32')}")
  print(f"{is_valid_cidr('2001:db8::/129')}")
  
