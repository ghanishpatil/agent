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
        'id; whoami; hostname',
        'cat /opt/mc/server.properties',
        'cat /opt/mc/config/sync-request.conf',
        'cat /opt/mc/config/test.conf',
        'cat /opt/mc/scripts/sync-loop.sh 2>&1',
        'head -200 /opt/mc/logs/latest.log',
        'tail -50 /opt/mc/logs/latest.log',
        'ls -laR /opt/mc/',
        'cat /etc/hosts',
        'cat /proc/net/arp',
        'ifconfig 2>/dev/null; cat /proc/net/tcp',
        # Check what tools we have
        'which curl wget nc ncat python3 python perl bash socat ssh nmap 2>/dev/null; ls /usr/bin/ | head -50',
        # Check capabilities
        'cat /proc/self/status | grep -i cap',
        # Check for SUID binaries
        'find / -perm -4000 -type f 2>/dev/null',
        # Try to read .sync dir
        'ls -la /opt/mc/.sync/ 2>&1',
        # Mount info
        'mount | grep sync',
        # Check writable dirs
        'touch /opt/mc/config/test_write 2>&1 && echo "config WRITABLE" && rm /opt/mc/config/test_write',
        'touch /opt/mc/plugins/test_write 2>&1 && echo "plugins WRITABLE" && rm /opt/mc/plugins/test_write',
        # Docker image labels/info
        'cat /etc/image-id 2>/dev/null; cat /etc/machine-id 2>/dev/null; cat /opt/mc/Dockerfile 2>/dev/null',
        # Scan neighbor IPs for minecraft port 25565
        'bash -c "for i in 1 2 3 4 5 6 7 8 9 10; do echo -n \"172.27.0.$i:25565 \"; timeout 1 bash -c \"echo > /dev/tcp/172.27.0.$i/25565\" 2>/dev/null && echo OPEN || echo closed; done"',
        # Scan for SSH on neighbors
        'bash -c "for i in 1 2 3 4 5 6 7 8 9 10; do echo -n \"172.27.0.$i:22 \"; timeout 1 bash -c \"echo > /dev/tcp/172.27.0.$i/22\" 2>/dev/null && echo OPEN || echo closed; done"',
        # Scan for RCON on neighbors 
        'bash -c "for i in 1 2 3 4 5 6 7 8 9 10; do echo -n \"172.27.0.$i:25575 \"; timeout 1 bash -c \"echo > /dev/tcp/172.27.0.$i/25575\" 2>/dev/null && echo OPEN || echo closed; done"',
        # Check home directory and bash history
        'ls -la /home/player/ 2>/dev/null; cat /home/player/.bash_history 2>/dev/null',
        # Check env vars for clues
        'env',
        # Check for any SSH keys
        'find / -name "id_rsa" -o -name "id_ed25519" -o -name "authorized_keys" 2>/dev/null',
        # Check Dockerfile layers
        'cat /proc/1/cmdline 2>/dev/null | tr "\\0" " "; echo',
    ]
    
    run_commands(host, port, username, password, commands)
