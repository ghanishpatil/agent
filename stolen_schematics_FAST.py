#!/usr/bin/env python3
"""FAST Stolen Schematics Solver - 8 min deadline"""
import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32879
USER = "player"
PASSWORD = "reyalp"

def exec_cmd(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    time.sleep(1)
    return stdout.read().decode('utf-8', errors='ignore')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=20)
print("[+] Connected!")

# Quick checks for flag
print("\n[*] Checking flag locations...")
for loc in ['/etc/flag.txt', '/flag.txt', 'flag.txt', '/root/flag.txt']:
    result = exec_cmd(ssh, f"cat {loc} 2>/dev/null || echo 'no'")
    if 'TDHT{' in result:
        print(f"[FLAG FOUND] {result}")
        exit(0)

# Check sync config
print("\n[*] Checking sync-request.conf...")
print(exec_cmd(ssh, "cat /opt/mc/config/sync-request.conf 2>/dev/null"))

# Check network for other containers
print("\n[*] Scanning network 172.27.0.x...")
result = exec_cmd(ssh, "for i in 1 2 4 5; do timeout 1 bash -c 'echo >/dev/tcp/172.27.0.$i/22' 2>&1 && echo \"172.27.0.$i:22 UP\"; done")
print(result)

# Check HTTP services on gateway
print("\n[*] Checking HTTP on 172.27.0.1...")
result = exec_cmd(ssh, "wget -qO- http://172.27.0.1/ 2>&1 | head -20")
print(result)
result = exec_cmd(ssh, "wget -qO- http://172.27.0.1:8080/ 2>&1 | head -20")
print(result)

# Check for accessible files
print("\n[*] Searching for flags in accessible locations...")
result = exec_cmd(ssh, "find /opt /home /tmp -name '*flag*' 2>/dev/null | head -20")
print(result)

# Check if .sync volume has anything
print("\n[*] Checking .sync volume...")
result = exec_cmd(ssh, "ls -la /opt/mc/.sync 2>&1")
print(result)

# Try to read sync-loop.sh indirectly
print("\n[*] Checking sync-loop process...")
result = exec_cmd(ssh, "cat /proc/16/cmdline 2>/dev/null | tr '\\0' ' '")
print(result)

# Search all readable files
print("\n[*] Searching all readable content...")
result = exec_cmd(ssh, "grep -r 'TDHT{' /opt /home /tmp 2>/dev/null | head -5")
if 'TDHT{' in result:
    print(f"[FLAG FOUND] {result}")

print("\n[*] Checking if we can write to trigger sync...")
result = exec_cmd(ssh, "echo 'test' > /opt/mc/config/test.txt 2>&1; cat /opt/mc/config/test.txt 2>/dev/null")
print(result)

print("\n[*] Checking environment for clues...")
result = exec_cmd(ssh, "env | grep -i flag")
print(result)

print("\n[*] Checking /proc/1/environ...")
result = exec_cmd(ssh, "cat /proc/1/environ 2>/dev/null | tr '\\0' '\\n' | grep -i flag")
print(result)

# Try common Minecraft server locations
print("\n[*] Checking Minecraft logs...")
result = exec_cmd(ssh, "grep -i 'flag\\|TDHT' /opt/mc/logs/latest.log 2>/dev/null | head -5")
if 'TDHT{' in result or 'flag' in result.lower():
    print(result)

ssh.close()
print("\n[!] Script complete - check output above for flag")
