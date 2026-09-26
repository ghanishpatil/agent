#!/usr/bin/env python3
import struct, hashlib, base64, itertools
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
core=open(CORE,'rb').read()
def core_va(va,ln):
    ph=struct.unpack_from("<Q",core,32)[0]; n=struct.unpack_from("<H",core,56)[0]; ent=struct.unpack_from("<H",core,54)[0]
    for i in range(n):
        o=ph+i*ent; t=struct.unpack_from("<I",core,o)[0]
        off,v,pa,fsz=struct.unpack_from("<QQQQ",core,o+8)
        if t==1 and v<=va<v+fsz: return core[off+(va-v):off+(va-v)+ln]
    return None
S=core_va(0x3767ad0,0xac)
ctx=b"atlas/session/v3"
def sha(a1,a2,c): return hashlib.sha256(a1+a2+c.to_bytes(8,'little')+ctx).digest()
def checks(name,b):
    outs=[]
    reps=[("ascii",b), ("hex",b.hex().encode()), ("b64",base64.b64encode(b)), ("b64url",base64.urlsafe_b64encode(b))]
    for enc,val in reps:
        try: sval=val.decode('latin1')
        except: continue
        if 'flag{' in sval.lower() or 'flag' in sval.lower():
            outs.append((name,enc,sval))
    return outs
# build many candidate authenticated results
sid=S[0x10:0x20]
A_opts={"S10_28":S[0x10:0x28],"S20_38":S[0x20:0x38],"S34_4c":S[0x34:0x4c],"zeros":b"\x00"*24,"S00_18":S[0x00:0x18]}
B_opts={"sid":sid,"S28_38":S[0x28:0x38],"S20_30":S[0x20:0x30],"zeros16":b"\x00"*16}
found=[]
for (an,A),(bn,B),c in itertools.product(A_opts.items(),B_opts.items(),[0,1,2,3,6,0x73]):
    d=sha(A,B,c)
    r=checks(f"sha({an},{bn},{c})",d)
    found+=r
# also try raw material values and struct fields directly
for name,off,ln in [("material",0x34,8),("final",0x3c,8),("crc",0xa4,4),("sid",0x10,16),("Sfull",0,0xac)]:
    b=S[off:off+ln]
    found+=checks(name,b)
    # xorshift keystream from material as flag-length, xor with sid/ctx
if found:
    print("FLAG-LIKE FOUND:")
    for f in found: print("  ",f)
else:
    print("No flag{ in any candidate authenticated result / encoding.")
# print the primary authenticated result candidate
print("\nPrimary authenticated result sha(S[0x10:0x28] || sid || 2 || ctx):")
d=sha(S[0x10:0x28],sid,2)
print("  hex:",d.hex())
print("  b64:",base64.b64encode(d).decode())
