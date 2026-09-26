import socket, ssl, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

raw = socket.create_connection(('impossible-45cf236ff719.chall.nnsc.tf', 1337), timeout=15)
s = ctx.wrap_socket(raw, server_hostname='impossible-45cf236ff719.chall.nnsc.tf')
s.settimeout(6)
buf = b''
try:
    while True:
        d = s.recv(4096)
        if not d: break
        buf += d
        if b'>' in d or b':' in d: break
except: pass
print(buf.decode(errors='replace'))
s.close()
