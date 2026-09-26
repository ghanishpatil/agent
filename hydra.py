import socket, time, re, hashlib

def talk(host, port, payload):
    s = socket.socket()
    s.connect((host, port))
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
    return buf.decode(errors='replace'), resp.decode(errors='replace')

HOST, PORT = 'lab.hexnova.space', 30982

# First see the prompt
prompt, _ = talk(HOST, PORT, '')
print('PROMPT:', prompt)
