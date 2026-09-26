#!/usr/bin/env python3
"""Find and inspect the public GHCR image"""
import paramiko, time

HOST = "instance.ctf.tdho.st"
PORT = 32879
USER, PASSWORD = "player", "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=20)

def ex(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    time.sleep(2)
    return stdout.read().decode('utf-8', errors='ignore')

print("[*] Searching for GHCR image info from container...")

# Try to get the image name from container
print(ex("cat /proc/self/mountinfo | grep lowerdir | head -1"))

# Check for image metadata
print("\n[*] Looking for Dockerfile or build info...")
print(ex("find / -name 'Dockerfile*' -o -name '.dockerignore' 2>/dev/null | head -10"))

# Try to pull/inspect ghcr image
print("\n[*] Attempting to access TallDwarfHosting GHCR packages...")
script = """
python3 << 'EOF'
import urllib.request, json
repos = ['mc-server', 'minecraft-server', 'game-server', 'server', 'stolen-schematics']
for r in repos:
    try:
        url = f'https://ghcr.io/v2/talldwarfhosting/{r}/tags/list'
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=5)
        print(f"[+] FOUND: {r}")
        print(json.dumps(json.loads(resp.read()), indent=2))
    except Exception as e:
        pass
EOF
"""
print(ex(script))

# Check if there's a way to access host docker
print("\n[*] Checking for docker access...")
print(ex("which docker 2>/dev/null || echo 'no docker'"))

ssh.close()
