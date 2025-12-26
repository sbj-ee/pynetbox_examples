import ipaddress

def is_valid_cidr(cidr: str) -> bool:
    # Explicitly check for prefix
    if '/' not in cidr:
        return False
    try:
        ipaddress.ip_network(cidr, strict=True)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    # Test cases
    test_cases = [
        "192.168.1.0/24",      # Valid
        "10.0.0.0/8",          # Valid
        "192.168.1.0",         # Invalid (no prefix)
        "256.1.2.3/24",        # Invalid IP
        "192.168.1.0/33",      # Invalid prefix
    ]

    for cidr in test_cases:
        print(f"{cidr}: {'Valid' if is_valid_cidr(cidr) else 'Invalid'}")