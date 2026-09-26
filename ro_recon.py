from pwn import *
context.log_level="info"
io=remote("chal.secso.cc",4000)
# name length
io.recvuntil(b"how long would you like your name to be?")
io.sendline(b"20")
# capture through first snapshot up to [addr]>
data=io.recvuntil(b"[addr]> ", timeout=15)
print("==== initial (incl first SNAPSHOT) ====")
print(data.decode(errors="replace"))
# probe: send an address of 0 (<= &wager) then value, to trigger the write + 2nd snapshot
io.sendline(b"0")
d2=io.recvuntil(b"[value]> ", timeout=10)
print("==== after addr=0 ====")
print(d2.decode(errors="replace"))
io.sendline(b"65")   # value 'A'
d3=io.recvuntil(b"wager> ", timeout=10)
print("==== after value (incl 2nd SNAPSHOT) ====")
print(d3.decode(errors="replace"))
io.close()
