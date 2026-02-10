#!/usr/bin/env python3
"""
Features implemented:
- TCP connect scanning
- Multithreading
- Banner grabbing
- Port range parsing
- Error handling
- Timing and progress output
"""

import socket
import argparse
import concurrent.futures
import time



def scan_port(target, port, timeout=1.0):
    """
    Attempts to connect to a specific port and grab a banner.

    Returns:
        (port, state, banner, time_taken)
    """

    start_time = time.time()

    try:
        # Create TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set connection timeout
        sock.settimeout(timeout)

        # Attempt TCP connection
        result = sock.connect_ex((target, port))

        banner = ""

        if result == 0:
            # Try to grab service banner
            try:
                sock.send(b"\r\n")
                banner = sock.recv(1024).decode(errors="ignore").strip()
            except:
                banner = "No banner"

            state = "open"
        else:
            state = "closed"

        sock.close()

    except Exception:
        state = "error"
        banner = ""

    end_time = time.time()
    elapsed = round(end_time - start_time, 3)

    return (port, state, banner, elapsed)


# Scan port range using multithreading
def scan_range(target, start_port, end_port, threads=100):
    print(f"[*] Scanning {target} from port {start_port} to {end_port}")
    print(f"[*] Using {threads} threads\n")

    results = []

    # Thread pool executor for parallel scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:

        futures = []

        for port in range(start_port, end_port + 1):
            futures.append(executor.submit(scan_port, target, port))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()

            port, state, banner, elapsed = result

            if state == "open":
                print(f"[+] Port {port} OPEN ({elapsed}s)")
                if banner:
                    print(f"    Banner: {banner}")

                results.append(result)

    return results



# Parse port ranges like 1-1000
def parse_port_range(port_string):
    """
    Converts a string like '1-1000' into integers.
    """

    try:
        start, end = port_string.split("-")
        return int(start), int(end)
    except:
        print("[-] Invalid port range format. Use start-end (e.g., 1-1000)")
        exit(1)


# main funciton 
def main():

    parser = argparse.ArgumentParser(description="Archit Port Scanner")

    parser.add_argument("--target", required=True,
                        help="Target IP or hostname")

    parser.add_argument("--ports", default="1-1024",
                        help="Port range (example: 1-65535)")

    parser.add_argument("--threads", type=int, default=100,
                        help="Number of scanning threads")

    args = parser.parse_args()

    start_port, end_port = parse_port_range(args.ports)

    print(f"\n[*] Starting scan on {args.target}")
    start_time = time.time()

    results = scan_range(args.target, start_port, end_port, args.threads)

    end_time = time.time()

    print("\n[+] Scan Complete")
    print(f"[+] Open Ports Found: {len(results)}")

    for port, state, banner, elapsed in results:
        print(f"    Port {port} - {state}")
        if banner:
            print(f"        {banner}")

    print(f"\n[*] Total Scan Time: {round(end_time - start_time,2)} seconds")


if __name__ == "__main__":
    main()
