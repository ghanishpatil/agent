#!/usr/bin/env python3
import urllib.request, json, gzip, tarfile, io, os

ORG, REPO, TAG = "talldwarfhosting", "stolen-schematics-game-server-prerelease", "v2.5.39"
OUT = r"d:\mission-git-hackss\ghcr_extract"
os.makedirs(OUT, exist_ok=True)

def token():
    url = f"https://ghcr.io/token?service=ghcr.io&scope=repository:{ORG}/{REPO}:pull"
    return json.loads(urllib.request.urlopen(url, timeout=10).read())["token"]

def get(url, tok, accept=None):
    headers = {"Authorization": f"Bearer {tok}"}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

tok = token()
idx = json.loads(
    get(
        f"https://ghcr.io/v2/{ORG}/{REPO}/manifests/{TAG}",
        tok,
        "application/vnd.oci.image.index.v1+json",
    )
)
print("index manifests:", len(idx["manifests"]))

# pick linux/amd64
sub_digest = None
for m in idx["manifests"]:
    plat = m.get("platform", {})
    if plat.get("os") == "linux" and plat.get("architecture") == "amd64":
        sub_digest = m["digest"]
        break
if not sub_digest:
    sub_digest = idx["manifests"][0]["digest"]

man = json.loads(
    get(
        f"https://ghcr.io/v2/{ORG}/{REPO}/manifests/{sub_digest}",
        tok,
        "application/vnd.oci.image.manifest.v1+json",
    )
)
print("layers:", len(man.get("layers", [])))

for i, layer in enumerate(man.get("layers", [])):
    digest = layer["digest"]
    print(f"layer {i}: {digest[:24]}...")
    data = get(f"https://ghcr.io/v2/{ORG}/{REPO}/blobs/{digest}", tok)
    raw = gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data
    try:
        tf = tarfile.open(fileobj=io.BytesIO(raw), mode="r:*")
    except Exception as e:
        print("  tar error:", e)
        continue
    for mem in tf.getmembers():
        if not mem.isfile():
            continue
        name = mem.name.lstrip("./")
        body = tf.extractfile(mem).read()
        interesting = any(
            x in name
            for x in ["sync", "entry", "ssh", "flag", "watch", "scripts", "CHANGELOG", "root"]
        )
        if interesting or b"tdho{" in body or b"BEGIN" in body:
            path = os.path.join(OUT, name.replace("/", os.sep))
            os.makedirs(os.path.dirname(path) or OUT, exist_ok=True)
            with open(path, "wb") as f:
                f.write(body)
            print(f"  FILE {name} ({len(body)}b)")
            if len(body) < 20000 and b"\x00" not in body[:100]:
                print(body.decode(errors="replace"))
                print("---")

cfg_digest = man["config"]["digest"]
cfg = json.loads(get(f"https://ghcr.io/v2/{ORG}/{REPO}/blobs/{cfg_digest}", tok))
print("ENV:", cfg.get("config", {}).get("Env"))
for h in cfg.get("history", []):
    cb = h.get("created_by", "")
    if cb and not cb.startswith("("):
        print("HIST:", cb[:300])

print("Done ->", OUT)
