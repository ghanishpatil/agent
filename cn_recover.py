import json, base64, hashlib
from math import gcd
toks=json.load(open('cn_tokens.json'))
def b64d(x): return base64.urlsafe_b64decode(x+'='*(-len(x)%4))
e=65537
k=256
# DigestInfo prefix for SHA-256
PREFIX=bytes.fromhex('3031300d060960864801650304020105000420')
def emsa(msg):
    h=hashlib.sha256(msg).digest()
    T=PREFIX+h
    ps=b'\xff'*(k-3-len(T))
    EM=b'\x00\x01'+ps+b'\x00'+T
    return int.from_bytes(EM,'big')
def sig_int(tok):
    return int.from_bytes(b64d(tok.split('.')[2]),'big')
def signing_input(tok):
    a,b,c=tok.split('.')
    return (a+'.'+b).encode()

vals=[]
for t in toks:
    s=sig_int(t); m=emsa(signing_input(t))
    vals.append(pow(s,e)-m)

# gcd of all
g=vals[0]
for v in vals[1:]:
    g=gcd(g,v)
print('gcd bit length', g.bit_length())
# remove small factors
n=g
for sf in range(2,100000):
    while n%sf==0:
        n//=sf
print('after strip small factors bit length', n.bit_length())

# sanity: n should be 2048-bit. verify a signature: s^e mod n == emsa(m)?
import json as _j
ok=all(pow(sig_int(t),e,n)==emsa(signing_input(t)) for t in toks)
print('verify all sigs mod n:', ok)
json.dump({'n':n,'e':e}, open('cn_pubkey.json','w'))
print('n =', hex(n)[:80],'...')
