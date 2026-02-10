#!/usr/bin/env python3
"""
Port Knocking Client
Sends a sequence of TCP connection attempts ("knocks") to unlock a protected port.
"""

import argparse
import socket
import time

DEFAULT_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_DELAY = 0.3


def send_knock(target, port, delay):
    try:
        # Open a TCP connection to target:port
        with socket.create_connection((target, port), timeout=1):
            pass
    except Exception:
        pass
    #delay in between to give for precessing time 
    time.sleep(delay)


def perform_knock_sequence(target, sequence, delay):
    # Log what we're doing for the user
    print(f"[*] Knocking sequence {sequence} on {target}")
    for port in sequence:
        send_knock(target, port, delay)


def check_protected_port(target, port):
    try:
        # connecting after the knock sequence 
        with socket.create_connection((target, port), timeout=2):
            print(f"[+] Connected to protected port {port}")
    except Exception:
        # FAILL
        print(f"[-] Could not connect to protected port {port}")


def main():
    # Specify target, sequence, delay
    parser = argparse.ArgumentParser(description="Port knocking client")
    parser.add_argument("--target", required=True, help="Target IP or hostname")
    parser.add_argument(
        "--sequence",
        # Default: "1234,5678,9012"
        default=",".join(map(str, DEFAULT_SEQUENCE)),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected port to test after knocking",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="Delay between knocks (seconds)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check protected port after knocking",
    )
    args = parser.parse_args()

    # Parse comma-separated ports into a list of integers
    sequence = [int(p) for p in args.sequence.split(",")]
    perform_knock_sequence(args.target, sequence, args.delay)

    # If --check was passed, try connecting to the protected port to verify it opened
    if args.check:
        check_protected_port(args.target, args.protected_port)


if __name__ == "__main__":
    main()
