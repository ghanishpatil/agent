#!/usr/bin/env python3
"""
Stolen Schematics - Windows-compatible SSH reconnaisance
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
        stdin, stdout, stderr = ssh.exec_command(command, timeout=10)
        time.sleep(wait_time)
        
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(f"\n[CMD] {command}")
        if output:
            print(output)
        if error:
            print(f"[ERR] {error}")
        
        return output, error
    except Exception as e:
        print(f"[-] Error executing '{command}': {e}")
        return "", str(e)

def main():
    print("="*70)
    print("Stolen Schematics - Container Escape Challenge Reconnaissance")
    print("="*70)
    
    try:
        # Install paramiko if needed
        try:
            import paramiko
        except ImportError:
            print("[*] Installing paramiko...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "paramiko"], check=True)
            import paramiko
        
        # Connect via SSH
        print(f"\n[*] Connecting to {HOST}:{PORT} as {USER}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=30)
        print("[+] Connected successfully!")
        
        # Basic reconnaissance
        recon_commands = [
            "whoami",
            "id",
            "pwd",
            "hostname",
            "ls -la",
            "ls -la /",
            "cat /etc/os-release",
            "uname -a",
        ]
        
        print("\n" + "="*70)
        print("BASIC RECONNAISSANCE")
        print("="*70)
        for cmd in recon_commands:
            execute_command(ssh, cmd)
        
        # Container detection
        container_commands = [
            "cat /.dockerenv 2>/dev/null || echo 'No .dockerenv'",
            "cat /proc/1/cgroup | head -5",
            "mount | grep docker || echo 'No docker mounts'",
            "ls -la /var/run/docker.sock 2>/dev/null || echo 'No docker socket'",
            "cat /proc/self/status | grep Cap",
        ]
        
        print("\n" + "="*70)
        print("CONTAINER DETECTION")
        print("="*70)
        for cmd in container_commands:
            execute_command(ssh, cmd)
        
        # Process and network info
        info_commands = [
            "ps aux | grep -v grep",
            "netstat -tuln 2>/dev/null || ss -tuln 2>/dev/null || echo 'No netstat/ss'",
            "ip addr show 2>/dev/null || ifconfig 2>/dev/null || echo 'No network info'",
            "cat /proc/net/tcp | head -20",
        ]
        
        print("\n" + "="*70)
        print("PROCESS & NETWORK INFO")
        print("="*70)
        for cmd in info_commands:
            execute_command(ssh, cmd)
        
        # Look for Java/game server
        game_commands = [
            "ps aux | grep java",
            "find / -name '*.jar' 2>/dev/null | head -20",
            "ls -la /opt 2>/dev/null || echo 'No /opt'",
            "ls -la /srv 2>/dev/null || echo 'No /srv'",
            "ls -la /app 2>/dev/null || echo 'No /app'",
            "ls -la /home 2>/dev/null || echo 'No /home'",
        ]
        
        print("\n" + "="*70)
        print("GAME SERVER SEARCH")
        print("="*70)
        for cmd in game_commands:
            execute_command(ssh, cmd)
        
        # Check environment for registry hints
        env_commands = [
            "env | sort",
            "cat /proc/1/environ | tr '\\0' '\\n' | grep -i -E '(ghcr|registry|image)' || echo 'No registry vars'",
            "cat /proc/self/environ | tr '\\0' '\\n' | sort",
        ]
        
        print("\n" + "="*70)
        print("ENVIRONMENT VARIABLES (Registry Hints)")
        print("="*70)
        for cmd in env_commands:
            execute_command(ssh, cmd)
        
        # Search for flags
        flag_commands = [
            "find / -name '*flag*' 2>/dev/null | head -30",
            "grep -r 'flag{' /home 2>/dev/null | head -10 || echo 'No flags in /home'",
            "grep -r 'flag{' /root 2>/dev/null | head -10 || echo 'No access to /root'",
            "grep -r 'CTF{' / 2>/dev/null | head -10 || echo 'Searching...'",
        ]
        
        print("\n" + "="*70)
        print("FLAG SEARCH")
        print("="*70)
        for cmd in flag_commands:
            execute_command(ssh, cmd, wait_time=3)
        
        # Privilege escalation checks
        priv_commands = [
            "sudo -l 2>/dev/null || echo 'No sudo access'",
            "find / -perm -4000 2>/dev/null | head -20",  # SUID binaries
            "getcap -r / 2>/dev/null | head -20 || echo 'No getcap'",
            "cat /etc/sudoers 2>/dev/null || echo 'No access to sudoers'",
        ]
        
        print("\n" + "="*70)
        print("PRIVILEGE ESCALATION VECTORS")
        print("="*70)
        for cmd in priv_commands:
            execute_command(ssh, cmd)
        
        # Docker-specific escape vectors
        docker_escape = [
            "ls -la /var/run/",
            "ls -la /proc/self/ns/",
            "cat /proc/self/mountinfo | grep docker",
            "find / -name 'docker' -o -name 'containerd' 2>/dev/null",
        ]
        
        print("\n" + "="*70)
        print("CONTAINER ESCAPE VECTORS")
        print("="*70)
        for cmd in docker_escape:
            execute_command(ssh, cmd)
        
        # Network connections to find other containers
        network_commands = [
            "cat /etc/hosts",
            "cat /etc/resolv.conf",
            "arp -a 2>/dev/null || echo 'No arp'",
            "ip route show 2>/dev/null || route -n 2>/dev/null || echo 'No route info'",
        ]
        
        print("\n" + "="*70)
        print("NETWORK TOPOLOGY")
        print("="*70)
        for cmd in network_commands:
            execute_command(ssh, cmd)
        
        print("\n" + "="*70)
        print("RECONNAISSANCE COMPLETE")
        print("="*70)
        print("\n[*] Connection will remain open for 60 seconds for manual commands...")
        print("[*] Type commands manually if needed\n")
        
        # Keep connection alive briefly
        time.sleep(5)
        
        ssh.close()
        print("\n[+] Disconnected")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
