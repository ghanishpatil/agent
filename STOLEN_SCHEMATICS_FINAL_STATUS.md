# STOLEN SCHEMATICS - FINAL STATUS & SOLUTION PATH

## Challenge Overview
- **Goal**: Escape container → compromise another game server → retrieve flag from `/root/flag.txt`
- **Instance**: `ssh player@instance.ctf.tdho.st -p 32964` (password: `reyalp`)
- **Time**: ~9 minutes per instance
- **Points**: 350

## What We Know FOR CERTAIN

### Container Environment (172.27.0.3 - Current)
- **OS**: Ubuntu 22.04.5 LTS (minimized - no curl, no sshpass)
- **Inside Docker**: `/.dockerenv` exists
- **Not privileged**: CapEff = 0 (no special capabilities)
- **Running processes**:
  - PID 1: `/bin/bash /entrypoint.sh` (starts SSH + sync-loop.sh)
  - PID 15: SSH server
  - PID 16: `/bin/bash /opt/mc/scripts/sync-loop.sh` (root-owned, CANNOT READ)
  - PID 17: `tail -f /dev/null` (keeps container alive)

### Network Topology
- **172.27.0.1**: Docker host
  - Port 22: SSH (OpenSSH_9.2p1 Debian) ✅ CONFIRMED OPEN
  - Port 80: HTTP ✅ OPEN
  - Port 8080: HTTP ✅ OPEN
  - Port 5000: Docker Registry ✅ ACCESSIBLE
- **172.27.0.2**: Gateway (likely)
- **172.27.0.3**: Current container (game server)

