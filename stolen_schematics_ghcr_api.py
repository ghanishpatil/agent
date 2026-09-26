#!/usr/bin/env python3
"""
Stolen Schematics - GHCR API Exploration

Using the GitHub Container Registry API to find public containers
"""

import paramiko
import time
import sys

HOST = "instance.ctf.tdho.st"
PORT = 32867
USER = "player"
PASSWORD = "reyalp"

def execute_command(ssh, command, wait_time=2):
    """Execute a command and return output"""
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=20)
        time.sleep(wait_time)
        
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(f"\n[CMD] {command}")
        if output:
            print(output)
        if error and "Permission denied" not in error and "No such file" not in error and error.strip():
            print(f"[ERR] {error}")
        
        return output, error
    except Exception as e:
        print(f"[-] Error executing '{command}': {e}")
        return "", str(e)

def main():
    print("="*70)
    print("Stolen Schematics - GHCR API & Container Registry Exploration")
    print("="*70)
    
    try:
        import paramiko
        
        print(f"\n[*] Connecting to {HOST}:{PORT}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=30)
        print("[+] Connected!")
        
        # Try to access GHCR API
        print("\n" + "="*70)
        print("GHCR API - Trying to find talldwarfhosting packages")
        print("="*70)
        
        ghcr_commands = [
            "wget -qO- 'https://ghcr.io/v2/' 2>&1",
            "wget -qO- 'https://ghcr.io/v2/talldwarfhosting/minecraft-server/tags/list' 2>&1",
            "wget -qO- 'https://ghcr.io/v2/talldwarfhosting/mc-server/tags/list' 2>&1",
            "wget -qO- 'https://ghcr.io/v2/talldwarfhosting/game-server/tags/list' 2>&1",
            "wget -qO- 'https://api.github.com/users/talldwarfhosting' 2>&1",
        ]
        
        for cmd in ghcr_commands:
            execute_command(ssh, cmd, wait_time=5)
        
        # Try Python approach
        print("\n" + "="*70)
        print("USING PYTHON TO QUERY GHCR")
        print("="*70)
        
        python_ghcr = """
python3 << 'PYSCRIPT'
import urllib.request
import json

# Try to access GHCR anonymously
repos = [
    'talldwarfhosting/minecraft-server',
    'talldwarfhosting/mc-server',
    'talldwarfhosting/game-server',
    'talldwarfhosting/server',
]

for repo in repos:
    url = f'https://ghcr.io/v2/{repo}/tags/list'
    print(f"\\n[*] Trying: {url}")
    try:
        response = urllib.request.urlopen(url, timeout=5)
        data = json.loads(response.read())
        print(f"[+] FOUND: {repo}")
        print(json.dumps(data, indent=2))
    except urllib.error.HTTPError as e:
        print(f"[-] {e.code}: {e.reason}")
    except Exception as e:
        print(f"[-] Error: {e}")
PYSCRIPT
"""
        
        execute_command(ssh, python_ghcr, wait_time=10)
        
        # Check if there's a backup or older image mentioned anywhere
        print("\n" + "="*70)
        print("SEARCHING FOR IMAGE/REGISTRY HINTS IN FILES")
        print("="*70)
        
        search_commands = [
            "grep -r 'ghcr' /opt 2>/dev/null | head -20",
            "grep -r 'registry' /opt 2>/dev/null | head -20",
            "grep -r 'image' /opt/mc/config 2>/dev/null",
            "grep -r 'docker' /opt 2>/dev/null | head -20",
        ]
        
        for cmd in search_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Check for any backup or old files
        print("\n" + "="*70)
        print("SEARCHING FOR BACKUP OR OLD FILES")
        print("="*70)
        
        backup_commands = [
            "find /opt -name '*.bak' 2>/dev/null",
            "find /opt -name '*.old' 2>/dev/null",
            "find /opt -name '*backup*' 2>/dev/null",
            "find /opt -name 'Dockerfile*' 2>/dev/null",
            "find / -name 'Dockerfile*' 2>/dev/null | head -20",
        ]
        
        for cmd in backup_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        ssh.close()
        print("\n[+] GHCR exploration complete!")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
