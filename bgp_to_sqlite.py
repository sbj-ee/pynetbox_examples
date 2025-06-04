import sqlite3
import netmiko
from datetime import datetime
import re
import sys
from typing import List, Dict

def connect_to_router(device: Dict) -> netmiko.ConnectHandler:
    """Connect to a router using Netmiko."""
    try:
        return netmiko.ConnectHandler(**device)
    except Exception as e:
        print(f"Failed to connect to {device['host']}: {e}")
        return None

def get_bgp_sessions_iosxr(connection: netmiko.ConnectHandler) -> List[Dict]:
    """Retrieve BGP sessions from IOS-XR router."""
    output = connection.send_command("show bgp summary")
    sessions = []
    neighbor_pattern = re.compile(r"(\S+)\s+(\d+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+/\d+)")
    
    for line in output.splitlines():
        match = neighbor_pattern.search(line)
        if match:
            sessions.append({
                "neighbor_ip": match.group(1),
                "remote_as": match.group(2),
                "state": match.group(3),
                "prefixes_received": match.group(4)
            })
    return sessions

def get_bgp_sessions_sros(connection: netmiko.ConnectHandler) -> List[Dict]:
    """Retrieve BGP sessions from Nokia SR OS router."""
    output = connection.send_command("show router bgp summary")
    sessions = []
    neighbor_pattern = re.compile(r"(\S+)\s+(\d+)\s+(\S+)\s+\S+\s+\S+\s+(\d+/\d+)")
    
    for line in output.splitlines():
        match = neighbor_pattern.search(line)
        if match:
            sessions.append({
                "neighbor_ip": match.group(1),
                "remote_as": match.group(2),
                "state": match.group(3),
                "prefixes_received": match.group(4)
            })
    return sessions

def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize SQLite database and create bgp_sessions table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bgp_sessions (
            hostname TEXT,
            neighbor_ip TEXT,
            remote_as INTEGER,
            local_as INTEGER,
            state TEXT,
            prefixes_received TEXT,
            last_updated TIMESTAMP,
            PRIMARY KEY (hostname, neighbor_ip)
        )
    """)
    conn.commit()
    return conn

def update_db(conn: sqlite3.Connection, hostname: str, sessions: List[Dict], local_as: int):
    """Update or insert BGP session data into the database."""
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    
    for session in sessions:
        cursor.execute("""
            INSERT OR REPLACE INTO bgp_sessions 
            (hostname, neighbor_ip, remote_as, local_as, state, prefixes_received, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            hostname,
            session["neighbor_ip"],
            int(session["remote_as"]),
            local_as,
            session["state"],
            session["prefixes_received"],
            timestamp
        ))
    conn.commit()

def main():
    # Router configuration
    routers = [
        {
            "device_type": "cisco_xr",
            "host": "192.168.1.1",
            "username": "admin",
            "password": "password",
            "port": 22,
            "local_as": 65001
        },
        {
            "device_type": "nokia_sros",
            "host": "192.168.1.2",
            "username": "admin",
            "password": "password",
            "port": 22,
            "local_as": 65002
        }
    ]
    
    db_path = "bgp_sessions.db"
    conn = init_db(db_path)
    
    for router in routers:
        connection = connect_to_router(router)
        if not connection:
            continue
            
        hostname = connection.find_prompt().strip("#>")
        if router["device_type"] == "cisco_xr":
            sessions = get_bgp_sessions_iosxr(connection)
        elif router["device_type"] == "nokia_sros":
            sessions = get_bgp_sessions_sros(connection)
        else:
            print(f"Unsupported device type for {router['host']}")
            connection.disconnect()
            continue
            
        update_db(conn, hostname, sessions, router["local_as"])
        print(f"Updated BGP sessions for {hostname}")
        connection.disconnect()
    
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
