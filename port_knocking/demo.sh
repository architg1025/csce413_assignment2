SEQUENCE=${2:-"1234,5678,9012"}

echo "[*] Blocking SSH port 2222"
sudo iptables -D INPUT -p tcp --dport 2222 -j ACCEPT 2>/dev/null
sudo iptables -A INPUT -p tcp --dport 2222 -j DROP

echo "[1/3] Attempting protected port before knocking - will timeout in 5 seconds"
timeout 5 ssh user@localhost -p 2222 || echo "[✓] the port is blocked as we expected it to be"

echo "[*] Starting knock server"
sudo python3 knock_server.py &
SERVER_PID=$!
sleep 2

echo "[2/3] Sending knock sequence: $SEQUENCE"
python3 knock_client.py --target localhost --check

echo "[3/3] Attempting protected port after knocking"
ssh user@localhost -p 2222

sudo kill $SERVER_PID
sudo iptables -D INPUT -p tcp --dport 2222 -j DROP
