#!/usr/bin/env python3
"""Hunt for the public ghcr.io registry with old vulnerable image"""
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
    stdin, stdout, stderr = ssh.exec_command(c, timeout=15)
    return (stdout.read() + stderr.read()).decode()

print("[*] Hunting for public ghcr.io registry...")

# Check local Docker registry
print("\n[1] Local registry at 172.27.0.1:5000:")
registry_check = '''python3 << 'PY'
import urllib.request
import json

reg = "http://172.27.0.1:5000"

# List repositories
try:
    with urllib.request.urlopen(f"{reg}/v2/_catalog", timeout=3) as r:
        repos = json.loads(r.read().decode())
        print("Repositories:", repos)
        
        # For each repo, list tags
        for repo in repos.get('repositories', []):
            try:
                with urllib.request.urlopen(f"{reg}/v2/{repo}/tags/list", timeout=3) as tr:
                    tags = json.loads(tr.read().decode())
                    print(f"  {repo}: {tags}")
                    
                    # Try to pull manifest for each tag
                    for tag in tags.get('tags', []):
                        try:
                            req = urllib.request.Request(
                                f"{reg}/v2/{repo}/manifests/{tag}",
                                headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
                            )
                            with urllib.request.urlopen(req, timeout=3) as mr:
                                manifest = json.loads(mr.read().decode())
                                print(f"    Tag {tag} config: {manifest.get('config', {}).get('digest', 'N/A')}")
                        except:
                            pass
            except Exception as e:
                print(f"  Error listing tags for {repo}: {e}")
except Exception as e:
    print(f"Registry error: {e}")
PY
'''
print(cmd(registry_check))

# Check environment variables for hints
print("\n[2] Environment variables:")
print(cmd("env | grep -iE '(registry|ghcr|github|docker|image)'"))

# Check Dockerfile or build info
print("\n[3] Looking for build artifacts:")
print(cmd("find / -name 'Dockerfile*' -o -name '.dockerignore' -o -name 'docker-compose*' 2>/dev/null"))

# Check for .git directory that might have GitHub org name
print("\n[4] Looking for Git info:")
print(cmd("find / -name '.git' -type d 2>/dev/null"))
print(cmd("cat /.git/config 2>/dev/null"))

# Look for organization hints in any config files
print("\n[5] Searching for GitHub/registry hints:")
print(cmd("grep -r 'ghcr.io' / 2>/dev/null | head -10"))
print(cmd("grep -r 'github.com' / 2>/dev/null | head -10"))

# Check if we can access Docker socket (unlikely but worth trying)
print("\n[6] Docker socket check:")
docker_test = cmd("docker ps 2>&1")
if "Cannot connect" not in docker_test:
    print(docker_test)
    print(cmd("docker images 2>&1"))

# Try common CTF org names on ghcr.io
print("\n[7] Trying common ghcr.io org names...")
orgs = [
    "talld-holders",
    "tall-dwarf-holders",
    "tdho-ctf",
    "tdho",
    "tdhos",
    "tallholders",
    "ctf-tdho",
    "ctf7-tdho",
    "stolen-schematics",
    "talldwarfholders",
]

for org in orgs:
    test = f'''python3 -c "import urllib.request; urllib.request.urlopen('https://ghcr.io/v2/{org}/stolen-schematics-gameserver/tags/list', timeout=2); print('{org}: FOUND')" 2>/dev/null'''
    result = cmd(test)
    if result.strip():
        print(result)

ssh.close()
