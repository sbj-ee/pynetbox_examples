import argparse
import sqlite3
import sys
import os
import re
from netmiko import ConnectHandler
from datetime import datetime

# Add parent directory to path for credentials module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from credentials import get_credentials


def create_database():
    # Connect to SQLite database (creates if doesn't exist)
    conn = sqlite3.connect("bgp_neighbors.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bgp_neighbors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            router_name TEXT,
            neighbor_ip TEXT,
            as_number TEXT,
            state TEXT,
            prefix_received INTEGER,
            timestamp TEXT
        )
    """
    )
    conn.commit()
    return conn


def parse_bgp_output(output, router_name):
    # Regular expression to match BGP neighbor lines
    # Adjust pattern based on actual output format
    pattern = r"(\S+)\s+(\d+)\s+(\d+)\s+([^\n]+?)\s+([\d\w:]+)\s+(\S+)"
    neighbors = []

    for line in output.splitlines():
        match = re.match(pattern, line.strip())
        if match:
            neighbor_ip = match.group(1)
            as_number = match.group(3)
            state = match.group(6)
            prefix_received = int(match.group(4)) if match.group(4).isdigit() else 0
            neighbors.append(
                {
                    "neighbor_ip": neighbor_ip,
                    "as_number": as_number,
                    "state": state,
                    "prefix_received": prefix_received,
                }
            )
    return neighbors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--env",
        type=str,
        required=False,
        default="prod",
        help="specify the environment (prod, lab)",
    )
    parser.add_argument(
        "-r", "--router", type=str, required=True, help="indicate the router"
    )
    args = parser.parse_args()

    # Get credentials from environment variables
    username, password = get_credentials()

    # Router configuration
    routers = [
        {
            "device_type": "cisco_ios",
            "host": args.router,
            "username": username,
            "password": password,
        },
    ]

    conn = create_database()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for router in routers:
        router_name = router["host"]
        try:
            print(f"Connecting to {router_name}...")
            # Establish SSH connection
            net_connect = ConnectHandler(**router)

            # Execute command
            output = net_connect.send_command("show bgp neighbor brief wide")

            # Parse output
            neighbors = parse_bgp_output(output, router_name)

            # Insert data into database
            for neighbor in neighbors:
                cursor.execute(
                    """
                    INSERT INTO bgp_neighbors (router_name, neighbor_ip, as_number, state, prefix_received, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        router_name,
                        neighbor["neighbor_ip"],
                        neighbor["as_number"],
                        neighbor["state"],
                        neighbor["prefix_received"],
                        timestamp,
                    ),
                )

            print(f"Successfully processed {router_name}")
            net_connect.disconnect()

        except Exception as e:
            print(f"Error processing {router_name}: {str(e)}")

        # Commit changes after each router
        conn.commit()

    # Close database connection
    conn.close()
    print("Data collection complete. Results stored in bgp_neighbors.db")


if __name__ == "__main__":
    main()