### Docker Registry Contents
```
http://172.27.0.1:5000/v2/_catalog returns:
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

**CRITICAL**: All manifest/layer requests return 404 - registry might be empty/misconfigured OR layers stored elsewhere.

### Files We Can Access
- `/opt/mc/server.properties` - Contains `management-server-secret=dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ`
- `/opt/mc/config/sync-request.conf` - Player-writable
- `/entrypoint.sh` - Readable, starts sync-loop.sh in background
- **CANNOT ACCESS**:
  - `/opt/mc/scripts/sync-loop.sh` - Permission denied (root only, 741 bytes)
  - `/opt/mc/.sync/` - Permission denied
  - `/proc/16/` (sync-loop.sh process) - Permission denied
  - No bash history on this instance

### Flag Location
- **NOT** in current container (searched `/`, no `TDHO{` found)
- **Likely** at `/root/flag.txt` on Docker host (172.27.0.1) or another container
- Challenge says "compromise ANOTHER game server" - implies pivot required

## What We've Tried

### Sync-Loop.sh Config Exploitation ❌
Tried 20+ config format variations:
- `talldwarf-sync-command=cat /root/flag.txt`
- `talldwarf-sync-command=FILE-READ:/root/flag.txt`
- With/without `talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true`
- JSON formats, base64 encoding, command injection
- **Result**: sync.trigger file created (mechanism detects config) but NO output files anywhere

### Docker Registry Extraction ❌
- Attempted to extract sync-loop.sh from all repository tags
- All manifest requests successful, but blob/layer downloads return 404
- **Conclusion**: Layers not stored in local registry OR registry API misconfigured

### SSH Pivot Attempts ❌
- No SSH keys found in `/home/player/`, `/tmp/`, or anywhere accessible
- Cannot use sshpass (not installed in minimized container)
- Password `reyalp` doesn't work for `player@172.27.0.1` or `root@172.27.0.1` (can't test - no sshpass)

### HTTP Management API ❌
- Tested http://172.27.0.1:8080/ with secret in headers, query params, body
- Tested endpoints: `/flag`, `/api/flag`, `/exec`, `/admin`, `/management`
- **All silently fail** (no response, no errors)

## UNSOLVED APPROACHES

### 1. External ghcr.io Registry (HIGHEST PROBABILITY)
Challenge description: "An older build of this server image was **accidentally left public on our ghcr.io registry**"

This means the real sync-loop.sh is on **ghcr.io** (GitHub Container Registry), NOT the local registry!

**Possible ghcr.io locations**:
```
ghcr.io/thedarkhandorg/stolen-schematics-watcher
ghcr.io/tdho/stolen-schematics-watcher
ghcr.io/darkhand/stolen-schematics-watcher  
ghcr.io/ctf7/stolen-schematics-watcher
ghcr.io/thedarkhand/stolen-schematics
ghcr.io/hackfest/stolen-schematics-watcher
```

**How to check from Kali**:
```bash
# Test if image is public
curl -s "https://ghcr.io/v2/<org>/<repo>/tags/list"

# If successful, download and extract
docker pull ghcr.io/<org>/<repo>:<tag>
docker save ghcr.io/<org>/<repo>:<tag> -o image.tar
tar -xf image.tar
grep -r "sync-loop" .
```

### 2. Actual Container Escape Vulnerability
The sync-loop.sh approach might be a **RED HERRING**. Real exploit could be:

**A. Docker Socket Mount**:
```bash
# From inside container
ls -la /var/run/docker.sock  # Already checked - doesn't exist
find / -name "docker.sock" 2>/dev/null
```

**B. Privileged Container + Kernel Exploit**:
```bash
# Check if container is actually privileged (despite CapEff=0)
fdisk -l  # Can we see host disks?
ls /dev/  # Check for unexpected devices
```

**C. cgroup/procfs Mount Escape**:
```bash
# Check for writable cgroups
find /sys/fs/cgroup -writable 2>/dev/null
# Check procfs
cat /proc/1/cgroup
```

### 3. SSH Brute Force to Docker Host
```bash
# From Kali, brute force SSH to Docker host
# User might be: player, root, admin, tdho, minecraft, mc
hydra -l player -P /usr/share/wordlists/rockyou.txt ssh://instance.ctf.tdho.st:32964 -t 4 -V
```

But use the INTERNAL IP once connected:
```python
# From inside container via Python
import paramiko
for password in ["reyalp", "player", "admin", "password", "minecraft"]:
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect("172.27.0.1", username="player", password=password, timeout=2)
        stdin, stdout, stderr = client.exec_command("cat /root/flag.txt")
        print(stdout.read())
        break
    except:
        pass
```

### 4. Minecraft Server Exploitation
- Port scan other containers: `172.27.0.{1..10}:25565` (Minecraft default)
- Exploit Minecraft RCON if enabled in `server.properties`
- Check for Minecraft-specific CVEs (Log4Shell, etc.)

## RECOMMENDED NEXT STEPS

1. **Search ghcr.io for public image** (HIGHEST PRIORITY):
   - Use GitHub search, Google dorks, or enumerate common org names
   - Once found, extract sync-loop.sh to understand correct config format
   - OR find flag directly in image layers

2. **Test Python SSH library** for pivot:
   ```bash
   sshpass -p "reyalp" ssh player@instance.ctf.tdho.st -p 32964 'python3 -c "import paramiko; print(paramiko.__version__)"'
   ```

3. **Docker breakout research**:
   - Felix Wilhelm's container escape techniques
   - Check for recent Docker CVEs (2024-2026)
   - TOCTOU race conditions in sync mechanisms

4. **Fresh instance investigation**:
   - Current instance may have been altered by previous attempts
   - New instance might have different bash history or hints

## FILES FOR SHARING WITH ANOTHER AI

Copy these to another AI (Claude, GPT-4, etc.):
1. This file (`STOLEN_SCHEMATICS_FINAL_STATUS.md`)
2. `STOLEN_SCHEMATICS_COMPLETE_CONTEXT.md` (if it exists)
3. Tell them: *"This is a Docker container escape CTF challenge. The sync-loop.sh config approach isn't working after 20+ attempts. The challenge mentions an 'accidentally public ghcr.io registry' - that's likely where sync-loop.sh source is. Need to either find that image OR discover the real container escape vector."*

## Current Instance Info
- **Host**: instance.ctf.tdho.st
- **Port**: 32964
- **Password**: reyalp
- **Time**: Check instance timer (was 9:51 at start)

---
**Last Updated**: Session context compact - all attempts documented above
