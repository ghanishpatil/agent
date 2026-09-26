from pwn import *
context.log_level='info'
io=remote('chal.secso.cc',4001)
# read everything up to first snapshot output
import time
time.sleep(1)
data=io.recv(timeout=3)
print("==== initial recv ====")
print(data.decode(errors='replace'))
# send name length
io.sendline(b'20')
time.sleep(1)
data=io.recv(timeout=3)
print("==== after name length (should show snapshot 1) ====")
print(data.decode(errors='replace'))
io.close()
