#!/usr/bin/env python3
import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("instance.ctf.tdho.st", port=32879, username="player", password="reyalp", timeout=15)

def e(c):
    stdin, stdout, stderr = ssh.exec_command(c, timeout=10)
    time.sleep(1.5)
    return stdout.read().decode('utf-8', errors='ignore')

# Check the management server secret
print("[*] Checking server.properties secret...")
result = e("grep -E 'management-server|secret|password' /opt/mc/server.properties")
print(result)

# The flag might be in the actual running game server or accessed via management API
print("\n[*] Checking if management server is running...")
result = e("netstat -tuln 2>/dev/null || ss -tuln 2>/dev/null || cat /proc/net/tcp")
print(result[:500])

# Check if we can access localhost services
print("\n[*] Testing localhost access...")
for port in [8080, 9000, 25565, 25575]:
    result = e(f"timeout 2 bash -c 'echo test 2>/dev/null >/dev/tcp/127.0.0.1/{port}' && echo 'Port {port} OPEN'")
    if 'OPEN' in result:
        print(result)

# Check the `.sync` volume ownership - maybe flag is there but we need root
print("\n[*] Checking .sync volume details...")
result = e("stat /opt/mc/.sync; ls -la /opt/mc/")
print(result)

# Maybe flag is in a file we haven't checked
print("\n[*] Deep search for TDHT flag pattern...")
result = e("find /opt /home -type f -readable 2>/dev/null | xargs grep -l 'TDHT{' 2>/dev/null | head -5")
print(result)

ssh.close()
print("\n[!] If no flag found, the challenge requires escaping to the host system")
