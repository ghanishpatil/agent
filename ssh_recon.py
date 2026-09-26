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
        'id; whoami; hostname',
        'ls -la /',
        'ls -la /home/ 2>/dev/null',
        'ls -la /home/player/ 2>/dev/null',
        'cat /etc/os-release 2>/dev/null',
        'env',
        'cat /proc/1/cgroup 2>/dev/null',
        'ip addr 2>/dev/null || ifconfig 2>/dev/null',
        'ps aux 2>/dev/null || ps -ef 2>/dev/null',
        'find / -name "flag*" -type f 2>/dev/null',
        'find / -name "*.jar" -type f 2>/dev/null',
        'ls -la /opt/ 2>/dev/null',
        'ls -la /var/ 2>/dev/null',
        'cat /etc/passwd',
        'ls -la /root/ 2>/dev/null',
        'which docker 2>/dev/null; which kubectl 2>/dev/null; which crictl 2>/dev/null',
        'cat /proc/self/status | head -20',
        'mount 2>/dev/null',
        'cat /etc/hosts',
        'arp -a 2>/dev/null || ip neigh 2>/dev/null',
        'netstat -tlnp 2>/dev/null || ss -tlnp 2>/dev/null',
    ]
    
    run_commands(host, port, username, password, commands)
