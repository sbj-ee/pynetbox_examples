# pynetbox_examples

This repository contains a collection of Python scripts and utilities for interacting with NetBox using the `pynetbox` library. It includes a reusable library `netbox_utils` and various operational scripts to automate common network automation tasks such as managing IP addresses, devices, interfaces, and BGP sessions.

## Directory Structure

*   **`netbox_utils/`**:  A Python package containing reusable libraries and helper classes.
    *   `NetboxClient.py`: A comprehensive wrapper class for interacting with the NetBox API.
    *   `netboxlib.py`: A collection of utility functions for common NetBox operations.
    *   `ip_info.py`:  Utilities for extracting and displaying IP address information.
    *   `validate_cidr.py`: Functions for validating CIDR notations.
    *   `BgpSession.py`: A dataclass representing a BGP session.
    *   `get_clli_from_device.py`: Logic to extract CLLI codes from device names.
    *   `netbox_interface_types.py`: Mapping of interface types to NetBox slugs.

*   **`scripts/`**: Executable scripts for performing specific tasks.
    *   `manage_vlans.py`: **[NEW]** CLI tool to create VLANs and VLAN Groups.
    *   `add_ipv4_subnet.py`: Adds an entire IPv4 subnet and its host IPs to NetBox.
    *   `bgp_session_add.py`: Automates the addition of BGP sessions.
    *   `bgp_to_sqlite.py`: Exports BGP session data to a SQLite database.
    *   `change_cisco_interface_names.py`: Renames interfaces on Cisco devices in NetBox.
    *   `find_dupe_ip.py`: Identifies duplicate IP addresses in NetBox.
    *   `get_all_netbox_bgp_sessions.py`: Retrieves and lists all BGP sessions.
    *   `move_interfaces.py`: Moves interfaces from one device to another (via cloning).
    *   `sync_iosxr_interfaces.py`: Synchronizes interfaces from IOS-XR devices.
    *   `cisco_interface_validator.py`: Validates Cisco interface naming.
    *   `edit_bgp_session.py`: Modify existing BGP sessions.
    *   `get_device_interfaces.py`: List all interfaces on a device.
    *   `get_interface_id.py`: Retrieve interface IDs by name.
    *   `get_maintenance_count.py`: Count devices in maintenance mode.
    *   `get_maintenance_value.py`: Get maintenance status values.
    *   And additional utility scripts (22 total).

*   **`tests/`**: Unit and integration tests using `pytest`.
    *   `test_netbox_client.py`: Unit tests for the `NetboxClient` class (using mocks).
    *   `test_move_interfaces.py`: Unit and logic tests for interface moving script.
    *   `test_integration_move_interfaces.py`: Live integration test for interface moving.
    *   `test_vlans.py`: Tests for VLAN management.
    *   `test_validate_cidr.py`: Unit tests for CIDR validation logic.
    *   `test_ip_info.py`: Tests for IP information display.
    *   `test_ip_add.py`: Integration tests for adding IPs (requires live NetBox).
    *   `test_contact.py`: Integration tests for contact management.

## Prerequisites

*   Python 3.10+
*   A NetBox instance (v3.5+ recommended)
*   `pip` for installing dependencies

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/stevebj/pynetbox_examples.git
    cd pynetbox_examples
    ```

2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt

    # For development (includes test dependencies)
    pip install -r requirements-dev.txt
    ```

## Configuration

The scripts use environment variables for authentication. You must export the following variables in your shell before running any script:

### NetBox Credentials
```bash
export NETBOX_URL="https://your-netbox-url.com"
export NETBOX_TOKEN="your-api-token"
```

### Device Credentials (for scripts that connect to routers)
```bash
# Production environment
export CISCO_PROD_USERNAME="your-username"
export CISCO_PROD_PASSWORD="your-password"

# Lab environment (optional)
export CISCO_LAB_USERNAME="your-lab-username"
export CISCO_LAB_PASSWORD="your-lab-password"
```

Scripts that connect to devices accept an `-e/--env` flag to select the environment (defaults to `prod`):
```bash
python scripts/bgp_to_sqlite.py -r router.example.com -e prod
python scripts/sync_iosxr_interfaces.py -r router.example.com -e lab
```

> **Note**: These scripts use `ssl_verify=False` by default for ease of use in lab environments with self-signed certificates.

## Usage

### Running Scripts

You can run any script from the root directory. The scripts resolve imports automatically.

**Example: Adding a BGP Session**
```bash
python scripts/bgp_session_add.py --name "Peer-1" --local_as 65001 --remote_as 65002 --device "Router-A" ...
```

**Example: Finding Duplicate IPs**
```bash
python scripts/find_dupe_ip.py
```

### Running Tests

To run the full test suite with coverage report:

```bash
pytest --cov=netbox_utils tests
```

To run a specific test file:

```bash
pytest tests/test_validate_cidr.py
```

## Contributing

1.  Create a feature branch.
2.  Add your changes.
3.  Ensure all tests pass (`pytest`).
4.  Add new tests for new functionality.

## Test Descriptions

This project includes a comprehensive test suite covering both unit logic and integration with a live NetBox instance.

### Unit Tests
These tests use mocks or simple logic verification and do not require a connection to a live NetBox instance.

*   **`tests/test_bgp_session.py`**: Tests the `BgpSession` dataclass to ensure valid instantiation and default values.
*   **`tests/bgp_session_dict_test.py`**: Validates helper functions that extract site names and CLLI codes for BGP configurations.
*   **`tests/test_get_clli.py`**: Unit tests for converting device names to CLLI codes and Site names.
*   **`tests/test_ip_info.py`**: Verifies that the `ip_info` utility correctly parses and logs details about IPv4 and IPv6 addresses.
*   **`tests/test_interface_types.py`**: Validates the mapping dictionary of interface types to NetBox slugs.
*   **`tests/test_move_interfaces.py`**: Tests the logic of the `move_interfaces` script using mocks, ensuring it attempts to clone and delete interfaces correctly.
*   **`tests/test_netbox_client.py`**: Comprehensive unit tests for the `NetboxClient` wrapper class.
*   **`tests/test_netbox_manager.py`**: Unit tests for the `NetboxManager` class.
*   **`tests/test_netboxlib.py`**: Unit tests for the library of utility functions in `netboxlib.py`.
*   **`tests/test_validate_cidr.py`**: Tests the `is_valid_cidr` function with various valid and invalid input strings.
*   **`tests/test_vlans.py`**: Mocks NetBox API calls to verify the logic for creating and retrieving VLANs and VLAN Groups.

### Integration Tests
These tests **REQUIRE** a live NetBox instance and valid `NETBOX_URL` / `NETBOX_TOKEN` environment variables. They create, modify, and delete real data.

*   **`tests/test_contact.py`**: specific tests for creating, modifying, and deleting Contact objects.
*   **`tests/test_integration_move_interfaces.py`**: End-to-end test that creates sites, devices, and interfaces, then runs the `move_interfaces` script to verify it works against a real API.
*   **`tests/test_ip_add.py`**: Tests adding IPv4 and IPv6 addresses to NetBox IPAM.
*   **`tests/test_prefix.py`**: Tests the lifecycle (add, list, delete) of IP Prefixes.
