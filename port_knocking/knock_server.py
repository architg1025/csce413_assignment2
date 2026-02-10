#!/usr/bin/env python3
"""
Port Knocking Server
Listens for a predefined knock sequence and opens a protected port using iptables.
"""

import argparse
import logging
import socket
import subprocess
import time


DEFAULT_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_WINDOW = 10.0


def setup_logging():
    # timestamp and level
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def open_protected_port(port):
    logging.info("Opening firewall for port %s", port)
    #iptables ACCEPT rule for TCP traffic to this port using sudo 
    subprocess.run(
        ["iptables", "-I", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "ACCEPT"],
        check=False,
    )


def listen_for_knocks(sequence, window, protected_port):
    logging.info("Listening for knock sequence: %s", sequence)
    logging.info("Protected port: %s", protected_port)

    sockets = []
    for port in sequence:
        # IPv4
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # avoiding the already in use error 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.listen(5)
        sockets.append(s)

    # Current position in the sequence: 0 = waiting for first knock, 1 = second 
    knock_index = 0
    # When we received the first knock of the current attempt 
    start_time = None

    while True:
        # we keep the the true condioton in order to block until someone connects to the socket for the expected knock sequence 
        conn, addr = sockets[knock_index].accept()
        conn.close()

        now = time.time()

        # First knock of a new sequence:
        if knock_index == 0:
            start_time = now

        # If too much time passed since first knock, treat as wrong sequence and reset (directions said to havewa time impemented)
        if now - start_time > window:
            logging.warning("Knock timeout from %s — resetting", addr[0])
            knock_index = 0
            continue

        # if the knock happens in the correct timefram we can advance to the next expected port
        knock_index += 1

       
        if knock_index == len(sequence):
            logging.info("Correct knock sequence from %s", addr[0])
            # Add iptables rule so the client can now reach the protected port (we are configuring firewall rule) 
            open_protected_port(protected_port)

            # reset after
            knock_index = 0


def main():
    parser = argparse.ArgumentParser(description="Port knocking server")
    parser.add_argument(
        "--sequence",
        default=",".join(map(str, DEFAULT_SEQUENCE)),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected port to open",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_WINDOW,
        help="Time window to complete knock sequence",
    )
    args = parser.parse_args()

    setup_logging()
    # Parse comma-separated ports into a list of integers
    sequence = [int(p) for p in args.sequence.split(",")]

    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":
    main()
