#!/usr/bin/env python3
"""
Stolen Schematics - Accessing Host Services

Found open ports on 172.27.0.1 (gateway/host):
- Port 22: SSH
- Port 80: HTTP  
- Port 8080: HTTP

Let's investigate these services!
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
    print("Stolen Schematics - Host Service Investigation")
    print("="*70)
    
    try:
        import paramiko
        
        print(f"\n[*] Connecting to {HOST}:{PORT}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=30)
        print("[+] Connected!")
        
        # Check HTTP services
        print("\n" + "="*70)
        print("HTTP SERVICE ON 172.27.0.1:80")
        print("="*70)
        
        http_commands = [
            "curl -s http://172.27.0.1/ 2>&1 | head -100",
            "curl -s http://172.27.0.1/flag.txt 2>&1",
            "curl -s http://172.27.0.1/robots.txt 2>&1",
            "curl -sI http://172.27.0.1/ 2>&1",
        ]
        
        for cmd in http_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Check HTTP service on port 8080
        print("\n" + "="*70)
        print("HTTP SERVICE ON 172.27.0.1:8080")
        print("="*70)
        
        http_8080_commands = [
            "curl -s http://172.27.0.1:8080/ 2>&1 | head -100",
            "curl -s http://172.27.0.1:8080/flag.txt 2>&1",
            "curl -sI http://172.27.0.1:8080/ 2>&1",
        ]
        
        for cmd in http_8080_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Try SSH to the host
        print("\n" + "="*70)
        print("ATTEMPTING SSH TO HOST 172.27.0.1:22")
        print("="*70)
        
        ssh_commands = [
            "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 player@172.27.0.1 'whoami' 2>&1",
            "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@172.27.0.1 'whoami' 2>&1",
        ]
        
        for cmd in ssh_commands:
            execute_command(ssh, cmd, wait_time=8)
        
        # Check for more network services/containers
        print("\n" + "="*70)
        print("SCANNING FOR MORE SERVICES")
        print("="*70)
        
        scan_commands = [
            "for i in {1..254}; do timeout 0.5 bash -c \"echo > /dev/tcp/172.27.0.$i/25565\" 2>&1 && echo \"172.27.0.$i:25565 MINECRAFT\" || true; done | grep MINECRAFT",
            "for i in {1..254}; do timeout 0.5 bash -c \"echo > /dev/tcp/172.27.0.$i/22\" 2>&1 && echo \"172.27.0.$i:22 SSH\" || true; done | grep SSH",
        ]
        
        for cmd in scan_commands:
            execute_command(ssh, cmd, wait_time=20)
        
        # Try to access container registry info
        print("\n" + "="*70)
        print("SEARCHING FOR REGISTRY/IMAGE INFO")
        print("="*70)
        
        registry_commands = [
            "curl -s http://172.27.0.1/api/version 2>&1",
            "curl -s http://172.27.0.1:8080/api/version 2>&1",
            "curl -s http://172.27.0.1/v2/ 2>&1",
            "curl -s http://172.27.0.1:8080/v2/ 2>&1",
        ]
        
        for cmd in registry_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Check DNS for internal services
        print("\n" + "="*70)
        print("DNS LOOKUPS FOR INTERNAL SERVICES")
        print("="*70)
        
        dns_commands = [
            "nslookup ghcr.io 2>&1 || echo 'No nslookup'",
            "host ghcr.io 2>&1 || echo 'No host'",
            "dig ghcr.io 2>&1 || echo 'No dig'",
            "getent hosts ghcr.io 2>&1 || echo 'No ghcr.io resolution'",
        ]
        
        for cmd in dns_commands:
            execute_command(ssh, cmd)
        
        ssh.close()
        print("\n[+] Host investigation complete!")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
