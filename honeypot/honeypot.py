import socket   
import threading  
import logging  
import time  

LOG_PATH = "/app/logs/honeypot.log"

# Fake banner to convicne attackers its the real deal 
SSH_BANNER = "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n"
FAKE_HOSTNAME = "ip-172-20-0-30"
MAX_ATTEMPTS = 3


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  
        format="%(asctime)s | %(message)s",  
        handlers=[
            # Write logs to the honeypot log file
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(),
        ],
    )


def cowrie_log(msg):
#taken from cowrie github
    logging.info(msg)


def handle_client(conn, addr):

    # addr is a (IP, port) tuple provided by socket.accept()
    src_ip, src_port = addr
    # Record when this session started so we can compute its duration
    start_time = time.time()

    # Log that a new session has started from this source IP/port
    cowrie_log(f"cowrie.session.connect src_ip={src_ip} src_port={src_port}")

    try:
        # Send a fake SSH banner so scanners think this is a real SSH service
        conn.sendall(SSH_BANNER.encode())

        attempts = 0
        while attempts < MAX_ATTEMPTS:
            # Ask for a username
            conn.sendall(b"login: ")
            username = conn.recv(1024).decode(errors="ignore").strip()

            # Ask for a password
            conn.sendall(b"Password: ")
            password = conn.recv(1024).decode(errors="ignore").strip()

            attempts += 1

            # Password is masked with '*' characters but length is preserved.
            cowrie_log(
                f"cowrie.login.failed "
                f"src_ip={src_ip} username={username} "
                f"password={'*' * len(password)} "
                f"attempts={attempts}"
            )

            conn.sendall(b"Permission denied, please try again.\r\n")

        # After MAX_ATTEMPTS, present a fake shell prompt to keep attacker engaged
        conn.sendall(
            f"\r\nWelcome to Ubuntu 20.04 LTS (GNU/Linux 5.15.0-91-generic x86_64)\r\n\r\n"
            f"{FAKE_HOSTNAME}:~$ ".encode()
        )

        while True:
            # Read the command the attacker types
            cmd = conn.recv(1024).decode(errors="ignore").strip()
            #if no command is passed we break
            if not cmd:
                break

            # Log the command they attempted to run
            cowrie_log(
                f"cowrie.command.input src_ip={src_ip} command=\"{cmd}\""
            )

            if cmd in ("exit", "logout"):
                break

            conn.sendall(b"command not found\r\n")
            # Re-print the fake shell prompt
            conn.sendall(f"{FAKE_HOSTNAME}:~$ ".encode())

    except Exception as e:
        cowrie_log(f"cowrie.session.error src_ip={src_ip} error={e}")

    finally:
        duration = round(time.time() - start_time, 2)
        cowrie_log(
            f"cowrie.session.closed src_ip={src_ip} duration={duration}s"
        )
        conn.close()


def run_honeypot():
    # Create a TCP/IPv4 socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to all interfaces on port 22 (standard SSH port)
    server.bind(("0.0.0.0", 22))
    server.listen(5)

    # Log that the honeypot is now listening for SSH connections
    cowrie_log("cowrie.ssh.listen port=22")

    # Main accept loop: handle connections one by one
    while True:
        # Block until a client connects, returning a new socket and its address
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True, 
        ).start()


if __name__ == "__main__":
    setup_logging()
    run_honeypot()