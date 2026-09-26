#!/usr/bin/env python3
"""
Stolen Schematics - Using wget to explore HTTP services
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
    print("Stolen Schematics - HTTP Service Exploration with wget")
    print("="*70)
    
    try:
        import paramiko
        
        print(f"\n[*] Connecting to {HOST}:{PORT}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=30)
        print("[+] Connected!")
        
        # Check if wget is available
        print("\n" + "="*70)
        print("CHECKING AVAILABLE TOOLS")
        print("="*70)
        
        tool_commands = [
            "which wget",
            "which nc",
            "which telnet",
            "python3 --version 2>&1 || echo 'No python3'",
        ]
        
        for cmd in tool_commands:
            execute_command(ssh, cmd)
        
        # Use wget to explore HTTP services
        print("\n" + "="*70)
        print("EXPLORING HTTP ON 172.27.0.1:80")
        print("="*70)
        
        http_commands = [
            "wget -q -O - http://172.27.0.1/ 2>&1 | head -100",
            "wget -q -O - http://172.27.0.1/flag.txt 2>&1",
            "wget -q -O - http://172.27.0.1/robots.txt 2>&1",
            "wget -S -O /dev/null http://172.27.0.1/ 2>&1 | head -20",
        ]
        
        for cmd in http_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Check port 8080
        print("\n" + "="*70)
        print("EXPLORING HTTP ON 172.27.0.1:8080")
        print("="*70)
        
        http_8080_commands = [
            "wget -q -O - http://172.27.0.1:8080/ 2>&1 | head -100",
            "wget -q -O - http://172.27.0.1:8080/flag.txt 2>&1",
            "wget -S -O /dev/null http://172.27.0.1:8080/ 2>&1 | head -20",
        ]
        
        for cmd in http_8080_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Try to use python to make HTTP requests if available
        print("\n" + "="*70)
        print("USING PYTHON FOR HTTP REQUESTS")
        print("="*70)
        
        python_commands = [
            "python3 -c \"import urllib.request; print(urllib.request.urlopen('http://172.27.0.1/').read().decode())\" 2>&1 | head -100",
            "python3 -c \"import urllib.request; print(urllib.request.urlopen('http://172.27.0.1:8080/').read().decode())\" 2>&1 | head -100",
        ]
        
        for cmd in python_commands:
            execute_command(ssh, cmd, wait_time=5)
        
        # Check for /etc/flag.txt on the HTTP servers
        print("\n" + "="*70)
        print("CHECKING FOR FLAG FILES VIA HTTP")
        print("="*70)
        
        flag_commands = [
            "wget -q -O - http://172.27.0.1/etc/flag.txt 2>&1",
            "wget -q -O - http://172.27.0.1:8080/etc/flag.txt 2>&1",
            "wget -q -O - http://172.27.0.1/../../etc/flag.txt 2>&1",
        ]
        
        for cmd in flag_commands:
            execute_command(ssh, cmd)
        
        ssh.close()
        print("\n[+] Exploration complete!")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
