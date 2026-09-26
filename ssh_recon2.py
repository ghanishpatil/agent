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
            stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
            out = stdout.read().decode('utf-8', errors='replace')
            err = stderr.read().decode('utf-8', errors='replace')
            if out:
                print(out)
            if err:
                print(f"[STDERR] {err}")
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    host = 'instance.ctf.tdho.st'
    port = 32867
    username = 'player'
    password = 'reyalp'
    
    commands = [
        # More detailed recon - explore the mc directory (minecraft?)
        'ls -laR /opt/mc/',
        'cat /opt/mc/.sync 2>/dev/null; ls -la /opt/mc/.sync/ 2>/dev/null',
        'find /opt/mc/ -type f 2>/dev/null',
        # Check for container escape vectors
        'cat /proc/1/cgroup',
        'ls -la /proc/1/root/ 2>/dev/null',
        'capsh --print 2>/dev/null || cat /proc/self/status | grep -i cap',
        # Check docker socket or other escape paths
        'ls -la /var/run/docker.sock 2>/dev/null',
        'ls -la /run/containerd/ 2>/dev/null',
        # Network scan - discover other containers
        'ip addr',
        'ip route',
        'cat /proc/net/arp',
        # Check for writable mount or host filesystem access
        'ls -la /opt/mc/.sync/',
        'df -h',
        # Check for useful tools
        'which curl wget nc ncat nmap python python3 perl 2>/dev/null',
        # Home dir exploration 
        'ls -la /home/player/',
        'cat /home/player/.bash_history 2>/dev/null',
        # Check Dockerfile/image info
        'cat /Dockerfile 2>/dev/null',
        'cat /.dockerenv 2>/dev/null; ls -la /.dockerenv 2>/dev/null',
    ]
    
    run_commands(host, port, username, password, commands)
