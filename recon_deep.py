import paramiko
import sys

def run_commands(host, port, username, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=port, username=username, password=password, timeout=15)
        print(f"[+] Connected to {host}:{port} as {username}")
        for cmd in commands:
            print(f"\n{'='*60}")
            print(f"[CMD] {cmd}")
            print('='*60)
            try:
                stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
                out = stdout.read().decode('utf-8', errors='replace')
                err = stderr.read().decode('utf-8', errors='replace')
                if out: print(out)
                if err: print(f"[STDERR] {err}")
            except Exception as e:
                print(f"[ERROR] {e}")
    except Exception as e:
        print(f"[-] Connection Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    host = 'instance.ctf.tdho.st'
    port = 32879
    username = 'player'
    password = 'reyalp'
    
    commands = [
        # Read the server properties
        'cat /opt/mc/server.properties',
        # Read sync-request.conf
        'cat /opt/mc/config/sync-request.conf',
        # Read entrypoint.sh
        'cat /entrypoint.sh 2>/dev/null',
        # Read the log - look for ghcr.io references or image names
        'grep -i "ghcr\|image\|docker\|container\|registry\|tdho\|flag\|secret" /opt/mc/logs/latest.log 2>/dev/null',
        # Network scan using Python3
        '''python3 -c "
import socket
for i in range(1, 11):
    ip = f'172.27.0.{i}'
    for port in [22, 25565, 25575, 80, 8080, 8443]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((ip, port))
        if result == 0:
            print(f'{ip}:{port} OPEN')
        s.close()
"''',
        # Look at the log for plugin info, server version, etc
        'head -50 /opt/mc/logs/latest.log',
        # Check the sync script - we know it's root-only but try anyway
        'cat /opt/mc/scripts/sync-loop.sh 2>&1',
        # Check if we can sudo
        'sudo -l 2>&1',
        # Check for any cron jobs
        'crontab -l 2>/dev/null; cat /etc/crontab 2>/dev/null; ls -la /etc/cron* 2>/dev/null',
        # Check which processes are running from root
        'ps aux | grep root',
        # Try to read /opt/mc/.sync with different methods
        'find /opt/mc/.sync -maxdepth 1 2>&1',
        # Check for any interesting files in /tmp or elsewhere
        'ls -la /tmp/ 2>/dev/null',
        # Check for .dockerenv
        'ls -la /.dockerenv 2>/dev/null',
        # Look for Dockerfile in the image
        'find / -name "Dockerfile" 2>/dev/null',
        # Check for any config mentioning another server
        'grep -r "172.27" /opt/mc/ 2>/dev/null',
    ]
    
    run_commands(host, port, username, password, commands)
