#!/usr/bin/env python3
"""
Stolen Schematics - Check TallDwarfHosting GitHub repos
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
    print("Stolen Schematics - TallDwarfHosting GitHub Investigation")
    print("="*70)
    
    try:
        import paramiko
        
        print(f"\n[*] Connecting to {HOST}:{PORT}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=30)
        print("[+] Connected!")
        
        # Check GitHub repos
        print("\n" + "="*70)
        print("CHECKING TALLDWARFHOSTING GITHUB REPOS")
        print("="*70)
        
        github_commands = [
            "wget -qO- 'https://api.github.com/users/TallDwarfHosting/repos' 2>&1",
            "wget -qO- 'https://api.github.com/orgs/TallDwarfHosting/packages' 2>&1",
        ]
        
        for cmd in github_commands:
            execute_command(ssh, cmd, wait_time=5)
        
        # Try Python to parse the response better
        print("\n" + "="*70)
        print("PARSING GITHUB API WITH PYTHON")
        print("="*70)
        
        python_script = """
python3 << 'PYSCRIPT'
import urllib.request
import json

# Get repos
print("[*] Fetching TallDwarfHosting repos...")
try:
    response = urllib.request.urlopen('https://api.github.com/users/TallDwarfHosting/repos', timeout=10)
    repos = json.loads(response.read())
    
    if repos:
        print(f"[+] Found {len(repos)} repo(s):\\n")
        for repo in repos:
            print(f"Name: {repo['name']}")
            print(f"URL: {repo['html_url']}")
            print(f"Description: {repo.get('description', 'N/A')}")
            print(f"Created: {repo['created_at']}")
            print(f"Updated: {repo['updated_at']}")
            print("-" * 60)
    else:
        print("[-] No repos found")
except Exception as e:
    print(f"[-] Error: {e}")

# Try to get packages
print("\\n[*] Checking for packages...")
try:
    # Try the GitHub packages API
    url = 'https://api.github.com/orgs/TallDwarfHosting/packages?package_type=container'
    response = urllib.request.urlopen(url, timeout=10)
    packages = json.loads(response.read())
    
    if packages:
        print(f"[+] Found {len(packages)} package(s):\\n")
        for pkg in packages:
            print(f"Name: {pkg['name']}")
            print(f"Package Type: {pkg['package_type']}")
            print(f"Visibility: {pkg['visibility']}")
            print("-" * 60)
    else:
        print("[-] No packages found")
except urllib.error.HTTPError as e:
    print(f"[-] HTTP Error {e.code}: {e.reason}")
except Exception as e:
    print(f"[-] Error: {e}")
PYSCRIPT
"""
        
        execute_command(ssh, python_script, wait_time=15)
        
        ssh.close()
        print("\n[+] GitHub investigation complete!")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
