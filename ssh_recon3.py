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
        # Read the config files
        'cat /opt/mc/server.properties',
        'cat /opt/mc/config/sync-request.conf',
        'cat /opt/mc/config/test.conf',
        # Read the log file
        'head -100 /opt/mc/logs/latest.log',
        'tail -100 /opt/mc/logs/latest.log',
        # Check which tools available  
        'which curl 2>/dev/null; which wget 2>/dev/null; which nc 2>/dev/null; which ncat 2>/dev/null; which python3 2>/dev/null; which python 2>/dev/null; which perl 2>/dev/null; which nmap 2>/dev/null; which bash 2>/dev/null; which socat 2>/dev/null',
        # Explore the .sync mount - this is interesting, it's from the host
        'ls -la /opt/mc/.sync/ 2>&1',
        # Try to read the sync script 
        'cat /opt/mc/scripts/sync-loop.sh 2>&1',
        # Check ifconfig output
        'ifconfig 2>/dev/null || cat /proc/net/if_inet6 2>/dev/null; cat /proc/net/fib_trie 2>/dev/null | head -30',
        # Check if we can write to config dir
        'touch /opt/mc/config/test_write 2>&1 && echo "WRITABLE" && rm /opt/mc/config/test_write',
        # Check /home/player 
        'ls -la /home/player/ 2>/dev/null',
        # Check if we can access host filesystem through any mount
        'findmnt 2>/dev/null',
        # Container image info
        'cat /etc/image-id 2>/dev/null; cat /etc/machine-id 2>/dev/null',
        # Check for RCON or game server ports
        'cat /proc/net/tcp 2>/dev/null',
        # Scan the gateway/neighbor - 172.27.0.1 is the gateway, our IP is 172.27.0.3
        'bash -c "for i in 1 2 3 4 5; do echo -n \"172.27.0.$i: \"; (echo > /dev/tcp/172.27.0.$i/25565) 2>/dev/null && echo OPEN || echo closed; done"',
        # Check for minecraft RCON port
        'bash -c "for i in 1 2 3 4 5; do echo -n \"172.27.0.$i:25575 \"; (echo > /dev/tcp/172.27.0.$i/25575) 2>/dev/null && echo OPEN || echo closed; done"',
        # Check SSH port on other containers
        'bash -c "for i in 1 2 3 4 5; do echo -n \"172.27.0.$i:22 \"; (echo > /dev/tcp/172.27.0.$i/22) 2>/dev/null && echo OPEN || echo closed; done"',
    ]
    
    run_commands(host, port, username, password, commands)
